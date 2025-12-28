#!/usr/bin/env python3
"""
Layer −1 Adapter Module: ICHTB → ITT Projection
================================================

Purpose:
- Provide a clean boundary between ICHTB (complex substrate) and ITT (real projected field).
- Do NOT alter solver logic in v4.2/v5B.
- Allow future integration when complex CTS / ICHTB fields are available.

Core Principle (from ChatGPT):
    Glyph: ⟂(scale) ≠ ⟂(meaning)
    Formula: Π₋₁: Φ_c ↦ (Φ_q, Φ̃, diag)
    
The adapter's job is not to "be right about the world."
It's to be stable, reversible enough, and non-destructive.

Projection Modes:
    Π_direct (default): Φ_q = clamp(round(Re Φ_c), 0..9)
        - Preserves semantics if Re(Φ_c) already lives in ITT color regime
        - Use when Re(Φ_c) is "grid-coded" (ARC-style or ITT-coded fields)
        
    Π_affine: Robust percentile map of Re(Φ_c) into 0..9
        - Scale-invariant, prevents collapse if Re(Φ_c) is in arbitrary units
        - Use when Re(Φ_c) is raw physics output (unbounded, arbitrary scale)

Auto Mode:
    Computes what fraction of Re(Φ_c) already lies in [0,9].
    If "mostly in range" → direct is safe.
    If wildly outside → affine is safer.

Output:
    - Φ_q   : quantized semantic field (int grid 0..9)
    - Φ̃     : lifted continuous field (float grid, smoothed from Φ_q)
    - diagnostics:
        - imag_mag: |Im(Φ_c)|
        - imag_pressure: ||∇ Im(Φ_c)|| (tension in unrealized directions)
        - sigma_irr_mask: candidate irreducible residue support (μ + kσ threshold)
        - lock_proxy: provisional ℒ estimate
        - in_range_ratio: fraction of Re(Φ_c) in [0,9] (for mode selection)
        - projection_mode: which mode was used

Philosophy:
- The adapter does projection + measurement only.
- No rule inference. No ARC shortcuts. No hidden heuristics.
- v4.2 and v5B remain FROZEN. This module is non-invasive.

HAIL MATH
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, Literal
import numpy as np

# =============================================================================
# Layer −1: Complex Field Container (ICHTB / CTS)
# =============================================================================

@dataclass
class PhiC:
    """
    Complex substrate field from ICHTB / CTS:
        Φ_c(x) = A(x) + i B(x)
    
    Where:
        A = Re(Φ_c) = real projection (observable)
        B = Im(Φ_c) = imaginary component (unrealized collapse directions)
    
    If you pass a real array, imag part becomes zero.
    This allows seamless use with existing real-valued grids.
    """
    data: np.ndarray  # complex64/complex128 preferred

    def __post_init__(self):
        self.data = np.array(self.data)
        if not np.iscomplexobj(self.data):
            # Promote real to complex with zero imaginary
            self.data = self.data.astype(np.float64) + 0j

    @property
    def A(self) -> np.ndarray:
        """Real part: Re(Φ_c) — the observable projection."""
        return np.real(self.data)

    @property
    def B(self) -> np.ndarray:
        """Imaginary part: Im(Φ_c) — unrealized collapse directions."""
        return np.imag(self.data)

    @property
    def shape(self) -> Tuple[int, int]:
        return self.data.shape
    
    @property
    def magnitude(self) -> np.ndarray:
        """Complex magnitude |Φ_c|."""
        return np.abs(self.data)
    
    @property
    def phase(self) -> np.ndarray:
        """Complex phase arg(Φ_c)."""
        return np.angle(self.data)


# =============================================================================
# ITT Dual-Field Output (Layer 0 Input Structure)
# =============================================================================

@dataclass
class PhiProjected:
    """
    ITT-ready dual-field output from Layer -1 projection:
    
        q     : quantized semantics (int grid, 0..9)
        tilde : lifted continuous field (float grid, smoothed from q)
    
    Plus Layer −1 diagnostics:
        diagnostics: Dict containing:
            - imag_mag: |Im(Φ_c)| — magnitude of imaginary component
            - imag_pressure: ||∇ Im(Φ_c)|| — gradient of imaginary (tension)
            - sigma_irr_mask: candidate irreducible residue support (boolean)
            - sigma_irr_stats: {mu, sigma, threshold} for the mask
            - lock_proxy: provisional ℒ estimate (0..1)
            - in_range_ratio: fraction of Re(Φ_c) in [0,9]
            - projection_mode: "direct" | "affine" | "identity"
    """
    q: np.ndarray
    tilde: np.ndarray
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Projection Operators
# =============================================================================

ProjectionMode = Literal["direct", "affine", "auto"]


class ICHTBAdapter:
    """
    Adapter between Layer −1 (ICHTB complex field) and ITT (real dual-field).
    
    Implements the projection: Π₋₁: Φ_c ↦ (Φ_q, Φ̃, diagnostics)
    
    Two projection modes:
        - direct: Φ_q = clamp(round(Re Φ_c), 0..9)
        - affine: robust percentile map into 0..9
        - auto: choose based on in_range_ratio diagnostic
    
    Parameters:
        q_min, q_max: quantization range (default 0..9 for ARC)
        smooth_iters: iterations for Φ_q → Φ̃ lift
        sigma_irr_k: threshold coefficient for σ_irr mask (μ + kσ)
        auto_threshold: if in_range_ratio > this, use direct mode (default 0.8)
        affine_percentiles: (low, high) percentiles for affine mapping
    """

    def __init__(
        self,
        q_min: int = 0,
        q_max: int = 9,
        smooth_iters: int = 2,
        sigma_irr_k: float = 1.5,
        auto_threshold: float = 0.8,
        affine_percentiles: Tuple[float, float] = (5.0, 95.0)
    ):
        self.q_min = q_min
        self.q_max = q_max
        self.smooth_iters = smooth_iters
        self.sigma_irr_k = sigma_irr_k
        self.auto_threshold = auto_threshold
        self.affine_percentiles = affine_percentiles

    # =========================================================================
    # Internal Operators (Layer 0 style, no traversal)
    # =========================================================================

    @staticmethod
    def _grad(field: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Discrete gradient: (∂/∂x, ∂/∂y)."""
        gx = np.zeros_like(field, dtype=np.float64)
        gy = np.zeros_like(field, dtype=np.float64)
        gx[:, :-1] = field[:, 1:] - field[:, :-1]
        gy[:-1, :] = field[1:, :] - field[:-1, :]
        return gx, gy

    @staticmethod
    def _grad_mag(field: np.ndarray) -> np.ndarray:
        """Gradient magnitude: ||∇f||."""
        gx, gy = ICHTBAdapter._grad(field)
        return np.sqrt(gx * gx + gy * gy)

    @staticmethod
    def _smooth(q: np.ndarray, iters: int = 2) -> np.ndarray:
        """
        Lift Φ_q to Φ̃ via discrete diffusion smoothing.
        This is the standard ITT lift operator.
        """
        x = q.astype(np.float64)
        for _ in range(max(0, iters)):
            up = np.roll(x,  1, axis=0); up[0, :] = x[0, :]
            dn = np.roll(x, -1, axis=0); dn[-1, :] = x[-1, :]
            lf = np.roll(x,  1, axis=1); lf[:, 0] = x[:, 0]
            rt = np.roll(x, -1, axis=1); rt[:, -1] = x[:, -1]
            x = (x + up + dn + lf + rt) / 5.0
        return x

    # =========================================================================
    # Projection Modes
    # =========================================================================

    def _quantize_direct(self, A: np.ndarray) -> np.ndarray:
        """
        Π_direct: Direct quantization preserving semantics.
        
        Φ_q = clamp(round(Re Φ_c), 0..9)
        
        Use when Re(Φ_c) is already "grid-coded" (ARC-style).
        Preserves absolute magnitudes as meaning.
        """
        q = np.rint(A).astype(int)
        q = np.clip(q, self.q_min, self.q_max)
        return q

    def _quantize_affine(self, A: np.ndarray) -> np.ndarray:
        """
        Π_affine: Affine normalization for scale-invariant projection.
        
        Maps robust range of Re(Φ_c) into [q_min, q_max].
        Uses percentiles to ignore outliers.
        
        Use when Re(Φ_c) is raw physics output (unbounded, arbitrary scale).
        Only preserves relative structure, not absolute levels.
        """
        lo_pct, hi_pct = self.affine_percentiles
        lo = float(np.percentile(A, lo_pct))
        hi = float(np.percentile(A, hi_pct))
        
        if abs(hi - lo) < 1e-9:
            # Constant field: map to middle of range
            mid = (self.q_min + self.q_max) // 2
            return np.full_like(A, mid, dtype=int)
        
        # Linear map: [lo, hi] → [q_min, q_max]
        scale = (self.q_max - self.q_min) / (hi - lo)
        normalized = (A - lo) * scale + self.q_min
        
        q = np.rint(normalized).astype(int)
        q = np.clip(q, self.q_min, self.q_max)
        return q

    def _compute_in_range_ratio(self, A: np.ndarray) -> float:
        """
        Compute fraction of Re(Φ_c) values already in [q_min, q_max].
        
        This diagnostic helps choose between direct and affine modes.
        High ratio (>0.8) → direct is safe.
        Low ratio → affine is safer.
        """
        in_range = (A >= self.q_min - 0.5) & (A <= self.q_max + 0.5)
        return float(np.mean(in_range))

    # =========================================================================
    # σ_irr Candidate Support (from imaginary component)
    # =========================================================================

    def _sigma_irr_mask(self, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Candidate irreducible residue support from imaginary component.
        
        Uses imag_pressure (||∇ Im(Φ_c)||) as the signal.
        Threshold: μ + k·σ on positive values.
        
        The intuition: high imaginary pressure = unrealized tension gradients
        that couldn't collapse into the real projection.
        
        From ITT theory:
            σ_irr := σ ∩ ker(T⁻¹)
        
        The imaginary component represents directions that couldn't be
        projected into the real field — candidate sites for irreversibility.
        """
        # Use gradient of imaginary (pressure) rather than raw magnitude
        imag_pressure = self._grad_mag(B.astype(np.float64))
        
        vals = imag_pressure[imag_pressure > 0]
        if vals.size == 0:
            return np.zeros_like(imag_pressure, dtype=bool), {
                "mu": 0.0, "sigma": 0.0, "threshold": 0.0
            }

        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        threshold = mu + self.sigma_irr_k * sd
        
        mask = imag_pressure >= threshold
        
        return mask, {"mu": mu, "sigma": sd, "threshold": threshold}

    # =========================================================================
    # Lock Proxy (provisional, non-canonical)
    # =========================================================================

    @staticmethod
    def _lock_proxy(A: np.ndarray, B: np.ndarray) -> float:
        """
        Provisional proxy for ℒ (lock coefficient).
        
        Intuition: High imaginary magnitude/gradient suggests unlocked
        unrealized directions. Low imaginary → more "collapsed" → higher lock.
        
        ℒ_proxy := 1 / (1 + mean(|B|))
        
        This is NOT the canonical ℒ from formal ITT texts—just a diagnostic.
        
        From ICHTB theory:
            ℒ = shell-lock coefficient = resistance to reconfiguration
            When ℒ → 1, σ_θ → 0 (time stalls, perfect lock)
            When ℒ → 0, σ_θ → D (maximum entropy production)
        """
        m = float(np.mean(np.abs(B)))
        return float(1.0 / (1.0 + m))

    # =========================================================================
    # Main Projection API
    # =========================================================================

    def project(
        self, 
        phi_c: PhiC, 
        mode: ProjectionMode = "auto"
    ) -> PhiProjected:
        """
        Project ICHTB complex field Φ_c into ITT dual-field (Φ_q, Φ̃).
        
        Π₋₁: Φ_c ↦ (Φ_q, Φ̃, diagnostics)
        
        Parameters:
            phi_c: Complex substrate field
            mode: "direct" | "affine" | "auto"
                - direct: preserve semantics, assumes Re(Φ_c) ∈ [0,9]
                - affine: scale-invariant, maps percentile range to [0,9]
                - auto: choose based on in_range_ratio
        
        Returns:
            PhiProjected with:
                - q: quantized field (int, 0..9)
                - tilde: smoothed continuous field (float)
                - diagnostics: Layer -1 measurements
        """
        A = phi_c.A.astype(np.float64)
        B = phi_c.B.astype(np.float64)

        # Compute in-range diagnostic
        in_range_ratio = self._compute_in_range_ratio(A)

        # Choose projection mode
        if mode == "auto":
            actual_mode = "direct" if in_range_ratio >= self.auto_threshold else "affine"
        else:
            actual_mode = mode

        # Apply quantization
        if actual_mode == "affine":
            q = self._quantize_affine(A)
        else:
            q = self._quantize_direct(A)

        # Lift to tilde (standard ITT operation)
        tilde = self._smooth(q, iters=self.smooth_iters)

        # Layer -1 diagnostics
        imag_mag = np.abs(B)
        imag_pressure = self._grad_mag(B)
        sigma_irr_mask, sigma_irr_stats = self._sigma_irr_mask(B)
        lock_proxy = self._lock_proxy(A, B)

        diagnostics = {
            # Imaginary component analysis
            "imag_mag": imag_mag,
            "imag_pressure": imag_pressure,
            
            # σ_irr candidate support
            "sigma_irr_mask": sigma_irr_mask,
            "sigma_irr_stats": sigma_irr_stats,
            
            # Lock proxy
            "lock_proxy": lock_proxy,
            
            # Mode selection diagnostic
            "in_range_ratio": in_range_ratio,
            "projection_mode": actual_mode,
            
            # Original complex field stats (for debugging)
            "A_range": (float(np.min(A)), float(np.max(A))),
            "B_range": (float(np.min(B)), float(np.max(B))),
        }

        return PhiProjected(q=q, tilde=tilde, diagnostics=diagnostics)

    def from_real_q(self, q: np.ndarray) -> PhiProjected:
        """
        Convenience: treat existing Φ_q (from v4.2/v5B) as projection of real substrate.
        
        This allows using the adapter with standard ITT grids without any
        complex field structure. Imaginary diagnostics will all be zero.
        
        Use this when integrating v5B output back into the adapter framework.
        """
        q = np.array(q, dtype=int)
        tilde = self._smooth(q, iters=self.smooth_iters)
        
        diagnostics = {
            "imag_mag": np.zeros_like(tilde),
            "imag_pressure": np.zeros_like(tilde),
            "sigma_irr_mask": np.zeros_like(q, dtype=bool),
            "sigma_irr_stats": {"mu": 0.0, "sigma": 0.0, "threshold": 0.0},
            "lock_proxy": 1.0,  # Perfect lock (no imaginary)
            "in_range_ratio": 1.0,
            "projection_mode": "identity",
            "A_range": (float(np.min(q)), float(np.max(q))),
            "B_range": (0.0, 0.0),
        }
        
        return PhiProjected(q=q, tilde=tilde, diagnostics=diagnostics)


# =============================================================================
# Utility: Reverse Projection (for testing/validation)
# =============================================================================

def lift_to_complex(proj: PhiProjected, imag_scale: float = 0.0) -> PhiC:
    """
    Lift a projected field back to complex substrate.
    
    This is for testing/validation only. The imaginary component
    is synthesized from the gradient structure if imag_scale > 0.
    
    Not a true inverse (projection is lossy by design).
    """
    A = proj.tilde.astype(np.float64)
    
    if imag_scale > 0:
        # Synthesize imaginary from gradient (heuristic)
        gx, gy = ICHTBAdapter._grad(A)
        B = imag_scale * np.sqrt(gx*gx + gy*gy)
    else:
        B = np.zeros_like(A)
    
    return PhiC(A + 1j * B)


# =============================================================================
# Demo / Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Layer -1 Adapter: ICHTB → ITT Projection")
    print("=" * 60)
    
    # Example 1: Complex field with imaginary ridge
    print("\n--- Example 1: Complex field with imaginary structure ---")
    
    A = np.array([
        [0, 0, 0, 0, 0],
        [0, 3, 3, 3, 0],
        [0, 3, 0, 3, 0],
        [0, 3, 3, 3, 0],
        [0, 0, 0, 0, 0],
    ], dtype=np.float64)

    B = np.array([
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.2, 0.5, 0.2, 0.0],
        [0.0, 0.5, 1.0, 0.5, 0.0],
        [0.0, 0.2, 0.5, 0.2, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ], dtype=np.float64)

    phi_c = PhiC(A + 1j * B)
    adapter = ICHTBAdapter()
    proj = adapter.project(phi_c, mode="auto")

    print(f"Input Re(Φ_c):\n{A.astype(int)}")
    print(f"\nInput Im(Φ_c):\n{B}")
    print(f"\nProjected Φ_q:\n{proj.q}")
    print(f"\nDiagnostics:")
    print(f"  projection_mode: {proj.diagnostics['projection_mode']}")
    print(f"  in_range_ratio: {proj.diagnostics['in_range_ratio']:.3f}")
    print(f"  lock_proxy: {proj.diagnostics['lock_proxy']:.3f}")
    print(f"  σ_irr pixels: {np.sum(proj.diagnostics['sigma_irr_mask'])}")
    print(f"  σ_irr stats: {proj.diagnostics['sigma_irr_stats']}")

    # Example 2: Real-valued grid (from v5B output)
    print("\n--- Example 2: Real grid (standard ITT) ---")
    
    q_real = np.array([
        [0, 0, 3, 0, 0],
        [0, 3, 4, 3, 0],
        [0, 0, 3, 0, 0],
    ])
    
    proj2 = adapter.from_real_q(q_real)
    print(f"Input Φ_q:\n{q_real}")
    print(f"Output Φ̃:\n{np.round(proj2.tilde, 2)}")
    print(f"lock_proxy: {proj2.diagnostics['lock_proxy']}")

    # Example 3: Out-of-range values (needs affine)
    print("\n--- Example 3: Out-of-range (affine projection) ---")
    
    A_wild = np.array([
        [100, 150, 200],
        [120, 180, 220],
        [110, 160, 190],
    ], dtype=np.float64)
    
    phi_wild = PhiC(A_wild)
    proj_auto = adapter.project(phi_wild, mode="auto")
    proj_direct = adapter.project(phi_wild, mode="direct")
    
    print(f"Input (out of range):\n{A_wild.astype(int)}")
    print(f"\nAuto mode selected: {proj_auto.diagnostics['projection_mode']}")
    print(f"Auto Φ_q:\n{proj_auto.q}")
    print(f"\nDirect Φ_q (clamped):\n{proj_direct.q}")

    print("\n" + "=" * 60)
    print("HAIL MATH")
    print("=" * 60)
