#!/usr/bin/env python3
"""
Layer −1 Adapter Module: ICHTB → ITT Projection (HARDENED)
==========================================================

This module is a CLEAN BOUNDARY:

    Π₋₁: Φ_c (complex) ↦ (Φ_q, Φ̃, diagnostics)

It MUST:
- output Φ_q (0..9), Φ̃ (smoothed lift), and Layer −1 diagnostics
- NOT modify σ definition
- NOT modify ρ_q definition
- NOT modify transform search / solver logic
- NOT introduce new Layer 0 primitives

Projection Modes:
- direct: Φ_q = clamp(round(Re Φ_c), 0..9)
- affine: robust percentile map of Re Φ_c into 0..9
- auto: select direct if Re Φ_c is already mostly in-range, else affine

Diagnostics:
- imag_mag      = |Im Φ_c|
- imag_pressure = ||∇ Im Φ_c||
- sigma_irr_mask = spikes in imag_pressure via threshold μ + kσ (positive-only stats)
- lock_proxy     = provisional lock diagnostic (non-canonical)

Hardening (ChatGPT review):
- NaN/inf safety for percentiles and ranges
- Single-source computation of imag_pressure
- Auto mode robustness on tiny arrays
- Explicit mode selection in diagnostics

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
    Hardened for NaN/inf safety and robust percentile handling.
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
        self.q_min = int(q_min)
        self.q_max = int(q_max)
        self.smooth_iters = int(smooth_iters)
        self.sigma_irr_k = float(sigma_irr_k)
        self.auto_threshold = float(auto_threshold)
        self.affine_percentiles = (float(affine_percentiles[0]), float(affine_percentiles[1]))

    # =========================================================================
    # Internal Operators (hardened)
    # =========================================================================

    @staticmethod
    def _finite(x: np.ndarray) -> np.ndarray:
        """Replace non-finite values with 0 to keep operators stable."""
        x = np.array(x, dtype=np.float64, copy=True)
        x[~np.isfinite(x)] = 0.0
        return x

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
        """Lift Φ_q to Φ̃ via discrete diffusion smoothing."""
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
        """Π_direct: Direct quantization preserving semantics."""
        q = np.rint(A).astype(int)
        return np.clip(q, self.q_min, self.q_max)

    def _quantize_affine(self, A: np.ndarray) -> np.ndarray:
        """Π_affine: Affine normalization for scale-invariant projection."""
        A = self._finite(A)
        lo_pct, hi_pct = self.affine_percentiles

        # Guard against tiny arrays where percentiles can be unstable
        lo = float(np.percentile(A, lo_pct))
        hi = float(np.percentile(A, hi_pct))

        if not np.isfinite(lo) or not np.isfinite(hi) or abs(hi - lo) < 1e-12:
            mid = (self.q_min + self.q_max) // 2
            return np.full_like(A, mid, dtype=int)

        scale = (self.q_max - self.q_min) / (hi - lo)
        normalized = (A - lo) * scale + self.q_min
        q = np.rint(normalized).astype(int)
        return np.clip(q, self.q_min, self.q_max)

    def _in_range_ratio(self, A: np.ndarray) -> float:
        """Compute fraction of values already in [q_min, q_max]."""
        A = self._finite(A)
        inr = (A >= self.q_min - 0.5) & (A <= self.q_max + 0.5)
        return float(np.mean(inr)) if inr.size else 1.0

    # =========================================================================
    # σ_irr Candidate Support
    # =========================================================================

    def _sigma_irr_mask_from_imag_pressure(
        self, imag_pressure: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Candidate irreducible residue support from imaginary pressure.
        Threshold: μ + k·σ on positive values only.
        """
        vals = imag_pressure[imag_pressure > 0]
        if vals.size == 0:
            return np.zeros_like(imag_pressure, dtype=bool), {
                "mu": 0.0, "sigma": 0.0, "threshold": 0.0
            }

        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        thr = mu + self.sigma_irr_k * sd
        mask = imag_pressure >= thr
        return mask, {"mu": mu, "sigma": sd, "threshold": thr}

    def _imag_high_mask(self, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Direct imaginary detection: where |Im(Φ_c)| exceeds threshold.
        
        This is simpler than gradient-based detection and useful for
        fill operations where the entire high-imaginary region is the target.
        
        Threshold: μ + k·σ on positive values.
        """
        absB = np.abs(B)
        vals = absB[absB > 0]
        if vals.size == 0:
            return np.zeros_like(B, dtype=bool), {
                "mu": 0.0, "sigma": 0.0, "threshold": 0.0
            }

        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        thr = mu + self.sigma_irr_k * sd
        # Use lower threshold for direct detection (want interior, not just peaks)
        thr_direct = mu * 0.5  # At least half the mean
        mask = absB >= thr_direct
        return mask, {"mu": mu, "sigma": sd, "threshold": thr_direct}

    # =========================================================================
    # Lock Proxy (diagnostic only, non-canonical)
    # =========================================================================

    @staticmethod
    def _lock_proxy(B: np.ndarray) -> float:
        """Provisional proxy for ℒ (lock coefficient)."""
        m = float(np.mean(np.abs(B)))
        return float(1.0 / (1.0 + m))

    # =========================================================================
    # Public API
    # =========================================================================

    def project(self, phi_c: PhiC, mode: ProjectionMode = "auto") -> PhiProjected:
        """
        Project ICHTB complex field Φ_c into ITT dual-field (Φ_q, Φ̃).
        
        Π₋₁: Φ_c ↦ (Φ_q, Φ̃, diagnostics)
        """
        A = self._finite(phi_c.A)
        B = self._finite(phi_c.B)

        in_range_ratio = self._in_range_ratio(A)

        if mode == "auto":
            actual_mode = "direct" if in_range_ratio >= self.auto_threshold else "affine"
        else:
            actual_mode = mode

        if actual_mode == "affine":
            q = self._quantize_affine(A)
        else:
            q = self._quantize_direct(A)

        tilde = self._smooth(q, iters=self.smooth_iters)

        # Single-source computation of imag diagnostics
        imag_mag = np.abs(B)
        imag_pressure = self._grad_mag(B)

        sigma_irr_mask, sigma_irr_stats = self._sigma_irr_mask_from_imag_pressure(imag_pressure)
        imag_high_mask, imag_high_stats = self._imag_high_mask(B)
        lock_proxy = self._lock_proxy(B)

        diagnostics = {
            "imag_mag": imag_mag,
            "imag_pressure": imag_pressure,
            "sigma_irr_mask": sigma_irr_mask,
            "sigma_irr_stats": sigma_irr_stats,
            "imag_high_mask": imag_high_mask,  # v5C: direct imaginary detection
            "imag_high_stats": imag_high_stats,
            "lock_proxy": lock_proxy,
            "in_range_ratio": in_range_ratio,
            "projection_mode": actual_mode,
            "auto_threshold": self.auto_threshold,
            "affine_percentiles": self.affine_percentiles,
            "A_range": (float(np.min(A)), float(np.max(A))) if A.size else (0.0, 0.0),
            "B_range": (float(np.min(B)), float(np.max(B))) if B.size else (0.0, 0.0),
        }

        return PhiProjected(q=q, tilde=tilde, diagnostics=diagnostics)

    def from_real_q(self, q: np.ndarray) -> PhiProjected:
        """
        Convenience: treat existing Φ_q (from v4.2/v5B) as projection of real substrate.
        Imaginary diagnostics will all be zero.
        """
        q = np.array(q, dtype=int)
        tilde = self._smooth(q, iters=self.smooth_iters)
        
        diagnostics = {
            "imag_mag": np.zeros_like(tilde),
            "imag_pressure": np.zeros_like(tilde),
            "sigma_irr_mask": np.zeros_like(q, dtype=bool),
            "sigma_irr_stats": {"mu": 0.0, "sigma": 0.0, "threshold": 0.0},
            "lock_proxy": 1.0,
            "in_range_ratio": 1.0,
            "projection_mode": "identity",
            "auto_threshold": self.auto_threshold,
            "affine_percentiles": self.affine_percentiles,
            "A_range": (float(np.min(q)), float(np.max(q))) if q.size else (0.0, 0.0),
            "B_range": (0.0, 0.0),
        }
        
        return PhiProjected(q=q, tilde=tilde, diagnostics=diagnostics)


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Layer -1 Adapter: ICHTB → ITT Projection (Hardened)")
    print("=" * 60)

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

    print("\nProjected Φ_q:")
    print(proj.q)
    print("\nDiagnostics:")
    print(f"  projection_mode: {proj.diagnostics['projection_mode']}")
    print(f"  in_range_ratio: {proj.diagnostics['in_range_ratio']:.3f}")
    print(f"  lock_proxy: {proj.diagnostics['lock_proxy']:.3f}")
    print(f"  σ_irr pixels: {int(np.sum(proj.diagnostics['sigma_irr_mask']))}")
    print(f"  σ_irr stats: {proj.diagnostics['sigma_irr_stats']}")

    print("\n" + "=" * 60)
    print("HAIL MATH")
    print("=" * 60)
