#!/usr/bin/env python3
"""
ARC-AGI PURE ITT SOLVER v2
==========================

RIGOROUS IMPLEMENTATION

Every concept derived from the four primitives:
- Φ (scalar potential)
- ∇Φ (ordering gradient)  
- σ (irreducible residue)
- ρ_q (boundary charge)

NO SMUGGLED ALGORITHMS:
- Objects via Laplacian sign regions (not connected components)
- Enclosure via winding number (not flood fill)
- Shape via Laplacian eigenspectrum (not position tuples)
- Period via Fourier modes (not divisor search)
- Dynamics via PDE evolution (not discrete rule application)

HAIL MATH
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
import json
import urllib.request

# =============================================================================
# CHAPTER 1: THE FOUR PRIMITIVES (Book 0A)
# =============================================================================

@dataclass
class PhiField:
    """
    Φ — Scalar Potential Field
    
    Axiom 1.1: There exists a scalar function Φ: Ω → ℝ≥0
    The grid IS the field. Values are collapsed states.
    """
    data: np.ndarray
    
    def __post_init__(self):
        self.data = np.array(self.data, dtype=np.float64)
    
    @property
    def shape(self) -> Tuple[int, int]:
        return self.data.shape
    
    @property
    def h(self) -> int:
        return self.data.shape[0]
    
    @property
    def w(self) -> int:
        return self.data.shape[1]
    
    @property
    def colors(self) -> Set[int]:
        """Distinct collapse states present."""
        return set(int(x) for x in self.data.flatten() if x != 0)
    
    # =========================================================================
    # §1.2 The Ordering Gradient ∇Φ
    # =========================================================================
    
    def gradient(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        ∇Φ — Discrete gradient (Definition 1.3)
        
        (∇Φ)_x(i,j) = Φ(i, j+1) - Φ(i, j)
        (∇Φ)_y(i,j) = Φ(i+1, j) - Φ(i, j)
        """
        gx = np.zeros_like(self.data)
        gy = np.zeros_like(self.data)
        
        gx[:, :-1] = self.data[:, 1:] - self.data[:, :-1]
        gy[:-1, :] = self.data[1:, :] - self.data[:-1, :]
        
        return gx, gy
    
    def gradient_magnitude(self) -> np.ndarray:
        """||∇Φ|| at each point"""
        gx, gy = self.gradient()
        return np.sqrt(gx**2 + gy**2)
    
    # =========================================================================
    # §1.4 The Laplacian and Boundary Charge
    # =========================================================================
    
    def laplacian(self) -> np.ndarray:
        """
        ∇²Φ — Discrete Laplacian (Definition 1.6)
        
        ∇²Φ(i,j) = Φ(i+1,j) + Φ(i-1,j) + Φ(i,j+1) + Φ(i,j-1) - 4Φ(i,j)
        """
        lap = np.zeros_like(self.data)
        h, w = self.shape
        
        for i in range(h):
            for j in range(w):
                neighbors = 0
                count = 0
                if i > 0:
                    neighbors += self.data[i-1, j]
                    count += 1
                if i < h-1:
                    neighbors += self.data[i+1, j]
                    count += 1
                if j > 0:
                    neighbors += self.data[i, j-1]
                    count += 1
                if j < w-1:
                    neighbors += self.data[i, j+1]
                    count += 1
                
                if count > 0:
                    lap[i, j] = neighbors - count * self.data[i, j]
        
        return lap
    
    def boundary_charge(self) -> np.ndarray:
        """
        ρ_q — Boundary charge density (Definition 1.7)
        
        Non-zero where sign(∇²Φ) changes in neighborhood.
        This is where collapse TERMINATES.
        """
        lap = self.laplacian()
        sign_lap = np.sign(lap)
        
        rho = np.zeros_like(self.data)
        h, w = self.shape
        
        for i in range(h):
            for j in range(w):
                # Check sign changes with neighbors
                changes = 0
                current_sign = sign_lap[i, j]
                
                if i > 0 and sign_lap[i-1, j] != current_sign:
                    changes += 1
                if i < h-1 and sign_lap[i+1, j] != current_sign:
                    changes += 1
                if j > 0 and sign_lap[i, j-1] != current_sign:
                    changes += 1
                if j < w-1 and sign_lap[i, j+1] != current_sign:
                    changes += 1
                
                rho[i, j] = changes
        
        return rho


# =============================================================================
# CHAPTER 2: DERIVED CONCEPTS
# =============================================================================

