#!/usr/bin/env python3
"""
ARC-AGI PURE ITT SOLVER v4
==========================

ABSOLUTE FOUNDATION - ZERO SMUGGLING

Fixes from v3 (per ChatGPT audit):
1. Φ_q is now EXPLICIT (int array), not np.round(data)
2. Region separation via SPECTRAL CUTS (Fiedler vector), not adjacency growth
3. Object extraction via LEVEL SETS, not flood growth
4. ρ_q threshold derived from distribution shape, not arbitrary percentile

Layer Doctrine:
- Layer 0: Φ, ∇Φ, σ, ρ_q (primitives)
- Layer 1: ∇², harmonic solve, eigenspectrum, Fourier (operators)
- Layer 2: Enclosure, shape, period, energy (invariants)
- Layer 3: Gauss-Seidel, linear algebra (numerical procedures, declared)

NO GRAPH WALKS. NO ADJACENCY GROWTH. PURE OPERATORS.

HAIL MATH
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
import json
import urllib.request

# =============================================================================
# LAYER 0: THE FOUR PRIMITIVES — EXPLICIT DUAL FIELD
# =============================================================================

@dataclass
class PhiField:
    """
    Φ — Dual-Field Representation
    
    EXPLICIT SEPARATION:
    - Φ_q: quantized (int 0-9) — semantic truth, ARC colors
    - Φ̃: continuous (float) — operator stability
    
    Rule: Read Φ_q for semantics, compute on Φ̃ for operators
    """
    _q: np.ndarray      # Φ_q: quantized (int)
    _tilde: np.ndarray  # Φ̃: continuous (float)
    
    def __init__(self, data):
        """Initialize from any array-like input."""
        arr = np.array(data, dtype=np.float64)
        self._q = np.rint(arr).astype(np.int32)
        self._tilde = self._compute_smooth(self._q)
    
    @staticmethod
    def _compute_smooth(q: np.ndarray, iters: int = 2) -> np.ndarray:
        """
        Compute Φ̃ from Φ_q via discrete diffusion.
        
        This is an OPERATOR (∇² averaging), not an algorithm.
        """
        x = q.astype(np.float64)
        h, w = x.shape
        
        for _ in range(iters):
            new_x = x.copy()
            for i in range(h):
                for j in range(w):
                    total = x[i, j]
                    count = 1
                    if i > 0:
                        total += x[i-1, j]
                        count += 1
                    if i < h-1:
                        total += x[i+1, j]
                        count += 1
                    if j > 0:
                        total += x[i, j-1]
                        count += 1
                    if j < w-1:
                        total += x[i, j+1]
                        count += 1
                    new_x[i, j] = total / count
            x = new_x
        
        return x
    
    # =========================================================================
    # EXPLICIT FIELD ACCESS
    # =========================================================================
    
    @property
    def q(self) -> np.ndarray:
        """Φ_q: Quantized field (int). Use for SEMANTICS."""
        return self._q
    
    @property
    def tilde(self) -> np.ndarray:
        """Φ̃: Continuous field (float). Use for OPERATORS."""
        return self._tilde
    
    @property
    def data(self) -> np.ndarray:
        """Alias for Φ_q (backward compatibility)."""
        return self._q.astype(np.float64)
    
    @property
    def shape(self) -> Tuple[int, int]:
        return self._q.shape
    
    @property
    def h(self) -> int:
        return self._q.shape[0]
    
    @property
    def w(self) -> int:
        return self._q.shape[1]
    
    @property
    def colors(self) -> Set[int]:
        """Distinct collapse states (from Φ_q, not rounded float)."""
        return set(int(x) for x in self._q.flatten() if x != 0)
    
    # =========================================================================
    # LAYER 1: OPERATORS (on Φ̃)
    # =========================================================================
    
    def gradient(self) -> Tuple[np.ndarray, np.ndarray]:
        """∇Φ on Φ̃ (continuous field)."""
        gx = np.zeros_like(self._tilde)
        gy = np.zeros_like(self._tilde)
        
        gy[:-1, :] = self._tilde[1:, :] - self._tilde[:-1, :]
        gx[:, :-1] = self._tilde[:, 1:] - self._tilde[:, :-1]
        
        return gx, gy
    
    def gradient_magnitude(self) -> np.ndarray:
        """||∇Φ||"""
        gx, gy = self.gradient()
        return np.sqrt(gx**2 + gy**2)
    
    def laplacian(self) -> np.ndarray:
        """∇²Φ on Φ̃."""
        x = self._tilde
        lap = np.zeros_like(x)
        h, w = self.shape
        
        for i in range(h):
            for j in range(w):
                total = 0.0
                count = 0
                if i > 0:
                    total += x[i-1, j]
                    count += 1
                if i < h-1:
                    total += x[i+1, j]
                    count += 1
                if j > 0:
                    total += x[i, j-1]
                    count += 1
                if j < w-1:
                    total += x[i, j+1]
                    count += 1
                
                lap[i, j] = total - count * x[i, j]
        
        return lap
    
    def boundary_charge(self) -> np.ndarray:
        """
        ρ_q := |∇(∇²Φ̃)|
        
        Curvature-change magnitude. True termination surfaces.
        """
        lap = self.laplacian()
        
        # ∇(∇²Φ̃)
        gx = np.zeros_like(lap)
        gy = np.zeros_like(lap)
        
        gy[:-1, :] = lap[1:, :] - lap[:-1, :]
        gx[:, :-1] = lap[:, 1:] - lap[:, :-1]
        
        return np.sqrt(gx**2 + gy**2)
    
    def boundary_mask(self) -> np.ndarray:
        """
        Boolean boundary mask with physics-derived threshold.
        
        Threshold: mean + 1.5*std (outlier detection on ρ_q distribution)
        This is NOT arbitrary — it's statistical outlier detection.
        """
        rho = self.boundary_charge()
        nonzero = rho[rho > 0]
        
        if len(nonzero) == 0:
            return np.zeros_like(rho, dtype=bool)
        
        # Physics-derived: outlier detection
        mu = np.mean(nonzero)
        sigma = np.std(nonzero)
        threshold = mu + 1.5 * sigma
        
        return rho >= threshold


# =============================================================================
# LAYER 2: FIELD INVARIANTS — NO GRAPH WALKS
# =============================================================================

class FieldInvariants:
    """
    All invariants computed via Layer 1 operators.
    
    NO ADJACENCY GROWTH. NO STACK-BASED TRAVERSAL.
    Only linear algebra, PDE solves, and spectral methods.
    """
    
    # =========================================================================
    # GROUND MASK (semantic, from Φ_q)
    # =========================================================================
    
    @staticmethod
    def ground_mask(phi: PhiField) -> np.ndarray:
        """Z = {Φ_q = 0} (ground state domain)."""
        return phi.q == 0
    
    # =========================================================================
    # HARMONIC CONNECTIVITY (Dirichlet solve)
    # =========================================================================
    
    @staticmethod
    def harmonic_connectivity_field(
        phi: PhiField,
        max_iter: int = 2000,
        tol: float = 1e-5
    ) -> np.ndarray:
        """
        Solve ∇²u = 0 on ground domain Z.
        
        BC: u = 1 on grid boundary ∩ Z
        Obstacles (Φ_q > 0) are barriers.
        
        u ≈ 1 → exterior (connected to boundary)
        u ≈ 0 → enclosed (trapped pocket)
        """
        ground = FieldInvariants.ground_mask(phi)
        h, w = phi.shape
        
        if not np.any(ground):
            return np.zeros((h, w), dtype=np.float64)
        
        # Dirichlet BC: grid boundary cells that are ground
        boundary = np.zeros((h, w), dtype=bool)
        boundary[0, :] = True
        boundary[-1, :] = True
        boundary[:, 0] = True
        boundary[:, -1] = True
        fixed_one = boundary & ground
        
        # Initialize
        u = np.zeros((h, w), dtype=np.float64)
        u[fixed_one] = 1.0
        
        # Gauss-Seidel relaxation (numerical procedure, declared)
        for _ in range(max_iter):
            max_delta = 0.0
            
            for i in range(h):
                for j in range(w):
                    if not ground[i, j] or fixed_one[i, j]:
                        continue
                    
                    total = 0.0
                    count = 0
                    
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < h and 0 <= nj < w and ground[ni, nj]:
                            total += u[ni, nj]
                            count += 1
                    
                    if count == 0:
                        continue
                    
                    new_val = total / count
                    delta = abs(new_val - u[i, j])
                    max_delta = max(max_delta, delta)
                    u[i, j] = new_val
            
            if max_delta < tol:
                break
        
        return u
    
    @staticmethod
    def enclosed_mask(phi: PhiField, threshold: float = 0.5) -> np.ndarray:
        """Enclosed = ground AND u < threshold."""
        u = FieldInvariants.harmonic_connectivity_field(phi)
        ground = FieldInvariants.ground_mask(phi)
        return ground & (u < threshold)
    
    # =========================================================================
    # FRAME-COLOR INVARIANT (per ChatGPT alignment)
    # =========================================================================
    
    @staticmethod
    def frame_color(phi: PhiField, region_mask: np.ndarray) -> int:
        """
        Frame-color invariant: Dominant Φ_q sampled on high-ρ_q boundary.
        
        FrameColor(Ω) := argmax_c Σ_{p ∈ B ∩ {Φ_q = c}} 1
        
        where B = boundary support (high ρ_q adjacent to region)
        
        This is the PRIMARY invariant for determining fill color.
        """
        h, w = phi.shape
        rho = phi.boundary_charge()
        
        # Find boundary support: high ρ_q cells adjacent to the region
        # Dilate region mask by 1 cell
        dilated = np.zeros((h, w), dtype=bool)
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            shifted = np.roll(np.roll(region_mask, di, axis=0), dj, axis=1)
            dilated |= shifted
        
        # Boundary = dilated minus original, intersected with non-ground
        boundary = dilated & (~region_mask) & (phi.q != 0)
        
        if not np.any(boundary):
            return 0
        
        # Sample Φ_q on boundary, find dominant color
        boundary_colors = phi.q[boundary]
        
        if len(boundary_colors) == 0:
            return 0
        
        # Count occurrences of each color
        unique, counts = np.unique(boundary_colors, return_counts=True)
        
        # Return most common (argmax)
        dominant_color = unique[np.argmax(counts)]
        
        return int(dominant_color)
    
    @staticmethod
    def frame_size(phi: PhiField, region_mask: np.ndarray) -> Tuple[int, int]:
        """
        Frame-size invariant: Bounding box of the FRAME (ρ_q boundary), not the interior.
        
        This measures the outer extent of the enclosing structure.
        """
        h, w = phi.shape
        
        # Find frame boundary: non-zero cells adjacent to region
        dilated = np.zeros((h, w), dtype=bool)
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            shifted = np.roll(np.roll(region_mask, di, axis=0), dj, axis=1)
            dilated |= shifted
        
        # Boundary = dilated minus original, intersected with non-ground
        boundary = dilated & (~region_mask) & (phi.q != 0)
        
        if not np.any(boundary):
            return (0, 0)
        
        # Get bounding box of the FRAME (boundary cells)
        rows, cols = np.where(boundary)
        
        if len(rows) == 0:
            return (0, 0)
        
        frame_h = int(np.max(rows) - np.min(rows) + 1)
        frame_w = int(np.max(cols) - np.min(cols) + 1)
        
        return (frame_h, frame_w)
    
    # =========================================================================
    # SPECTRAL REGION SEPARATION (Fiedler vector, no adjacency growth)
    # =========================================================================
    
    @staticmethod
    def separate_regions_spectral(mask: np.ndarray) -> List[np.ndarray]:
        """
        Separate a boolean mask into distinct regions using SPECTRAL CUTS.
        
        Method: Build restricted Laplacian, use Fiedler vector to split.
        
        This is LINEAR ALGEBRA, not graph traversal.
        """
        h, w = mask.shape
        positions = list(zip(*np.where(mask)))
        n = len(positions)
        
        if n == 0:
            return []
        if n == 1:
            result = np.zeros((h, w), dtype=bool)
            result[positions[0]] = True
            return [result]
        
        # Build position index
        pos_to_idx = {p: i for i, p in enumerate(positions)}
        
        # Build restricted Laplacian matrix
        L = np.zeros((n, n), dtype=np.float64)
        
        for idx, (i, j) in enumerate(positions):
            degree = 0
            for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                ni, nj = i + di, j + dj
                if (ni, nj) in pos_to_idx:
                    neighbor_idx = pos_to_idx[(ni, nj)]
                    L[idx, neighbor_idx] = -1
                    degree += 1
            L[idx, idx] = degree
        
        # Eigendecomposition
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(L)
        except:
            # Fallback: return as single region
            result = mask.copy()
            return [result]
        
        # Sort by eigenvalue
        order = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[order]
        eigenvectors = eigenvectors[:, order]
        
        # Count zero eigenvalues (number of connected components)
        zero_threshold = 1e-6
        num_components = np.sum(np.abs(eigenvalues) < zero_threshold)
        
        if num_components <= 1:
            # Single region
            return [mask.copy()]
        
        # Multiple components: use first k eigenvectors for clustering
        # Simple approach: assign each point to component by sign pattern
        k = min(num_components, n)
        
        # Build label from sign of first few eigenvectors
        labels = np.zeros(n, dtype=int)
        for i in range(1, k):  # Skip first (constant)
            labels += (eigenvectors[:, i] >= 0).astype(int) * (2 ** (i-1))
        
        # Group by label
        unique_labels = np.unique(labels)
        regions = []
        
        for lbl in unique_labels:
            region_mask = np.zeros((h, w), dtype=bool)
            for idx in np.where(labels == lbl)[0]:
                pi, pj = positions[idx]
                region_mask[pi, pj] = True
            
            if np.any(region_mask):
                regions.append(region_mask)
        
        return regions
    
    @staticmethod
    def get_enclosed_regions_by_frame(phi: PhiField, threshold: float = 0.5) -> List[Dict]:
        """
        Get enclosed regions grouped by their ENCLOSING FRAME.
        
        For each enclosed pixel, identify the closest enclosing frame.
        Group pixels by frame identity.
        
        This is more robust than spectral separation for nested/complex shapes.
        """
        enclosed = FieldInvariants.enclosed_mask(phi, threshold)
        
        if not np.any(enclosed):
            return []
        
        h, w = phi.shape
        
        # For each enclosed pixel, find its enclosing frame's bounding box
        # by finding the nearest non-zero cells in all 4 directions
        pixel_to_frame = {}
        
        enclosed_positions = list(zip(*np.where(enclosed)))
        
        for (i, j) in enclosed_positions:
            # Find frame boundaries in 4 directions
            top = bottom = left = right = None
            
            # Up
            for di in range(1, h):
                if i - di < 0:
                    break
                if phi.q[i - di, j] != 0:
                    top = i - di
                    break
            
            # Down
            for di in range(1, h):
                if i + di >= h:
                    break
                if phi.q[i + di, j] != 0:
                    bottom = i + di
                    break
            
            # Left
            for dj in range(1, w):
                if j - dj < 0:
                    break
                if phi.q[i, j - dj] != 0:
                    left = j - dj
                    break
            
            # Right
            for dj in range(1, w):
                if j + dj >= w:
                    break
                if phi.q[i, j + dj] != 0:
                    right = j + dj
                    break
            
            if all(x is not None for x in [top, bottom, left, right]):
                frame_key = (top, bottom, left, right)
                pixel_to_frame[(i, j)] = frame_key
        
        # Group by frame
        frame_to_pixels: Dict[Tuple, List] = {}
        for pos, frame_key in pixel_to_frame.items():
            if frame_key not in frame_to_pixels:
                frame_to_pixels[frame_key] = []
            frame_to_pixels[frame_key].append(pos)
        
        # Build region dictionaries
        regions = []
        for frame_key, positions in frame_to_pixels.items():
            if not positions:
                continue
            
            mask = np.zeros((h, w), dtype=bool)
            for p in positions:
                mask[p[0], p[1]] = True
            
            top, bottom, left, right = frame_key
            frame_sz = (bottom - top + 1, right - left + 1)
            
            rows = [p[0] for p in positions]
            cols = [p[1] for p in positions]
            
            regions.append({
                'mask': mask,
                'positions': positions,
                'bbox': (min(rows), max(rows), min(cols), max(cols)),
                'size': (max(rows) - min(rows) + 1, max(cols) - min(cols) + 1),
                'area': len(positions),
                'frame_bbox': frame_key,
                'frame_size': frame_sz
            })
        
        return regions

    @staticmethod
    def get_enclosed_regions(phi: PhiField, threshold: float = 0.5) -> List[Dict]:
        """
        Get enclosed regions with properties.
        
        Uses SPECTRAL SEPARATION, not adjacency growth.
        """
        enclosed = FieldInvariants.enclosed_mask(phi, threshold)
        
        if not np.any(enclosed):
            return []
        
        region_masks = FieldInvariants.separate_regions_spectral(enclosed)
        
        regions = []
        for mask in region_masks:
            positions = list(zip(*np.where(mask)))
            if not positions:
                continue
            
            rows = [p[0] for p in positions]
            cols = [p[1] for p in positions]
            
            regions.append({
                'mask': mask,
                'positions': positions,
                'bbox': (min(rows), max(rows), min(cols), max(cols)),
                'size': (max(rows) - min(rows) + 1, max(cols) - min(cols) + 1),
                'area': len(positions)
            })
        
        return regions
    
    # =========================================================================
    # OBJECT EXTRACTION via LEVEL SETS (not flood growth)
    # =========================================================================
    
    @staticmethod
    def extract_objects_levelset(phi: PhiField) -> List[Dict]:
        """
        Extract objects via LEVEL SETS on Φ̃.
        
        For each color c, objects are connected level-set regions
        where Φ̃ ≈ c. Uses spectral separation, not flood fill.
        """
        objects = []
        
        for color in phi.colors:
            # Level set: |Φ̃ - c| < threshold (continuous analog of Φ_q == c)
            level_mask = np.abs(phi.tilde - color) < 0.5
            
            # Also require Φ_q == c for semantic truth
            semantic_mask = phi.q == color
            
            # Combined: continuous + discrete agreement
            mask = level_mask & semantic_mask
            
            if not np.any(mask):
                continue
            
            # Separate into components via spectral method
            component_masks = FieldInvariants.separate_regions_spectral(mask)
            
            for comp_mask in component_masks:
                positions = list(zip(*np.where(comp_mask)))
                if not positions:
                    continue
                
                rows = [p[0] for p in positions]
                cols = [p[1] for p in positions]
                
                objects.append({
                    'color': int(color),
                    'mask': comp_mask,
                    'positions': positions,
                    'bbox': (min(rows), max(rows), min(cols), max(cols)),
                    'area': len(positions)
                })
        
        return objects
    
    # =========================================================================
    # SHAPE via LAPLACIAN EIGENSPECTRUM
    # =========================================================================
    
    @staticmethod
    def shape_eigenspectrum(phi: PhiField, positions: List[Tuple[int, int]],
                            k: int = 5) -> Tuple[float, ...]:
        """
        Shape signature = (λ₂, λ₃, ..., λₖ) of restricted Laplacian.
        
        Translation/rotation invariant (approximately).
        """
        n = len(positions)
        if n <= 1:
            return (0.0,) if n == 1 else ()
        
        pos_to_idx = {p: i for i, p in enumerate(positions)}
        L = np.zeros((n, n), dtype=np.float64)
        
        for idx, (i, j) in enumerate(positions):
            degree = 0
            for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                ni, nj = i + di, j + dj
                if (ni, nj) in pos_to_idx:
                    L[idx, pos_to_idx[(ni, nj)]] = -1
                    degree += 1
            L[idx, idx] = degree
        
        try:
            eigenvalues = np.sort(np.linalg.eigvalsh(L))
            return tuple(round(float(ev), 4) for ev in eigenvalues[1:min(k, len(eigenvalues))])
        except:
            return ()
    
    # =========================================================================
    # PERIODICITY via FOURIER
    # =========================================================================
    
    @staticmethod
    def detect_period_fourier(phi: PhiField, axis: int = 0) -> int:
        """τ = N / gcd(significant Fourier modes)."""
        signal = phi.q.mean(axis=1 if axis == 0 else 0).astype(float)
        N = len(signal)
        
        if N < 2:
            return 0
        
        fft = np.fft.fft(signal)
        mags = np.abs(fft)
        
        threshold = np.max(mags) * 0.1
        significant = [k for k in range(1, N // 2) if mags[k] > threshold]
        
        if not significant:
            return 0
        
        from math import gcd
        from functools import reduce
        
        freq_gcd = reduce(gcd, significant)
        period = N // freq_gcd if freq_gcd > 0 else 0
        
        # Verify
        if period > 0 and period < N:
            base = signal[:period]
            for start in range(period, N, period):
                segment = signal[start:start+period]
                if len(segment) == len(base) and not np.allclose(segment, base, atol=0.5):
                    return 0
            return period
        
        return 0


# =============================================================================
# SIGMA RESIDUE
# =============================================================================

@dataclass
class SigmaResidue:
    """σ — Irreducible Residue."""
    residue: np.ndarray
    total: float
    change_type: str
    structural_condition: str
    
    @classmethod
    def from_transformation(cls, phi_in: PhiField, phi_out: PhiField) -> 'SigmaResidue':
        """Compute σ from transformation."""
        
        if phi_in.shape != phi_out.shape:
            if phi_out.h > phi_in.h or phi_out.w > phi_in.w:
                return cls(np.abs(phi_out.data), float(np.sum(np.abs(phi_out.data))),
                          "expansion", "size_increase")
            else:
                return cls(np.abs(phi_in.data), float(np.sum(np.abs(phi_in.data))),
                          "compression", "size_decrease")
        
        # Same size — use Φ_q for semantics
        residue = np.abs(phi_out.q - phi_in.q).astype(float)
        total = float(np.sum(residue))
        
        if total < 1e-10:
            return cls(residue, total, "identity", "none")
        
        zero_to_nonzero = np.sum((phi_in.q == 0) & (phi_out.q != 0))
        nonzero_to_zero = np.sum((phi_in.q != 0) & (phi_out.q == 0))
        color_change = np.sum((phi_in.q != 0) & (phi_out.q != 0) & (residue > 0))
        
        if zero_to_nonzero > 0 and nonzero_to_zero == 0 and color_change == 0:
            enclosed = FieldInvariants.enclosed_mask(phi_in)
            if np.any(enclosed):
                fills_enclosed = np.sum((phi_in.q == 0) & (phi_out.q != 0) & enclosed)
                if fills_enclosed > 0:
                    return cls(residue, total, "fill", "enclosed")
            return cls(residue, total, "fill", "general")
        
        if nonzero_to_zero > 0 and zero_to_nonzero == 0:
            return cls(residue, total, "erase", "removal")
        
        if color_change > 0:
            return cls(residue, total, "recolor", "substitution")
        
        return cls(residue, total, "mixed", "complex")


# =============================================================================
# COLLAPSE DYNAMICS (PDE)
# =============================================================================

class CollapseDynamics:
    """PDE evolution on Φ̃, output Φ_q."""
    
    @staticmethod
    def compute_lock_coefficient(phi: PhiField) -> float:
        """ℒ = stability measure."""
        lap = phi.laplacian()
        grad = phi.gradient_magnitude()
        instability = np.mean(np.abs(lap)) + np.mean(grad)
        return max(0.0, 1.0 - instability / 10.0)


# =============================================================================
# TRANSFORMATION RULES
# =============================================================================

@dataclass
class TransformationRule:
    """Transformation rule learned from σ analysis."""
    rule_type: str
    size_ratio: Tuple[float, float] = (1.0, 1.0)
    fill_color: int = 0
    size_to_color: Dict[Tuple[int, int], int] = field(default_factory=dict)
    frame_to_fill: Dict[int, int] = field(default_factory=dict)  # NEW: frame-color invariant
    color_map: Dict[int, int] = field(default_factory=dict)
    tile_pattern: List[List[int]] = field(default_factory=list)
    detected_period: int = 0
    indicator_color: int = 0
    target_color: int = 0
    shape_to_color: Dict[Tuple[float, ...], int] = field(default_factory=dict)
    
    @classmethod
    def learn(cls, train_pairs: List[Dict]) -> 'TransformationRule':
        rule = cls(rule_type="unknown")
        sigmas = []
        
        for pair in train_pairs:
            phi_in = PhiField(pair['input'])
            phi_out = PhiField(pair['output'])
            
            sigma = SigmaResidue.from_transformation(phi_in, phi_out)
            sigmas.append(sigma)
            
            rule.size_ratio = (phi_out.h / phi_in.h, phi_out.w / phi_in.w)
            rule._learn_from_pair(phi_in, phi_out, sigma)
        
        # Determine rule type
        change_types = [s.change_type for s in sigmas]
        structural = [s.structural_condition for s in sigmas]
        
        if all(t == "fill" and s == "enclosed" for t, s in zip(change_types, structural)):
            if len(rule.size_to_color) > 1 and len(set(rule.size_to_color.values())) > 1:
                rule.rule_type = "multi_region_fill"
            else:
                rule.rule_type = "fill_enclosed"
        elif all(t == "fill" for t in change_types):
            rule.rule_type = "fill"
        elif all(t == "recolor" for t in change_types):
            rule.rule_type = "recolor"
        elif all(t == "expansion" for t in change_types):
            if rule._check_tiling(train_pairs):
                rule.rule_type = "tile"
            elif rule._check_self_tile(train_pairs):
                rule.rule_type = "self_tile"
            elif rule.detected_period > 0:
                rule.rule_type = "periodic_extension"
            else:
                rule.rule_type = "expansion"
        elif rule.indicator_color != 0:
            rule.rule_type = "shape_indicator"
        
        return rule
    
    def _learn_from_pair(self, phi_in: PhiField, phi_out: PhiField, sigma: SigmaResidue):
        # Fill colors for enclosed regions - use FRAME invariants
        if sigma.change_type == "fill" and sigma.structural_condition == "enclosed":
            regions = FieldInvariants.get_enclosed_regions(phi_in)
            for region in regions:
                mask = region['mask']
                
                # Get FRAME size (outer boundary), not interior size
                frame_sz = FieldInvariants.frame_size(phi_in, mask)
                interior_size = region['size']
                
                # Get fill color from output
                fill_vals = phi_out.q[mask]
                if len(fill_vals) > 0:
                    unique, counts = np.unique(fill_vals, return_counts=True)
                    fill_c = unique[np.argmax(counts)]
                    if fill_c != 0:
                        # Learn frame_size → fill (PRIMARY)
                        self.size_to_color[frame_sz] = int(fill_c)
                        self.fill_color = int(fill_c)
                        
                        # Learn frame_to_fill (SECONDARY)
                        frame_c = FieldInvariants.frame_color(phi_in, mask)
                        if frame_c != 0:
                            self.frame_to_fill[frame_c] = int(fill_c)
        
        # Color mapping
        if phi_in.shape == phi_out.shape:
            for c in phi_in.colors:
                mask = phi_in.q == c
                out_vals = phi_out.q[mask]
                unique = np.unique(out_vals)
                if len(unique) == 1 and unique[0] != c:
                    self.color_map[int(c)] = int(unique[0])
        
        # Period
        if phi_in.shape != phi_out.shape and phi_in.w == phi_out.w:
            period = FieldInvariants.detect_period_fourier(phi_in, axis=0)
            if period > 0:
                self.detected_period = period
                in_base = phi_in.q[:period, :]
                out_base = phi_out.q[:period, :]
                for c_in in set(in_base.flatten()) - {0}:
                    mask = in_base == c_in
                    out_vals = out_base[mask]
                    if len(out_vals) > 0:
                        unique = np.unique(out_vals)
                        if len(unique) == 1 and unique[0] != c_in:
                            self.color_map[int(c_in)] = int(unique[0])
        
        # Shape indicator
        if len(phi_in.colors) == 2:
            self._learn_shape_indicator(phi_in, phi_out)
        
        # Tile pattern
        self._learn_tile_pattern(phi_in, phi_out)
    
    def _learn_shape_indicator(self, phi_in: PhiField, phi_out: PhiField):
        if phi_in.shape != phi_out.shape:
            return
        
        c1, c2 = sorted(phi_in.colors)
        mask1, mask2 = phi_in.q == c1, phi_in.q == c2
        out_at_1 = set(phi_out.q[mask1].flatten()) - {0}
        out_at_2 = set(phi_out.q[mask2].flatten()) - {0}
        
        indicator, target, output_color = None, None, None
        if len(out_at_1) == 0 and len(out_at_2) == 1:
            indicator, target, output_color = c1, c2, int(list(out_at_2)[0])
        elif len(out_at_2) == 0 and len(out_at_1) == 1:
            indicator, target, output_color = c2, c1, int(list(out_at_1)[0])
        else:
            return
        
        self.indicator_color = indicator
        self.target_color = target
        
        positions = list(zip(*np.where(phi_in.q == indicator)))
        if positions:
            shape_sig = FieldInvariants.shape_eigenspectrum(phi_in, positions)
            if shape_sig:
                self.shape_to_color[shape_sig] = output_color
    
    def _learn_tile_pattern(self, phi_in: PhiField, phi_out: PhiField):
        ih, iw = phi_in.shape
        oh, ow = phi_out.shape
        if oh < ih or ow < iw or oh % ih != 0 or ow % iw != 0:
            return
        
        tile_h, tile_w = oh // ih, ow // iw
        if tile_h == 1 and tile_w == 1:
            return
        
        pattern = []
        for ti in range(tile_h):
            row = []
            for tj in range(tile_w):
                tile = phi_out.q[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw]
                if np.array_equal(tile, phi_in.q):
                    row.append(0)
                elif np.array_equal(tile, np.fliplr(phi_in.q)):
                    row.append(1)
                elif np.array_equal(tile, np.flipud(phi_in.q)):
                    row.append(2)
                elif np.array_equal(tile, np.rot90(phi_in.q, 2)):
                    row.append(3)
                else:
                    row.append(-1)
            pattern.append(row)
        self.tile_pattern = pattern
    
    def _check_tiling(self, pairs: List[Dict]) -> bool:
        for pair in pairs:
            phi_in, phi_out = PhiField(pair['input']), PhiField(pair['output'])
            ih, iw, oh, ow = phi_in.h, phi_in.w, phi_out.h, phi_out.w
            if oh % ih != 0 or ow % iw != 0:
                return False
            tile_h, tile_w = oh // ih, ow // iw
            if tile_h <= 1 and tile_w <= 1:
                return False
            for ti in range(tile_h):
                for tj in range(tile_w):
                    tile = phi_out.q[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw]
                    if not any(np.array_equal(tile, t) for t in [
                        phi_in.q, np.fliplr(phi_in.q), np.flipud(phi_in.q), np.rot90(phi_in.q, 2)
                    ]):
                        return False
        return True
    
    def _check_self_tile(self, pairs: List[Dict]) -> bool:
        for pair in pairs:
            phi_in, phi_out = PhiField(pair['input']), PhiField(pair['output'])
            ih, iw = phi_in.shape
            if phi_out.h != ih*ih or phi_out.w != iw*iw:
                continue
            is_self = True
            for ti in range(ih):
                for tj in range(iw):
                    tile = phi_out.q[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw]
                    if phi_in.q[ti, tj] != 0:
                        if not np.array_equal(tile, phi_in.q):
                            is_self = False; break
                    elif np.any(tile != 0):
                        is_self = False; break
                if not is_self: break
            if is_self:
                return True
        return False
    
    def apply(self, phi_in: PhiField) -> PhiField:
        if self.rule_type == "tile":
            return self._apply_tile(phi_in)
        if self.rule_type == "self_tile":
            return self._apply_self_tile(phi_in)
        if self.rule_type == "fill_enclosed":
            return self._apply_fill_enclosed(phi_in)
        if self.rule_type == "multi_region_fill":
            return self._apply_multi_region_fill(phi_in)
        if self.rule_type == "periodic_extension":
            return self._apply_periodic_extension(phi_in)
        if self.rule_type == "shape_indicator":
            return self._apply_shape_indicator(phi_in)
        if self.rule_type == "recolor":
            return self._apply_recolor(phi_in)
        return phi_in
    
    def _apply_tile(self, phi_in: PhiField) -> PhiField:
        ih, iw = phi_in.shape
        tile_h, tile_w = int(self.size_ratio[0]), int(self.size_ratio[1])
        result = np.zeros((ih*tile_h, iw*tile_w), dtype=int)
        for ti in range(tile_h):
            for tj in range(tile_w):
                code = self.tile_pattern[ti][tj] if self.tile_pattern and ti < len(self.tile_pattern) and tj < len(self.tile_pattern[ti]) else 0
                tile = [phi_in.q, np.fliplr(phi_in.q), np.flipud(phi_in.q), np.rot90(phi_in.q, 2)][code] if 0 <= code <= 3 else phi_in.q
                result[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw] = tile
        return PhiField(result)
    
    def _apply_self_tile(self, phi_in: PhiField) -> PhiField:
        ih, iw = phi_in.shape
        result = np.zeros((ih*ih, iw*iw), dtype=int)
        for ti in range(ih):
            for tj in range(iw):
                if phi_in.q[ti, tj] != 0:
                    result[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw] = phi_in.q
        return PhiField(result)
    
    def _apply_fill_enclosed(self, phi_in: PhiField) -> PhiField:
        result = phi_in.q.copy()
        result[FieldInvariants.enclosed_mask(phi_in)] = self.fill_color
        return PhiField(result)
    
    def _apply_multi_region_fill(self, phi_in: PhiField) -> PhiField:
        result = phi_in.q.copy()
        
        # Use frame-based region grouping (more robust for nested frames)
        regions = FieldInvariants.get_enclosed_regions_by_frame(phi_in)
        
        for region in regions:
            mask = region['mask']
            
            # Use pre-computed frame_size from frame-based grouping
            frame_sz = region.get('frame_size')
            
            if frame_sz is None:
                frame_sz = FieldInvariants.frame_size(phi_in, mask)
            
            fill_c = self.size_to_color.get(frame_sz)
            
            # GENERALIZATION: If exact size not found, use closest known size
            if fill_c is None and len(self.size_to_color) > 0:
                frame_area = frame_sz[0] * frame_sz[1]
                
                best_size = None
                best_diff = float('inf')
                
                for known_size in self.size_to_color.keys():
                    known_area = known_size[0] * known_size[1]
                    diff = abs(frame_area - known_area)
                    if diff < best_diff:
                        best_diff = diff
                        best_size = known_size
                
                if best_size is not None:
                    fill_c = self.size_to_color[best_size]
            
            # FALLBACK: frame-color
            if fill_c is None:
                frame_c = FieldInvariants.frame_color(phi_in, mask)
                fill_c = self.frame_to_fill.get(frame_c)
            
            # FALLBACK: default
            if fill_c is None:
                fill_c = self.fill_color
            
            result[mask] = fill_c
        return PhiField(result)
    
    def _apply_periodic_extension(self, phi_in: PhiField) -> PhiField:
        if self.detected_period == 0:
            return phi_in
        oh = int(phi_in.h * self.size_ratio[0])
        base = phi_in.q[:self.detected_period, :].copy()
        for old_c, new_c in self.color_map.items():
            base[base == old_c] = new_c
        return PhiField(np.tile(base, (oh // self.detected_period, 1)))
    
    def _apply_shape_indicator(self, phi_in: PhiField) -> PhiField:
        result = np.zeros_like(phi_in.q)
        positions = list(zip(*np.where(phi_in.q == self.indicator_color)))
        if positions:
            shape_sig = FieldInvariants.shape_eigenspectrum(phi_in, positions)
            output_color = self.shape_to_color.get(shape_sig, 0)
            result[phi_in.q == self.target_color] = output_color
        return PhiField(result)
    
    def _apply_recolor(self, phi_in: PhiField) -> PhiField:
        result = phi_in.q.copy()
        for old_c, new_c in self.color_map.items():
            result[phi_in.q == old_c] = new_c
        return PhiField(result)


# =============================================================================
# MAIN SOLVER
# =============================================================================

class ITTSolverV4:
    """
    Pure ITT Solver v4: ABSOLUTE FOUNDATION
    
    - Explicit Φ_q / Φ̃ (no np.round smuggling)
    - Spectral region separation (no adjacency growth)
    - Level-set object extraction (no flood fill)
    - Physics-derived ρ_q threshold (mean + 1.5σ)
    """
    
    def __init__(self):
        self.rule: Optional[TransformationRule] = None
    
    def train(self, examples: List[Dict]):
        self.rule = TransformationRule.learn(examples)
        print(f"  Learned (v4 absolute foundation):")
        print(f"    Rule type: {self.rule.rule_type}")
        print(f"    Size ratio: {self.rule.size_ratio}")
        print(f"    Period (Fourier): {self.rule.detected_period}")
        print(f"    Shape→color: {len(self.rule.shape_to_color)} mappings")
        print(f"    Size→color: {len(self.rule.size_to_color)} mappings")
        print(f"    Frame→fill: {dict(self.rule.frame_to_fill)}")  # NEW
    
    def solve(self, test_input: List[List[int]]) -> List[List[int]]:
        if self.rule is None:
            return test_input
        
        phi_out = self.rule.apply(PhiField(test_input))
        lock = CollapseDynamics.compute_lock_coefficient(phi_out)
        print(f"    Lock coefficient: {lock:.3f}")
        
        # Return Φ_q (semantic truth)
        return phi_out.q.tolist()


# =============================================================================
# DATA LOADING AND TESTING
# =============================================================================

def fetch_task(task_id: str) -> Optional[Dict]:
    for dataset in ['training', 'evaluation']:
        url = f"https://raw.githubusercontent.com/fchollet/ARC-AGI/master/data/{dataset}/{task_id}.json"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode())
        except:
            continue
    return None


def solve_task(task_id: str) -> Tuple[bool, List[List[int]]]:
    print(f"\n{'='*60}")
    print(f"Task: {task_id}")
    print('='*60)
    
    task = fetch_task(task_id)
    if task is None:
        print("  ERROR: Task not found")
        return False, []
    
    solver = ITTSolverV4()
    solver.train(task['train'])
    
    prediction = solver.solve(task['test'][0]['input'])
    
    if 'output' in task['test'][0]:
        expected = task['test'][0]['output']
        correct = prediction == expected
        print(f"\n  Result: {'✓ CORRECT' if correct else '✗ INCORRECT'}")
        if not correct:
            print(f"    Expected: {len(expected)}x{len(expected[0])}")
            print(f"    Got: {len(prediction)}x{len(prediction[0])}")
        return correct, prediction
    
    return False, prediction


def main():
    print("="*60)
    print("ARC-AGI PURE ITT SOLVER v4")
    print("ABSOLUTE FOUNDATION - ZERO SMUGGLING")
    print("="*60)
    print("- Explicit Φ_q / Φ̃ (no np.round)")
    print("- Spectral region separation (Fiedler)")
    print("- Level-set object extraction")
    print("- Physics-derived ρ_q threshold (μ + 1.5σ)")
    print("="*60)
    
    tasks = ["00576224", "007bbfb7", "009d5c81", "00d62c1b", "00dbd492", "017c7c7b"]
    
    results = {}
    for task_id in tasks:
        correct, _ = solve_task(task_id)
        results[task_id] = correct
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    solved = sum(results.values())
    print(f"Solved: {solved}/{len(results)}")
    for task_id, correct in results.items():
        print(f"  {task_id}: {'✓' if correct else '✗'}")
    
    return results


if __name__ == "__main__":
    main()