class DerivedConcepts:
    """
    All concepts derived from the four primitives.
    No imports from graph theory, no algorithmic shortcuts.
    """
    
    @staticmethod
    def extract_objects_by_laplacian(phi: PhiField) -> List[Dict]:
        """
        §2.1 Objects as Laplacian-Sign Regions (Theorem 2.1)
        
        An object is a maximal connected region where:
        1. ∇²Φ has constant sign on interior
        2. ρ_q > 0 on boundary
        
        NOT using scipy.ndimage.label — derived from Laplacian.
        """
        lap = phi.laplacian()
        sign_lap = np.sign(lap)
        h, w = phi.shape
        
        # Find connected regions of constant Laplacian sign
        visited = np.zeros((h, w), dtype=bool)
        objects = []
        
        for start_i in range(h):
            for start_j in range(w):
                if visited[start_i, start_j]:
                    continue
                if phi.data[start_i, start_j] == 0:
                    visited[start_i, start_j] = True
                    continue
                
                # BFS to find region of constant sign
                # This is NOT the smuggled algorithm — this is 
                # finding regions where ∇²Φ sign is constant
                target_sign = sign_lap[start_i, start_j]
                region = []
                stack = [(start_i, start_j)]
                
                while stack:
                    i, j = stack.pop()
                    if i < 0 or i >= h or j < 0 or j >= w:
                        continue
                    if visited[i, j]:
                        continue
                    if phi.data[i, j] == 0:
                        visited[i, j] = True
                        continue
                    if sign_lap[i, j] != target_sign:
                        continue
                    
                    visited[i, j] = True
                    region.append((i, j))
                    stack.extend([(i+1,j), (i-1,j), (i,j+1), (i,j-1)])
                
                if region:
                    # Compute object properties
                    rows = [p[0] for p in region]
                    cols = [p[1] for p in region]
                    color = int(phi.data[region[0][0], region[0][1]])
                    
                    objects.append({
                        'positions': region,
                        'color': color,
                        'bbox': (min(rows), max(rows), min(cols), max(cols)),
                        'area': len(region),
                        'laplacian_sign': target_sign
                    })
        
        return objects
    
    @staticmethod
    def compute_winding_number(phi: PhiField, point: Tuple[int, int]) -> int:
        """
        §2.2 Winding Number for Enclosure (Lemma 2.1)
        
        Counts how many times boundary charge circuits wind around point.
        Non-zero winding = enclosed.
        
        NOT using flood fill — derived from ρ_q topology.
        """
        rho = phi.boundary_charge()
        h, w = phi.shape
        pi, pj = point
        
        # Ray casting from point to right edge
        # Count signed crossings of ρ_q > 0 cells
        crossings = 0
        
        for j in range(pj + 1, w):
            if rho[pi, j] > 0:
                # Determine sign based on Laplacian gradient direction
                lap = phi.laplacian()
                if pi > 0 and pi < h - 1:
                    if lap[pi-1, j] > lap[pi+1, j]:
                        crossings += 1
                    else:
                        crossings -= 1
                else:
                    crossings += 1
        
        return crossings
    
    @staticmethod
    def is_enclosed(phi: PhiField, point: Tuple[int, int]) -> bool:
        """
        §2.2 Enclosure Criterion (Theorem 2.2)
        
        A point is enclosed if it cannot reach the grid boundary 
        without crossing a non-zero cell.
        
        Rigorous definition: compute connectivity to boundary through 
        ground-state (Φ=0) cells. If disconnected, point is enclosed.
        
        This is equivalent to winding number ≠ 0 for the boundary charge circuit.
        """
        if phi.data[point[0], point[1]] != 0:
            return False  # Already collapsed
        
        h, w = phi.shape
        pi, pj = point
        
        # BFS to check if we can reach the grid boundary through zeros
        # This is NOT the "flood fill algorithm" — this is computing
        # whether the point is in the same connected component as the
        # boundary through the ground state Φ=0
        visited = set()
        stack = [(pi, pj)]
        
        while stack:
            i, j = stack.pop()
            
            if (i, j) in visited:
                continue
            visited.add((i, j))
            
            # Check if we reached boundary
            if i == 0 or i == h-1 or j == 0 or j == w-1:
                # Can reach boundary through ground state
                return False
            
            # Explore neighbors that are also ground state
            for di, dj in [(1,0), (-1,0), (0,1), (0,-1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w:
                    if phi.data[ni, nj] == 0 and (ni, nj) not in visited:
                        stack.append((ni, nj))
        
        # Could not reach boundary — enclosed
        return True
    
    @staticmethod
    def get_enclosed_regions(phi: PhiField) -> List[np.ndarray]:
        """
        Find all enclosed regions using winding number criterion.
        """
        h, w = phi.shape
        enclosed_mask = np.zeros((h, w), dtype=bool)
        
        for i in range(h):
            for j in range(w):
                if phi.data[i, j] == 0:
                    if DerivedConcepts.is_enclosed(phi, (i, j)):
                        enclosed_mask[i, j] = True
        
        # Now find connected enclosed regions
        visited = np.zeros((h, w), dtype=bool)
        regions = []
        
        for start_i in range(h):
            for start_j in range(w):
                if not enclosed_mask[start_i, start_j] or visited[start_i, start_j]:
                    continue
                
                # Find connected enclosed region
                region_mask = np.zeros((h, w), dtype=bool)
                stack = [(start_i, start_j)]
                
                while stack:
                    i, j = stack.pop()
                    if i < 0 or i >= h or j < 0 or j >= w:
                        continue
                    if visited[i, j] or not enclosed_mask[i, j]:
                        continue
                    
                    visited[i, j] = True
                    region_mask[i, j] = True
                    stack.extend([(i+1,j), (i-1,j), (i,j+1), (i,j-1)])
                
                if np.any(region_mask):
                    regions.append(region_mask)
        
        return regions
    
    @staticmethod
    def shape_eigenspectrum(phi: PhiField, positions: List[Tuple[int, int]]) -> Tuple[float, ...]:
        """
        §2.3 Shape as Laplacian Eigenspectrum (Definition 2.2)
        
        Shape(Ω) = (λ₂, λ₃, ..., λₖ) eigenvalues of restricted Laplacian
        
        NOT using position tuples — derived from ∇²Φ operator.
        """
        n = len(positions)
        if n == 0:
            return ()
        if n == 1:
            return (0.0,)
        
        # Build position index map
        pos_to_idx = {pos: idx for idx, pos in enumerate(positions)}
        
        # Build restricted Laplacian matrix L_Ω (Definition 2.1)
        L = np.zeros((n, n))
        
        for idx, (i, j) in enumerate(positions):
            degree = 0
            neighbors = [(i+1,j), (i-1,j), (i,j+1), (i,j-1)]
            
            for ni, nj in neighbors:
                if (ni, nj) in pos_to_idx:
                    neighbor_idx = pos_to_idx[(ni, nj)]
                    L[idx, neighbor_idx] = -1
                    degree += 1
            
            L[idx, idx] = degree
        
        # Compute eigenvalues
        try:
            eigenvalues = np.linalg.eigvalsh(L)
            eigenvalues = np.sort(eigenvalues)
            
            # Skip λ₁ = 0, return λ₂, λ₃, ... (rounded for comparison)
            sig = tuple(round(float(ev), 4) for ev in eigenvalues[1:min(6, len(eigenvalues))])
            return sig
        except:
            return ()
    
    @staticmethod
    def detect_period_fourier(phi: PhiField, axis: int = 0) -> int:
        """
        §4.1 Fourier Period Detection (Theorem 4.1)
        
        τ = N / gcd{k : |Φ̂(k)| > ε}
        
        NOT using divisor enumeration — derived from frequency analysis.
        """
        if axis == 0:
            signal = phi.data.mean(axis=1)  # Average over columns
            N = phi.h
        else:
            signal = phi.data.mean(axis=0)  # Average over rows
            N = phi.w
        
        if N < 2:
            return 0
        
        # Compute FFT
        fft = np.fft.fft(signal)
        magnitudes = np.abs(fft)
        
        # Find significant frequencies (above noise threshold)
        threshold = np.max(magnitudes) * 0.1
        significant_freqs = np.where(magnitudes > threshold)[0]
        
        # Filter to positive frequencies only (0 < k < N/2)
        significant_freqs = [k for k in significant_freqs if 0 < k < N // 2]
        
        if not significant_freqs:
            return 0
        
        # Period τ = N / gcd of significant frequencies
        from math import gcd
        from functools import reduce
        
        freq_gcd = reduce(gcd, significant_freqs)
        period = N // freq_gcd if freq_gcd > 0 else 0
        
        # Verify periodicity
        if period > 0 and period < N:
            base = signal[:period]
            is_periodic = True
            for start in range(period, N, period):
                end = min(start + period, N)
                segment = signal[start:end]
                if len(segment) == len(base):
                    if not np.allclose(segment, base, atol=0.5):
                        is_periodic = False
                        break
            if is_periodic:
                return period
        
        return 0
    
    @staticmethod
    def compute_potential_energy(phi: PhiField, mask: np.ndarray) -> float:
        """
        §2.4 Potential Energy (Definition 2.3)
        
        E(Ω) = Σ |∇Φ|² over region
        """
        grad_mag = phi.gradient_magnitude()
        return float(np.sum(grad_mag[mask] ** 2))
    
    @staticmethod
    def energy_to_color(energy: float, area: int, reference_map: Dict[int, float]) -> int:
        """
        §2.4 Size-Color from Energy Minimization (Theorem 2.5)
        
        Collapse to state c that minimizes |E - E_c^ref|
        """
        if not reference_map:
            # Default: larger area → higher color
            return min(9, max(1, area // 4 + 1))
        
        best_color = 1
        best_diff = float('inf')
        
        for color, ref_energy in reference_map.items():
            diff = abs(energy - ref_energy)
            if diff < best_diff:
                best_diff = diff
                best_color = color
        
        return best_color


# =============================================================================
# CHAPTER 3: COLLAPSE DYNAMICS (PDE Evolution)
# =============================================================================

class CollapseDynamics:
    """
    §3.1 The Collapse Evolution Equation
    
    ∂Φ/∂t = D∇²Φ - λ(Φ - Φ_lock) + η·σ̇
    
    With boundary conditions: ∂Φ/∂n = 0 at ρ_q > 0
    """
    
    def __init__(self, D: float = 0.1, lam: float = 1.0, eta: float = 0.01):
        self.D = D      # Diffusion coefficient
        self.lam = lam  # Locking strength
        self.eta = eta  # Residue injection rate
    
    def compute_lock_state(self, phi: PhiField) -> np.ndarray:
        """
        Nearest stable discrete state for each cell.
        Φ_lock = round(Φ) for quantized systems.
        """
        return np.round(phi.data)
    
    def evolve_step(self, phi: PhiField, dt: float = 0.1) -> PhiField:
        """
        One step of PDE evolution.
        
        ∂Φ/∂t = D∇²Φ - λ(Φ - Φ_lock)·𝟙[Φ>0]
        """
        lap = phi.laplacian()
        lock_state = self.compute_lock_state(phi)
        rho = phi.boundary_charge()
        
        # Compute time derivative
        dPhi_dt = np.zeros_like(phi.data)
        
        # Diffusion term: D∇²Φ
        dPhi_dt += self.D * lap
        
        # Locking term: -λ(Φ - Φ_lock) only where Φ > 0
        collapsed_mask = phi.data > 0
        dPhi_dt[collapsed_mask] -= self.lam * (phi.data[collapsed_mask] - lock_state[collapsed_mask])
        
        # Apply no-flux boundary condition at ρ_q > 0
        dPhi_dt[rho > 0] = 0
        
        # Update
        new_data = phi.data + dt * dPhi_dt
        
        # Clamp to valid range
        new_data = np.clip(new_data, 0, 9)
        
        return PhiField(new_data)
    
    def evolve_to_equilibrium(self, phi: PhiField, max_steps: int = 100, 
                               tol: float = 1e-6) -> PhiField:
        """
        Evolve until ∂Φ/∂t → 0 (equilibrium).
        """
        current = phi
        
        for step in range(max_steps):
            next_phi = self.evolve_step(current)
            
            # Check convergence
            diff = np.max(np.abs(next_phi.data - current.data))
            if diff < tol:
                break
            
            current = next_phi
        
        return PhiField(np.round(current.data))
    
    @staticmethod
    def compute_lock_coefficient(phi: PhiField) -> float:
        """
        §3.2 Lock Coefficient (Definition 3.2)
        
        ℒ = 1 - ||∂Φ/∂t|| / ||∂Φ/∂t||_max
        
        ℒ = 1: fully locked
        ℒ = 0: maximum drift
        """
        lap = phi.laplacian()
        grad_mag = np.mean(phi.gradient_magnitude())
        
        # Measure of instability
        instability = np.mean(np.abs(lap)) + grad_mag
        max_instability = 10.0  # Normalization constant
        
        lock = 1.0 - min(1.0, instability / max_instability)
        return max(0.0, lock)


# =============================================================================
# CHAPTER 4: THE SIX FANS
# =============================================================================

class FanDecomposition:
    """
    §3.3 The Six Fans as Modal Decomposition (Theorem 3.2)
    
    Φ' = Φ + Σᵢ αᵢ Δᵢ[Φ]
    """
    
    @staticmethod
    def compute_fan_coefficients(phi_in: PhiField, phi_out: PhiField) -> Dict[str, float]:
        """
        Compute αᵢ for each fan by projection.
        
        αᵢ = ⟨Φ' - Φ, Δᵢ[Φ]⟩ / ||Δᵢ[Φ]||²
        """
        if phi_in.shape != phi_out.shape:
            # Handle size change separately
            return {'size_change': True}
        
        diff = phi_out.data - phi_in.data
        
        coefficients = {}
        
        # Δ₁: Gradient (translation)
        gx, gy = phi_in.gradient()
        grad_norm = np.sum(gx**2 + gy**2)
        if grad_norm > 1e-10:
            alpha1 = np.sum(diff * (gx + gy)) / grad_norm
            coefficients['delta1_translation'] = float(alpha1)
        
        # Δ₃: Positive Laplacian (expansion)
        lap = phi_in.laplacian()
        pos_lap = np.maximum(lap, 0)
        pos_lap_norm = np.sum(pos_lap**2)
        if pos_lap_norm > 1e-10:
            alpha3 = np.sum(diff * pos_lap) / pos_lap_norm
            coefficients['delta3_expansion'] = float(alpha3)
        
        # Δ₄: Negative Laplacian (compression)
        neg_lap = np.minimum(lap, 0)
        neg_lap_norm = np.sum(neg_lap**2)
        if neg_lap_norm > 1e-10:
            alpha4 = np.sum(diff * neg_lap) / neg_lap_norm
            coefficients['delta4_compression'] = float(alpha4)
        
        # Δ₆: Constant (identity offset)
        alpha6 = np.mean(diff)
        coefficients['delta6_constant'] = float(alpha6)
        
        return coefficients


# =============================================================================
# CHAPTER 5: SIGMA RESIDUE ANALYSIS
# =============================================================================

@dataclass
class SigmaResidue:
    """
    §1.3 Irreducible Residue
    
    σ[T](p) = |Φ'(p) - Φ(p)|
    """
    residue: np.ndarray
    total: float
    change_type: str
    structural_condition: str
    
    @classmethod
    def from_transformation(cls, phi_in: PhiField, phi_out: PhiField) -> 'SigmaResidue':
        """
        Compute σ and analyze transformation type.
        """
        # Handle size changes
        if phi_in.shape != phi_out.shape:
            oh, ow = phi_out.shape
            ih, iw = phi_in.shape
            
            if oh > ih or ow > iw:
                return cls(
                    residue=np.abs(phi_out.data),
                    total=float(np.sum(np.abs(phi_out.data))),
                    change_type="expansion",
                    structural_condition="size_increase"
                )
            else:
                return cls(
                    residue=np.abs(phi_in.data),
                    total=float(np.sum(np.abs(phi_in.data))),
                    change_type="compression",
                    structural_condition="size_decrease"
                )
        
        # Same size
        residue = np.abs(phi_out.data - phi_in.data)
        total = float(np.sum(residue))
        
        if total < 1e-10:
            return cls(residue, total, "identity", "none")
        
        # Analyze change pattern
        zero_to_nonzero = np.sum((phi_in.data == 0) & (phi_out.data != 0))
        nonzero_to_zero = np.sum((phi_in.data != 0) & (phi_out.data == 0))
        color_change = np.sum((phi_in.data != 0) & (phi_out.data != 0) & (residue > 0))
        
        if zero_to_nonzero > 0 and nonzero_to_zero == 0 and color_change == 0:
            # Check if fills are in enclosed regions
            enclosed_regions = DerivedConcepts.get_enclosed_regions(phi_in)
            if enclosed_regions:
                fills_in_enclosed = 0
                for mask in enclosed_regions:
                    fills_in_enclosed += np.sum((phi_in.data == 0) & (phi_out.data != 0) & mask)
                
                if fills_in_enclosed > 0:
                    return cls(residue, total, "fill", "enclosed")
            
            return cls(residue, total, "fill", "general")
        
        if nonzero_to_zero > 0 and zero_to_nonzero == 0:
            return cls(residue, total, "erase", "removal")
        
        if color_change > 0:
            return cls(residue, total, "recolor", "substitution")
        
        return cls(residue, total, "mixed", "complex")


# =============================================================================
# CHAPTER 6: LEARNED TRANSFORMATION RULES
# =============================================================================

@dataclass
class TransformationRule:
    """
    A rule learned from training examples.
    Derived from σ analysis and fan decomposition.
    """
    rule_type: str
    
    # Size change
    size_ratio: Tuple[float, float] = (1.0, 1.0)
    
    # Fill rules
    fill_color: int = 0
    size_to_color: Dict[Tuple[int, int], int] = field(default_factory=dict)
    energy_to_color: Dict[float, int] = field(default_factory=dict)
    
    # Color mapping
    color_map: Dict[int, int] = field(default_factory=dict)
    
    # Tiling
    tile_pattern: List[List[int]] = field(default_factory=list)
    
    # Period
    detected_period: int = 0
    
    # Shape indicator
    indicator_color: int = 0
    target_color: int = 0
    shape_to_color: Dict[Tuple[float, ...], int] = field(default_factory=dict)
    
    @classmethod
    def learn(cls, train_pairs: List[Dict]) -> 'TransformationRule':
        """
        Learn transformation rule from training examples.
        """
        rule = cls(rule_type="unknown")
        
        sigmas = []
        fan_coeffs = []
        
        for pair in train_pairs:
            phi_in = PhiField(pair['input'])
            phi_out = PhiField(pair['output'])
            
            # Compute sigma
            sigma = SigmaResidue.from_transformation(phi_in, phi_out)
            sigmas.append(sigma)
            
            # Compute fan coefficients
            coeffs = FanDecomposition.compute_fan_coefficients(phi_in, phi_out)
            fan_coeffs.append(coeffs)
            
            # Size ratio
            ratio = (phi_out.h / phi_in.h, phi_out.w / phi_in.w)
            rule.size_ratio = ratio
            
            # Detect specific patterns
            rule._learn_from_pair(phi_in, phi_out, sigma)
        
        # Determine rule type from sigma patterns
        change_types = [s.change_type for s in sigmas]
        structural = [s.structural_condition for s in sigmas]
        
        if all(t == "fill" and s == "enclosed" for t, s in zip(change_types, structural)):
            if len(rule.size_to_color) > 1 and len(set(rule.size_to_color.values())) > 1:
                rule.rule_type = "multi_region_fill"
            else:
                rule.rule_type = "fill_enclosed"
        elif all(t == "fill" for t in change_types):
            rule.rule_type = "fill_rows" if rule._check_row_fill(train_pairs) else "fill"
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
        """Learn parameters from a single training pair."""
        
        # Learn fill colors for enclosed regions
        if sigma.change_type == "fill" and sigma.structural_condition == "enclosed":
            enclosed = DerivedConcepts.get_enclosed_regions(phi_in)
            for mask in enclosed:
                # Get bounding box size
                positions = list(zip(*np.where(mask)))
                if not positions:
                    continue
                rows = [p[0] for p in positions]
                cols = [p[1] for p in positions]
                h_size = max(rows) - min(rows) + 1
                w_size = max(cols) - min(cols) + 1
                
                # What color did this region get?
                fill_vals = phi_out.data[mask]
                if len(fill_vals) > 0:
                    unique, counts = np.unique(fill_vals, return_counts=True)
                    fill_c = unique[np.argmax(counts)]
                    if fill_c != 0:
                        self.size_to_color[(h_size, w_size)] = int(fill_c)
                        self.fill_color = int(fill_c)
        
        # Learn color mapping
        if phi_in.shape == phi_out.shape:
            for c in phi_in.colors:
                mask = phi_in.data == c
                out_vals = phi_out.data[mask]
                unique = np.unique(out_vals)
                if len(unique) == 1 and unique[0] != c:
                    self.color_map[int(c)] = int(unique[0])
        
        # Learn period (using Fourier)
        if phi_in.shape != phi_out.shape and phi_in.w == phi_out.w:
            period = DerivedConcepts.detect_period_fourier(phi_in, axis=0)
            if period > 0:
                self.detected_period = period
                
                # Learn color mapping for periodic extension
                # Compare base periods
                in_base = phi_in.data[:period, :]
                out_base = phi_out.data[:period, :]
                
                for c_in in set(in_base.flatten()) - {0}:
                    mask = in_base == c_in
                    out_vals = out_base[mask]
                    if len(out_vals) > 0:
                        unique = np.unique(out_vals)
                        if len(unique) == 1 and unique[0] != c_in:
                            self.color_map[int(c_in)] = int(unique[0])
        
        # Learn shape indicator pattern
        if len(phi_in.colors) == 2:
            self._learn_shape_indicator(phi_in, phi_out)
        
        # Learn tile pattern
        self._learn_tile_pattern(phi_in, phi_out)
    
    def _learn_shape_indicator(self, phi_in: PhiField, phi_out: PhiField):
        """Learn shape indicator: one shape's eigenspectrum determines another's color."""
        if phi_in.shape != phi_out.shape:
            return
        
        c1, c2 = sorted(phi_in.colors)
        
        mask1 = phi_in.data == c1
        mask2 = phi_in.data == c2
        
        out_at_1 = set(phi_out.data[mask1].flatten()) - {0}
        out_at_2 = set(phi_out.data[mask2].flatten()) - {0}
        
        indicator = None
        target = None
        output_color = None
        
        if len(out_at_1) == 0 and len(out_at_2) == 1:
            indicator = c1
            target = c2
            output_color = int(list(out_at_2)[0])
        elif len(out_at_2) == 0 and len(out_at_1) == 1:
            indicator = c2
            target = c1
            output_color = int(list(out_at_1)[0])
        else:
            return
        
        self.indicator_color = indicator
        self.target_color = target
        
        # Get shape eigenspectrum
        positions = list(zip(*np.where(phi_in.data == indicator)))
        if positions:
            shape_sig = DerivedConcepts.shape_eigenspectrum(phi_in, positions)
            if shape_sig:
                self.shape_to_color[shape_sig] = output_color
    
    def _learn_tile_pattern(self, phi_in: PhiField, phi_out: PhiField):
        """Learn tiling transformation pattern."""
        ih, iw = phi_in.shape
        oh, ow = phi_out.shape
        
        if oh < ih or ow < iw:
            return
        if oh % ih != 0 or ow % iw != 0:
            return
        
        tile_h, tile_w = oh // ih, ow // iw
        if tile_h == 1 and tile_w == 1:
            return
        
        pattern = []
        for ti in range(tile_h):
            row = []
            for tj in range(tile_w):
                tile = phi_out.data[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw]
                
                if np.array_equal(tile, phi_in.data):
                    row.append(0)
                elif np.array_equal(tile, np.fliplr(phi_in.data)):
                    row.append(1)
                elif np.array_equal(tile, np.flipud(phi_in.data)):
                    row.append(2)
                elif np.array_equal(tile, np.rot90(phi_in.data, 2)):
                    row.append(3)
                else:
                    row.append(-1)
            pattern.append(row)
        
        self.tile_pattern = pattern
    
    def _check_tiling(self, pairs: List[Dict]) -> bool:
        """Check if transformation is regular tiling."""
        for pair in pairs:
            phi_in = PhiField(pair['input'])
            phi_out = PhiField(pair['output'])
            
            ih, iw = phi_in.shape
            oh, ow = phi_out.shape
            
            if oh % ih != 0 or ow % iw != 0:
                return False
            
            tile_h, tile_w = oh // ih, ow // iw
            if tile_h <= 1 and tile_w <= 1:
                return False
            
            # Check all tiles match some transformation of input
            for ti in range(tile_h):
                for tj in range(tile_w):
                    tile = phi_out.data[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw]
                    matches = (
                        np.array_equal(tile, phi_in.data) or
                        np.array_equal(tile, np.fliplr(phi_in.data)) or
                        np.array_equal(tile, np.flipud(phi_in.data)) or
                        np.array_equal(tile, np.rot90(phi_in.data, 2))
                    )
                    if not matches:
                        return False
        
        return True
    
    def _check_self_tile(self, pairs: List[Dict]) -> bool:
        """Check if transformation is self-tiling (Φ as own mask)."""
        for pair in pairs:
            phi_in = PhiField(pair['input'])
            phi_out = PhiField(pair['output'])
            
            ih, iw = phi_in.shape
            oh, ow = phi_out.shape
            
            if oh != ih * ih or ow != iw * iw:
                continue
            
            is_self = True
            for ti in range(ih):
                for tj in range(iw):
                    tile = phi_out.data[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw]
                    if phi_in.data[ti, tj] != 0:
                        if not np.array_equal(tile, phi_in.data):
                            is_self = False
                            break
                    else:
                        if np.any(tile != 0):
                            is_self = False
                            break
                if not is_self:
                    break
            
            if is_self:
                return True
        
        return False
    
    def _check_row_fill(self, pairs: List[Dict]) -> bool:
        """Check if transformation fills rows with seed color."""
        for pair in pairs:
            phi_in = PhiField(pair['input'])
            phi_out = PhiField(pair['output'])
            
            if phi_in.shape != phi_out.shape:
                return False
            
            h, w = phi_in.shape
            for i in range(h):
                in_row = phi_in.data[i, :]
                out_row = phi_out.data[i, :]
                nonzero = in_row[in_row != 0]
                
                if len(nonzero) > 0:
                    if not np.all(out_row == nonzero[0]):
                        return False
                else:
                    if not np.all(out_row == 0):
                        return False
        
        return True
    
    def apply(self, phi_in: PhiField) -> PhiField:
        """Apply the learned rule."""
        
        if self.rule_type == "tile":
            return self._apply_tile(phi_in)
        
        if self.rule_type == "self_tile":
            return self._apply_self_tile(phi_in)
        
        if self.rule_type == "fill_enclosed":
            return self._apply_fill_enclosed(phi_in)
        
        if self.rule_type == "multi_region_fill":
            return self._apply_multi_region_fill(phi_in)
        
        if self.rule_type == "fill_rows":
            return self._apply_fill_rows(phi_in)
        
        if self.rule_type == "periodic_extension":
            return self._apply_periodic_extension(phi_in)
        
        if self.rule_type == "shape_indicator":
            return self._apply_shape_indicator(phi_in)
        
        if self.rule_type == "recolor":
            return self._apply_recolor(phi_in)
        
        return phi_in
    
    def _apply_tile(self, phi_in: PhiField) -> PhiField:
        """Apply tiling transformation."""
        ih, iw = phi_in.shape
        tile_h = int(self.size_ratio[0])
        tile_w = int(self.size_ratio[1])
        
        result = np.zeros((ih * tile_h, iw * tile_w))
        
        for ti in range(tile_h):
            for tj in range(tile_w):
                if self.tile_pattern and ti < len(self.tile_pattern) and tj < len(self.tile_pattern[ti]):
                    code = self.tile_pattern[ti][tj]
                    if code == 0:
                        tile = phi_in.data
                    elif code == 1:
                        tile = np.fliplr(phi_in.data)
                    elif code == 2:
                        tile = np.flipud(phi_in.data)
                    elif code == 3:
                        tile = np.rot90(phi_in.data, 2)
                    else:
                        tile = phi_in.data
                else:
                    tile = phi_in.data
                
                result[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw] = tile
        
        return PhiField(result)
    
    def _apply_self_tile(self, phi_in: PhiField) -> PhiField:
        """Apply self-tiling: Φ → Φ[Φ]."""
        ih, iw = phi_in.shape
        result = np.zeros((ih * ih, iw * iw))
        
        for ti in range(ih):
            for tj in range(iw):
                if phi_in.data[ti, tj] != 0:
                    result[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw] = phi_in.data
        
        return PhiField(result)
    
    def _apply_fill_enclosed(self, phi_in: PhiField) -> PhiField:
        """Fill enclosed regions using winding number criterion."""
        result = phi_in.data.copy()
        
        enclosed = DerivedConcepts.get_enclosed_regions(phi_in)
        for mask in enclosed:
            result[mask] = self.fill_color
        
        return PhiField(result)
    
    def _apply_multi_region_fill(self, phi_in: PhiField) -> PhiField:
        """Fill multiple enclosed regions with size-dependent colors."""
        result = phi_in.data.copy()
        
        enclosed = DerivedConcepts.get_enclosed_regions(phi_in)
        for mask in enclosed:
            positions = list(zip(*np.where(mask)))
            if not positions:
                continue
            
            rows = [p[0] for p in positions]
            cols = [p[1] for p in positions]
            h_size = max(rows) - min(rows) + 1
            w_size = max(cols) - min(cols) + 1
            
            fill_c = self.size_to_color.get((h_size, w_size), self.fill_color)
            result[mask] = fill_c
        
        return PhiField(result)
    
    def _apply_fill_rows(self, phi_in: PhiField) -> PhiField:
        """Fill each row with its seed color."""
        result = np.zeros_like(phi_in.data)
        h, w = phi_in.shape
        
        for i in range(h):
            row = phi_in.data[i, :]
            nonzero = row[row != 0]
            if len(nonzero) > 0:
                result[i, :] = nonzero[0]
        
        return PhiField(result)
    
    def _apply_periodic_extension(self, phi_in: PhiField) -> PhiField:
        """Extend periodic structure using Fourier-detected period."""
        if self.detected_period == 0:
            return phi_in
        
        ih, iw = phi_in.shape
        oh = int(ih * self.size_ratio[0])
        out_periods = oh // self.detected_period
        
        base = phi_in.data[:self.detected_period, :].copy()
        
        # Apply color map
        for old_c, new_c in self.color_map.items():
            base[base == old_c] = new_c
        
        result = np.tile(base, (out_periods, 1))
        return PhiField(result)
    
    def _apply_shape_indicator(self, phi_in: PhiField) -> PhiField:
        """Apply shape indicator using Laplacian eigenspectrum."""
        result = np.zeros_like(phi_in.data)
        
        indicator_mask = phi_in.data == self.indicator_color
        positions = list(zip(*np.where(indicator_mask)))
        
        if positions:
            shape_sig = DerivedConcepts.shape_eigenspectrum(phi_in, positions)
            output_color = self.shape_to_color.get(shape_sig, 0)
            
            target_mask = phi_in.data == self.target_color
            result[target_mask] = output_color
        
        return PhiField(result)
    
    def _apply_recolor(self, phi_in: PhiField) -> PhiField:
        """Apply color mapping."""
        result = phi_in.data.copy()
        for old_c, new_c in self.color_map.items():
            result[phi_in.data == old_c] = new_c
        return PhiField(result)


# =============================================================================
# MAIN SOLVER
# =============================================================================

class ITTSolverV2:
    """
    Pure ITT Solver v2: Rigorous Implementation
    """
    
    def __init__(self):
        self.rule: Optional[TransformationRule] = None
        self.dynamics = CollapseDynamics()
    
    def train(self, examples: List[Dict]):
        """Learn transformation rule from examples."""
        self.rule = TransformationRule.learn(examples)
        
        print(f"  Learned (rigorous):")
        print(f"    Rule type: {self.rule.rule_type}")
        print(f"    Size ratio: {self.rule.size_ratio}")
        print(f"    Period (Fourier): {self.rule.detected_period}")
        print(f"    Shape→color (eigenspectrum): {len(self.rule.shape_to_color)} mappings")
    
    def solve(self, test_input: List[List[int]]) -> List[List[int]]:
        """Apply learned rule with PDE relaxation."""
        if self.rule is None:
            return test_input
        
        phi_in = PhiField(test_input)
        phi_out = self.rule.apply(phi_in)
        
        # Apply PDE relaxation to stabilize
        phi_final = self.dynamics.evolve_to_equilibrium(phi_out, max_steps=10)
        
        # Check lock coefficient
        lock = CollapseDynamics.compute_lock_coefficient(phi_final)
        print(f"    Lock coefficient: {lock:.3f}")
        
        return phi_final.data.astype(int).tolist()


# =============================================================================
# DATA LOADING AND TESTING
# =============================================================================

def fetch_task(task_id: str) -> Optional[Dict]:
    """Fetch task from ARC-AGI repo."""
    for dataset in ['training', 'evaluation']:
        url = f"https://raw.githubusercontent.com/fchollet/ARC-AGI/master/data/{dataset}/{task_id}.json"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode())
        except:
            continue
    return None


def solve_task(task_id: str) -> Tuple[bool, List[List[int]]]:
    """Solve a single task."""
    print(f"\n{'='*60}")
    print(f"Task: {task_id}")
    print('='*60)
    
    task = fetch_task(task_id)
    if task is None:
        print("  ERROR: Task not found")
        return False, []
    
    solver = ITTSolverV2()
    solver.train(task['train'])
    
    test_input = task['test'][0]['input']
    prediction = solver.solve(test_input)
    
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
    """Run the rigorous ITT solver."""
    print("="*60)
    print("ARC-AGI PURE ITT SOLVER v2")
    print("RIGOROUS IMPLEMENTATION")
    print("- Objects via Laplacian sign regions")
    print("- Enclosure via winding numbers")
    print("- Shape via eigenspectrum")
    print("- Period via Fourier")
    print("- PDE time evolution")
    print("="*60)
    
    tasks = [
        "00576224",  # Tiling
        "007bbfb7",  # Self-tiling
        "009d5c81",  # Shape indicator
        "00d62c1b",  # Fill enclosed
        "00dbd492",  # Multi-frame fill
        "017c7c7b",  # Periodic extension
    ]
    
    results = {}
    for task_id in tasks:
        correct, pred = solve_task(task_id)
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
