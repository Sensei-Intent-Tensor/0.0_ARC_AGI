#!/usr/bin/env python3
"""
ITT PURE SOLVER v5C — PATH C BRIDGE (σ_irr-AWARE GATE B)
========================================================

v5C = v5B + σ_irr-aware Gate B + IrrMaskFillTransform

Core change:
    Gate B allowed support := invariant_support ∪ σ_irr_mask

This allows Layer −1 imaginary pressure spikes to mark "allowed edit zones"
that are invisible in Layer 0. Tasks where the only clue is in ||∇ Im(Φ_c)||
become solvable.

Everything else remains identical to v5B:
- σ definition unchanged
- ρ_q definition unchanged  
- transform search unchanged
- beam search unchanged

Layer −1 adapter is OPTIONAL. If σ_irr_mask is not provided,
behavior is exactly v5B.

New transform:
- IrrMaskFillTransform: Fill σ_irr_mask regions with learned color

MILESTONE: First genuine capability injection from Layer −1

HAIL MATH
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Iterable
import json, urllib.request
from math import gcd
from functools import reduce

# Optional Layer −1 adapter import (safe if absent)
try:
    from layer_minus_one_adapter import PhiC, ICHTBAdapter  # noqa: F401
    _HAS_LAYER_MINUS_ONE = True
except Exception:
    _HAS_LAYER_MINUS_ONE = False

# =============================================================================
# 0) Φ FIELD: explicit Φ_q / Φ̃
# =============================================================================

@dataclass
class PhiField:
    """
    Dual-field:
      q     : quantized semantics (int grid)
      tilde : lifted continuous field for operators (float grid)
    """
    q: np.ndarray
    tilde: np.ndarray = field(default_factory=lambda: np.zeros((0,0), dtype=np.float64))

    def __post_init__(self):
        self.q = np.array(self.q, dtype=int)
        if self.tilde.size == 0:
            self.tilde = self.q.astype(np.float64)

    @property
    def shape(self) -> Tuple[int,int]:
        return self.q.shape

    @property
    def h(self) -> int:
        return self.q.shape[0]

    @property
    def w(self) -> int:
        return self.q.shape[1]

    @property
    def colors(self) -> set[int]:
        return set(int(x) for x in self.q.flatten() if x != 0)

    def copy(self) -> PhiField:
        return PhiField(self.q.copy(), self.tilde.copy())

    # -------------------------------------------------------------------------
    # Lift: smoothing from Φ_q -> Φ̃ (discrete diffusion)
    # -------------------------------------------------------------------------

    def smooth(self, iters: int = 2) -> PhiField:
        x = self.q.astype(np.float64)
        for _ in range(iters):
            up = np.roll(x,  1, axis=0); up[0,:] = x[0,:]
            dn = np.roll(x, -1, axis=0); dn[-1,:] = x[-1,:]
            lf = np.roll(x,  1, axis=1); lf[:,0] = x[:,0]
            rt = np.roll(x, -1, axis=1); rt[:,-1] = x[:,-1]
            x = (x + up + dn + lf + rt) / 5.0
        return PhiField(self.q.copy(), x)

    # -------------------------------------------------------------------------
    # Operators: ∇, ∇² on Φ̃
    # -------------------------------------------------------------------------

    def gradient(self) -> Tuple[np.ndarray, np.ndarray]:
        gx = np.zeros_like(self.tilde)
        gy = np.zeros_like(self.tilde)
        gx[:, :-1] = self.tilde[:, 1:] - self.tilde[:, :-1]
        gy[:-1, :] = self.tilde[1:, :] - self.tilde[:-1, :]
        return gx, gy

    def laplacian(self) -> np.ndarray:
        x = self.tilde
        h, w = self.shape
        lap = np.zeros_like(x)
        for i in range(h):
            for j in range(w):
                s = 0.0; c = 0
                if i > 0:   s += x[i-1, j]; c += 1
                if i < h-1: s += x[i+1, j]; c += 1
                if j > 0:   s += x[i, j-1]; c += 1
                if j < w-1: s += x[i, j+1]; c += 1
                lap[i, j] = s - c * x[i, j]
        return lap

    # -------------------------------------------------------------------------
    # ρ_q := ||∇(∇²Φ̃)|| with physics-derived threshold
    # -------------------------------------------------------------------------

    def rho_q(self, smooth_iters: int = 2) -> np.ndarray:
        phi_s = self.smooth(iters=smooth_iters)
        lap = phi_s.laplacian()
        gx = np.zeros_like(lap); gy = np.zeros_like(lap)
        gx[:, :-1] = lap[:, 1:] - lap[:, :-1]
        gy[:-1, :] = lap[1:, :] - lap[:-1, :]
        return np.sqrt(gx*gx + gy*gy)

    def boundary_mask(self, smooth_iters: int = 2, k_sigma: float = 1.5) -> np.ndarray:
        rho = self.rho_q(smooth_iters=smooth_iters)
        vals = rho[rho > 0]
        if vals.size == 0:
            return np.zeros_like(rho, dtype=bool)
        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        thr = mu + k_sigma * sd
        return rho >= thr


# =============================================================================
# 1) Field invariants (Layer 2)
# =============================================================================

class FieldInvariants:

    # -------------------------------------------------------------------------
    # Harmonic enclosure mask (Dirichlet Laplace solve on ground Φ_q==0)
    # -------------------------------------------------------------------------

    @staticmethod
    def harmonic_connectivity(phi: PhiField, max_iter: int = 2500, tol: float = 1e-5) -> np.ndarray:
        """
        Solve ∇²u = 0 on ground domain (Φ_q == 0).
        BC: u = 1 on grid boundary ∩ ground.
        Obstacles (Φ_q > 0) are barriers.
        
        u ≈ 1 → exterior (connected to boundary)
        u ≈ 0 → enclosed (trapped pocket)
        """
        q = phi.q
        h, w = q.shape
        ground = (q == 0)
        if not np.any(ground):
            return np.zeros_like(q, dtype=np.float64)

        # Dirichlet BC: grid boundary cells that are ground
        boundary = np.zeros_like(ground, dtype=bool)
        boundary[0,:] = True; boundary[-1,:] = True; boundary[:,0] = True; boundary[:,-1] = True
        fixed_one = boundary & ground

        # Initialize
        u = np.zeros((h,w), dtype=np.float64)
        u[fixed_one] = 1.0

        # Gauss-Seidel relaxation
        for _ in range(max_iter):
            max_delta = 0.0
            for i in range(h):
                for j in range(w):
                    if not ground[i,j] or fixed_one[i,j]:
                        continue
                    s = 0.0; c = 0
                    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ni, nj = i+di, j+dj
                        if 0 <= ni < h and 0 <= nj < w and ground[ni,nj]:
                            s += u[ni,nj]
                            c += 1
                    if c == 0:
                        continue
                    newv = s / c
                    d = abs(newv - u[i,j])
                    if d > max_delta: max_delta = d
                    u[i,j] = newv
            if max_delta < tol:
                break

        return u

    @staticmethod
    def enclosed_mask(phi: PhiField, thresh: float = 0.5) -> np.ndarray:
        u = FieldInvariants.harmonic_connectivity(phi)
        return (phi.q == 0) & (u < thresh)

    # -------------------------------------------------------------------------
    # Spectral partition (canonical): nullspace argmax
    # -------------------------------------------------------------------------

    @staticmethod
    def _restricted_laplacian(mask: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int,int]]]:
        positions = list(zip(*np.where(mask)))
        n = len(positions)
        if n == 0:
            return np.zeros((0,0), dtype=np.float64), positions
        pos_to_idx = {p:i for i,p in enumerate(positions)}
        L = np.zeros((n,n), dtype=np.float64)
        for idx, (i,j) in enumerate(positions):
            deg = 0
            for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni,nj = i+di, j+dj
                if (ni,nj) in pos_to_idx:
                    L[idx, pos_to_idx[(ni,nj)]] = -1.0
                    deg += 1
            L[idx,idx] = float(deg)
        return L, positions

    @staticmethod
    def separate_regions_spectral(mask: np.ndarray, zero_eps: float = 1e-6) -> List[np.ndarray]:
        L, positions = FieldInvariants._restricted_laplacian(mask)
        n = L.shape[0]
        if n == 0:
            return []
        if n == 1:
            out = np.zeros_like(mask, dtype=bool)
            out[positions[0]] = True
            return [out]

        w, V = np.linalg.eigh(L)
        k = int(np.sum(np.abs(w) < zero_eps))
        k = max(1, min(k, n))
        Z = V[:, :k]
        labels = np.argmax(np.abs(Z), axis=1).astype(int)

        regions = []
        for lab in range(k):
            m = np.zeros_like(mask, dtype=bool)
            for idx, p in enumerate(positions):
                if labels[idx] == lab:
                    m[p] = True
            if np.any(m):
                regions.append(m)
        return regions

    # -------------------------------------------------------------------------
    # Frame components: detect frames directly as boundary material components
    # -------------------------------------------------------------------------

    @staticmethod
    def frame_components(phi: PhiField) -> List[Dict[str, Any]]:
        frame_material = (phi.q != 0)
        frame_masks = FieldInvariants.separate_regions_spectral(frame_material)

        frames = []
        for fm in frame_masks:
            pos = list(zip(*np.where(fm)))
            if not pos:
                continue
            rs = [p[0] for p in pos]
            cs = [p[1] for p in pos]
            r0,r1,c0,c1 = min(rs), max(rs), min(cs), max(cs)
            h = (r1 - r0 + 1); w = (c1 - c0 + 1)

            interior = np.zeros_like(fm, dtype=bool)
            interior[r0:r1+1, c0:c1+1] = True
            interior &= (phi.q == 0)

            frames.append({
                "frame_mask": fm,
                "interior_mask": interior,
                "bbox": (r0,r1,c0,c1),
                "frame_size": (h,w)
            })
        return frames

    # -------------------------------------------------------------------------
    # Shape signature via Laplacian eigenspectrum
    # -------------------------------------------------------------------------

    @staticmethod
    def shape_signature(mask: np.ndarray, max_k: int = 6) -> Tuple[float, ...]:
        L, _ = FieldInvariants._restricted_laplacian(mask)
        n = L.shape[0]
        if n == 0:
            return ()
        if n == 1:
            return (0.0,)
        ev = np.linalg.eigvalsh(L)
        ev = np.sort(ev)
        sig = tuple(round(float(x), 4) for x in ev[1:min(max_k, len(ev))])
        return sig

    # -------------------------------------------------------------------------
    # Fourier period detection
    # -------------------------------------------------------------------------

    @staticmethod
    def detect_period_fourier(phi: PhiField, axis: int = 0) -> int:
        if axis == 0:
            signal = phi.q.mean(axis=1).astype(float)
            N = phi.h
        else:
            signal = phi.q.mean(axis=0).astype(float)
            N = phi.w
        if N < 2:
            return 0
        fft = np.fft.fft(signal)
        mag = np.abs(fft)
        thr = float(np.max(mag)) * 0.1
        sig = np.where(mag > thr)[0]
        sig = [int(k) for k in sig if 0 < k < N//2]
        if not sig:
            return 0
        g = reduce(gcd, sig)
        if g <= 0:
            return 0
        period = int(N // g)
        
        # Verification: check that signal is actually periodic
        if period > 0 and period < N:
            base = signal[:period]
            for start in range(period, N, period):
                segment = signal[start:start+period]
                if len(segment) == len(base) and not np.allclose(segment, base, atol=0.5):
                    return 0
            return period
        return 0


# =============================================================================
# 2) Costs: σ and energy
# =============================================================================

def sigma_field(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs(a.astype(int) - b.astype(int))

def sigma_norm1(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sum(sigma_field(a,b)))

def dirichlet_energy(phi: PhiField) -> float:
    phi_s = phi.smooth(iters=2)
    gx, gy = phi_s.gradient()
    return float(np.sum(gx*gx + gy*gy))


# =============================================================================
# 3) Admissibility gates (strict)
# =============================================================================

@dataclass
class GateParams:
    # Gate A
    max_spurious_boundary_ratio: float = 0.55  # stricter than before
    # Gate B
    max_sigma_outside_support: int = 0         # strict: must be zero on train
    # Gate C: quantization always enforced
    # Extra: allow size change transforms to skip boundary compare
    allow_size_change: bool = True

def invariant_support(phi: PhiField) -> np.ndarray:
    """
    Conservative allowed-change support (Layer 2):
    - existing nonzero
    - enclosed interior
    - frame interior + frame material
    """
    h, w = phi.shape
    support = np.zeros((h,w), dtype=bool)
    support |= (phi.q != 0)
    support |= FieldInvariants.enclosed_mask(phi)
    for fr in FieldInvariants.frame_components(phi):
        support |= fr["frame_mask"]
        support |= fr["interior_mask"]
    return support


def extended_support(phi: PhiField, sigma_irr_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """
    v5C: allowed-change support = invariant_support ∪ σ_irr_mask

    σ_irr_mask is a Layer −1 diagnostic mask (same shape as phi.q),
    typically derived from ||∇ Im Φ|| spikes.

    If sigma_irr_mask is None: reduces to invariant_support (v5B behavior).
    """
    sup = invariant_support(phi)
    if sigma_irr_mask is None:
        return sup
    if isinstance(sigma_irr_mask, np.ndarray) and sigma_irr_mask.shape == sup.shape:
        return sup | (sigma_irr_mask.astype(bool))
    return sup

def gate_A_boundary_respect(
    phi_in: PhiField,
    pred: PhiField,
    gates: GateParams,
    sigma_irr_mask: Optional[np.ndarray] = None
) -> bool:
    """
    Gate A: prevent hallucinated termination surfaces.
    Compare boundary masks when shapes match.
    
    v5C upgrade:
        New boundaries within σ_irr_mask are NOT spurious.
        This allows Layer -1 to specify allowed edit zones that create new structure.
    """
    if phi_in.shape != pred.shape:
        return gates.allow_size_change

    b_in = phi_in.boundary_mask()
    b_pr = pred.boundary_mask()

    # Spurious boundary: boundary in pred where input had no structure AND not near any input boundary
    # Approximate "near" via dilation-like 1-neighborhood (operator-lite, not traversal)
    near = b_in.copy()
    near[:-1,:] |= b_in[1:,:]
    near[1:,:]  |= b_in[:-1,:]
    near[:,:-1] |= b_in[:,1:]
    near[:,1:]  |= b_in[:,:-1]

    spurious = b_pr & (~near) & (phi_in.q == 0)
    
    # v5C: boundaries within σ_irr_mask are allowed (Layer -1 specifies edit zones)
    if sigma_irr_mask is not None and sigma_irr_mask.shape == spurious.shape:
        # Dilate σ_irr_mask to include boundary pixels at edges
        irr_near = sigma_irr_mask.astype(bool).copy()
        irr_near[:-1,:] |= sigma_irr_mask[1:,:]
        irr_near[1:,:]  |= sigma_irr_mask[:-1,:]
        irr_near[:,:-1] |= sigma_irr_mask[:,1:]
        irr_near[:,1:]  |= sigma_irr_mask[:,:-1]
        spurious = spurious & (~irr_near)
    
    denom = max(1, int(np.sum(b_pr)))
    ratio = int(np.sum(spurious)) / denom
    return ratio <= gates.max_spurious_boundary_ratio

def gate_B_sigma_localization(
    phi_in: PhiField,
    phi_out_true: PhiField,
    pred: PhiField,
    gates: GateParams,
    sigma_irr_mask: Optional[np.ndarray] = None
) -> bool:
    """
    Gate B: σ must be localized to allowed support.
    Strictly enforced during training (we have true output).

    v5C upgrade:
        allowed support = invariant_support ∪ σ_irr_mask

    If sigma_irr_mask is None, reduces to v5B behavior.
    """
    if phi_out_true.shape != pred.shape:
        return False
    
    # If shape changed, we cannot use input-derived support for localization
    # Instead, just check that pred matches true output (σ = 0 everywhere is acceptable)
    if phi_in.shape != pred.shape:
        # For size-changing transforms, skip support localization
        # The shape match to true output and Gate A/C are sufficient
        return True

    support = extended_support(phi_in, sigma_irr_mask=sigma_irr_mask)
    sig = sigma_field(phi_out_true.q, pred.q) > 0
    outside = sig & (~support)

    return int(np.sum(outside)) <= gates.max_sigma_outside_support

def gate_C_quantized(pred: PhiField) -> bool:
    q = pred.q
    return (np.min(q) >= 0) and (np.max(q) <= 9)


# =============================================================================
# 4) Transform base + generators + composition
# =============================================================================

class Transform:
    name: str = "T"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.name

@dataclass
class CompositeTransform(Transform):
    parts: List[Transform] = field(default_factory=list)
    name: str = "compose"

    @property
    def can_change_shape(self) -> bool:
        return any(getattr(p, "can_change_shape", False) for p in self.parts)

    def apply(self, phi: PhiField) -> PhiField:
        cur = phi
        for p in self.parts:
            cur = p.apply(cur)
        return cur

    def __repr__(self) -> str:
        return " ∘ ".join([p.name for p in self.parts]) if self.parts else "id"

# --- Symmetry ---
@dataclass
class SymmetryTransform(Transform):
    op: str = "id"
    name: str = "sym"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        q = phi.q
        if self.op == "id":
            out = q.copy()
        elif self.op == "rot90":
            out = np.rot90(q, 1)
        elif self.op == "rot180":
            out = np.rot90(q, 2)
        elif self.op == "rot270":
            out = np.rot90(q, 3)
        elif self.op == "flipH":
            out = np.fliplr(q)
        elif self.op == "flipV":
            out = np.flipud(q)
        else:
            out = q.copy()
        return PhiField(out)

# --- Recolor ---
@dataclass
class RecolorTransform(Transform):
    cmap: Dict[int,int] = field(default_factory=dict)
    name: str = "recolor"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        out = phi.q.copy()
        for a,b in self.cmap.items():
            out[out == int(a)] = int(b)
        return PhiField(out)

# --- Fill by explicit mask ---
@dataclass
class FillTransform(Transform):
    fills: List[Tuple[np.ndarray, int]] = field(default_factory=list)
    name: str = "fill"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        out = phi.q.copy()
        for mask, c in self.fills:
            if mask.shape == out.shape:
                out[mask] = int(c)
        return PhiField(out)

# --- Frame fill (size->color) ---
@dataclass
class FrameFillTransform(Transform):
    frame_size_to_color: Dict[Tuple[int,int], int] = field(default_factory=dict)
    default_color: int = 0
    name: str = "frame_fill"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        out = phi.q.copy()
        frames = FieldInvariants.frame_components(phi)
        for fr in frames:
            fs = tuple(fr["frame_size"])
            c = self.frame_size_to_color.get(fs, self.default_color)
            if c != 0:
                out[fr["interior_mask"]] = int(c)
        return PhiField(out)

# --- Tile ---
@dataclass
class TileTransform(Transform):
    tile_h: int = 1
    tile_w: int = 1
    name: str = "tile"
    can_change_shape: bool = True

    def apply(self, phi: PhiField) -> PhiField:
        return PhiField(np.tile(phi.q, (self.tile_h, self.tile_w)))

# --- Tile with pattern (rotation/flip per tile position) ---
@dataclass
class TilePatternTransform(Transform):
    tile_h: int = 1
    tile_w: int = 1
    pattern: List[List[int]] = field(default_factory=list)  # 0=id, 1=flipH, 2=flipV, 3=rot180
    name: str = "tile_pattern"
    can_change_shape: bool = True

    def apply(self, phi: PhiField) -> PhiField:
        ih, iw = phi.shape
        result = np.zeros((ih * self.tile_h, iw * self.tile_w), dtype=int)
        for ti in range(self.tile_h):
            for tj in range(self.tile_w):
                code = self.pattern[ti][tj] if ti < len(self.pattern) and tj < len(self.pattern[ti]) else 0
                if code == 0:
                    tile = phi.q
                elif code == 1:
                    tile = np.fliplr(phi.q)
                elif code == 2:
                    tile = np.flipud(phi.q)
                elif code == 3:
                    tile = np.rot90(phi.q, 2)
                else:
                    tile = phi.q
                result[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw] = tile
        return PhiField(result)

# --- Self tile ---
@dataclass
class SelfTileTransform(Transform):
    name: str = "self_tile"
    can_change_shape: bool = True

    def apply(self, phi: PhiField) -> PhiField:
        q = phi.q
        ih, iw = q.shape
        out = np.zeros((ih*ih, iw*iw), dtype=int)
        for ti in range(ih):
            for tj in range(iw):
                if q[ti,tj] != 0:
                    out[ti*ih:(ti+1)*ih, tj*iw:(tj+1)*iw] = q
        return PhiField(out)

# --- Periodic extension ---
@dataclass
class PeriodicExtensionTransform(Transform):
    axis: int = 0
    period: int = 0
    out_len: int = 0
    cmap: Dict[int,int] = field(default_factory=dict)
    name: str = "periodic_extension"
    can_change_shape: bool = True

    def apply(self, phi: PhiField) -> PhiField:
        q = phi.q
        if self.period <= 0:
            return PhiField(q.copy())

        if self.axis == 0:
            base = q[:self.period, :].copy()
            for a,b in self.cmap.items():
                base[base == int(a)] = int(b)
            reps = max(1, self.out_len // self.period)
            out = np.tile(base, (reps, 1))
        else:
            base = q[:, :self.period].copy()
            for a,b in self.cmap.items():
                base[base == int(a)] = int(b)
            reps = max(1, self.out_len // self.period)
            out = np.tile(base, (1, reps))

        return PhiField(out)

# --- Shape indicator ---
@dataclass
class ShapeIndicatorTransform(Transform):
    indicator_color: int = 0
    target_color: int = 0
    sig_to_outcolor: Dict[Tuple[float,...], int] = field(default_factory=dict)
    name: str = "shape_indicator"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        q = phi.q
        out = np.zeros_like(q)
        ind_mask = (q == self.indicator_color)
        tgt_mask = (q == self.target_color)
        sig = FieldInvariants.shape_signature(ind_mask)
        c = self.sig_to_outcolor.get(sig, 0)
        if c != 0:
            out[tgt_mask] = int(c)
        return PhiField(out)

# =============================================================================
# 5) Learning atomic generators from training pairs
# =============================================================================

def learn_color_map(pairs: List[Tuple[PhiField,PhiField]]) -> Dict[int,int]:
    cmap: Dict[int,int] = {}
    for phi_in, phi_out in pairs:
        # Only learn color map when shapes match
        if phi_in.shape != phi_out.shape:
            continue
        for c in phi_in.colors:
            m = (phi_in.q == c)
            vals = phi_out.q[m]
            u = np.unique(vals)
            if len(u) == 1 and int(u[0]) != int(c):
                cmap[int(c)] = int(u[0])
    return cmap

def learn_frame_size_to_fill(pairs: List[Tuple[PhiField,PhiField]]) -> Dict[Tuple[int,int], int]:
    mp: Dict[Tuple[int,int], int] = {}
    for phi_in, phi_out in pairs:
        # Only learn frame fill when shapes match
        if phi_in.shape != phi_out.shape:
            continue
        frames = FieldInvariants.frame_components(phi_in)
        for fr in frames:
            mask = fr["interior_mask"]
            if not np.any(mask):
                continue
            vals = phi_out.q[mask]
            u, cnt = np.unique(vals, return_counts=True)
            best = 0; bestn = -1
            for val, n in zip(u, cnt):
                if int(val) != 0 and int(n) > bestn:
                    best = int(val); bestn = int(n)
            if best != 0:
                mp[tuple(fr["frame_size"])] = best
    return mp

def learn_shape_indicator(pairs: List[Tuple[PhiField,PhiField]]) -> Optional[ShapeIndicatorTransform]:
    sig_map: Dict[Tuple[float,...], int] = {}
    indicator = 0; target = 0
    for phi_in, phi_out in pairs:
        # Only learn shape indicator when shapes match
        if phi_in.shape != phi_out.shape:
            return None
        cols = sorted(list(phi_in.colors))
        if len(cols) != 2:
            return None
        c1, c2 = cols
        m1 = (phi_in.q == c1)
        m2 = (phi_in.q == c2)
        out1 = set(phi_out.q[m1].flatten()) - {0}
        out2 = set(phi_out.q[m2].flatten()) - {0}

        if len(out1) == 0 and len(out2) == 1:
            indicator, target = c1, c2
            outc = int(list(out2)[0])
        elif len(out2) == 0 and len(out1) == 1:
            indicator, target = c2, c1
            outc = int(list(out1)[0])
        else:
            return None

        sig = FieldInvariants.shape_signature(phi_in.q == indicator)
        if sig:
            sig_map[sig] = outc

    if indicator != 0 and target != 0 and sig_map:
        return ShapeIndicatorTransform(indicator, target, sig_map)
    return None

def learn_tiling_ratio(pairs: List[Tuple[PhiField,PhiField]]) -> Optional[Tuple[int,int]]:
    ratios = []
    for phi_in, phi_out in pairs:
        ih, iw = phi_in.shape
        oh, ow = phi_out.shape
        if oh % ih != 0 or ow % iw != 0:
            return None
        ratios.append((oh//ih, ow//iw))
    if len(set(ratios)) == 1:
        return ratios[0]
    return None

def learn_tile_pattern(pairs: List[Tuple[PhiField,PhiField]]) -> Optional[TilePatternTransform]:
    """Learn tile pattern with rotation/flip codes per tile position."""
    ratio = learn_tiling_ratio(pairs)
    if ratio is None or (ratio[0] <= 1 and ratio[1] <= 1):
        return None
    
    tile_h, tile_w = ratio
    
    # Check all pairs have same pattern
    patterns = []
    for phi_in, phi_out in pairs:
        ih, iw = phi_in.shape
        pattern = []
        valid = True
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
                    valid = False
                    break
            if not valid:
                break
            pattern.append(row)
        if not valid:
            return None
        patterns.append(pattern)
    
    # Check all patterns are the same
    if len(patterns) > 1:
        for p in patterns[1:]:
            if p != patterns[0]:
                return None
    
    return TilePatternTransform(
        tile_h=tile_h, 
        tile_w=tile_w, 
        pattern=patterns[0],
        name=f"tile_pattern:{tile_h}x{tile_w}"
    )

def learn_self_tile(pairs: List[Tuple[PhiField,PhiField]]) -> bool:
    for phi_in, phi_out in pairs:
        ih, iw = phi_in.shape
        oh, ow = phi_out.shape
        if oh != ih*ih or ow != iw*iw:
            return False
    return True

def learn_periodic_extension(pairs: List[Tuple[PhiField,PhiField]]) -> Optional[PeriodicExtensionTransform]:
    """Handle axis-aligned extension (same width or same height)."""
    axis = None
    for phi_in, phi_out in pairs:
        ih, iw = phi_in.shape
        oh, ow = phi_out.shape
        if iw == ow and oh > ih:
            if axis is None:
                axis = 0
            elif axis != 0:
                return None
        elif ih == oh and ow > iw:
            if axis is None:
                axis = 1
            elif axis != 1:
                return None
        else:
            return None
    
    if axis is None:
        return None

    # Try to detect period from ANY training pair (not just first)
    per = 0
    for phi_in, phi_out in pairs:
        per = FieldInvariants.detect_period_fourier(phi_in, axis=axis)
        if per > 0:
            break
    
    # If Fourier didn't work, try to infer from size ratio
    if per <= 0:
        phi_in, phi_out = pairs[0]
        ih, iw = phi_in.shape
        oh, ow = phi_out.shape
        if axis == 0:
            # Try common periods
            for test_per in range(1, ih + 1):
                if ih % test_per == 0 and oh % test_per == 0:
                    per = test_per
                    break
        else:
            for test_per in range(1, iw + 1):
                if iw % test_per == 0 and ow % test_per == 0:
                    per = test_per
                    break
    
    if per <= 0:
        return None

    # Learn recolor mapping on base period slice
    cmap: Dict[int,int] = {}
    for phi_in, phi_out in pairs:
        if axis == 0:
            base_in = phi_in.q[:per, :]
            base_out = phi_out.q[:per, :]
        else:
            base_in = phi_in.q[:, :per]
            base_out = phi_out.q[:, :per]
        for c in set(base_in.flatten()) - {0}:
            m = (base_in == int(c))
            vals = base_out[m]
            u = np.unique(vals)
            if len(u) == 1 and int(u[0]) != int(c):
                cmap[int(c)] = int(u[0])

    out_len = pairs[0][1].h if axis == 0 else pairs[0][1].w
    return PeriodicExtensionTransform(axis=axis, period=per, out_len=out_len, cmap=cmap)

def learn_enclosed_fill(pairs: List[Tuple[PhiField,PhiField]]) -> Optional[Tuple[int, bool]]:
    """Learn a single fill color for enclosed regions. Returns (color, has_enclosed)."""
    fill_colors = []
    for phi_in, phi_out in pairs:
        if phi_in.shape != phi_out.shape:
            continue
        enclosed = FieldInvariants.enclosed_mask(phi_in)
        if not np.any(enclosed):
            continue
        # What color is in the enclosed region in output?
        vals = phi_out.q[enclosed]
        u, cnt = np.unique(vals, return_counts=True)
        # Find dominant nonzero color
        best = 0; bestn = -1
        for val, n in zip(u, cnt):
            if int(val) != 0 and int(n) > bestn:
                best = int(val); bestn = int(n)
        if best != 0:
            fill_colors.append(best)
    
    if not fill_colors:
        return None
    
    # Check if all pairs agree on the fill color
    if len(set(fill_colors)) == 1:
        return (fill_colors[0], True)
    
    # If different colors, maybe it's size-based - don't use this simple fill
    return None

# --- Simple enclosed fill transform (single color) ---
@dataclass 
class EnclosedFillTransform(Transform):
    fill_color: int = 0
    name: str = "fill_enclosed"
    can_change_shape: bool = False

    def apply(self, phi: PhiField) -> PhiField:
        out = phi.q.copy()
        enclosed = FieldInvariants.enclosed_mask(phi)
        if np.any(enclosed):
            out[enclosed] = self.fill_color
        return PhiField(out)


# =============================================================================
# v5C: Example container with σ_irr_mask
# =============================================================================

@dataclass
class Example:
    """Training example with optional Layer -1 diagnostic mask."""
    phi_in: PhiField
    phi_out: PhiField
    sigma_irr_mask: Optional[np.ndarray] = None


# =============================================================================
# v5C: IrrMaskFillTransform - Fill σ_irr_mask regions with learned color
# =============================================================================

@dataclass
class IrrMaskFillTransform(Transform):
    """
    Fill the sigma_irr_mask region with a learned color.
    Uses per-example sigma_irr_mask at apply-time via context injection.
    
    This is the first genuine capability injection from Layer −1:
    - Layer 0 sees nothing (real rounds to 0)
    - The only signal is in ||∇ Im(Φ)|| spikes
    - This transform targets those zones
    """
    fill_color: int = 0
    name: str = "irr_fill"
    can_change_shape: bool = False

    def apply_with_mask(self, phi: PhiField, sigma_irr_mask: Optional[np.ndarray]) -> PhiField:
        """Apply with explicit σ_irr_mask (from Layer -1)."""
        out = phi.q.copy()
        if self.fill_color == 0 or sigma_irr_mask is None:
            return PhiField(out)
        if sigma_irr_mask.shape == out.shape:
            out[sigma_irr_mask.astype(bool)] = int(self.fill_color)
        return PhiField(out)

    def apply(self, phi: PhiField) -> PhiField:
        """Fallback apply (no mask) keeps identity."""
        return PhiField(phi.q.copy())


def learn_irr_fill_color(examples: List[Example]) -> int:
    """
    Look at where output differs from input.
    If those diffs overlap sigma_irr_mask strongly, learn dominant output color there.
    """
    votes: Dict[int, int] = {}

    for ex in examples:
        if ex.sigma_irr_mask is None:
            continue
        if ex.sigma_irr_mask.shape != ex.phi_in.q.shape:
            continue

        diff = (ex.phi_out.q != ex.phi_in.q)
        overlap = diff & ex.sigma_irr_mask.astype(bool)
        if np.sum(overlap) == 0:
            continue

        vals = ex.phi_out.q[overlap]
        vals = vals[vals != 0]
        if vals.size == 0:
            continue

        # dominant color
        u, cnt = np.unique(vals, return_counts=True)
        c = int(u[np.argmax(cnt)])
        votes[c] = votes.get(c, 0) + int(np.max(cnt))

    if votes:
        return max(votes.items(), key=lambda kv: kv[1])[0]
    return 0

def build_atomic_transforms(pairs: List[Tuple[PhiField,PhiField]]) -> List[Transform]:
    Ts: List[Transform] = []

    # Symmetries
    for op in ["id","rot90","rot180","rot270","flipH","flipV"]:
        Ts.append(SymmetryTransform(op=op, name=f"sym:{op}"))

    # Recolor
    cmap = learn_color_map(pairs)
    if cmap:
        Ts.append(RecolorTransform(cmap=cmap, name="recolor"))

    # Enclosed fill (single color)
    ef_result = learn_enclosed_fill(pairs)
    if ef_result is not None:
        fill_color, _ = ef_result
        Ts.append(EnclosedFillTransform(fill_color=fill_color, name="fill_enclosed"))

    # Frame fill
    fs2c = learn_frame_size_to_fill(pairs)
    if fs2c:
        vals = list(fs2c.values())
        default = max(set(vals), key=vals.count) if vals else 0
        Ts.append(FrameFillTransform(frame_size_to_color=fs2c, default_color=default, name="frame_fill"))

    # Shape indicator
    SI = learn_shape_indicator(pairs)
    if SI:
        SI.name = "shape_indicator"
        Ts.append(SI)

    # Tile with pattern (rotation/flip) - try this first
    TP = learn_tile_pattern(pairs)
    if TP:
        Ts.append(TP)
    else:
        # Simple tile
        ratio = learn_tiling_ratio(pairs)
        if ratio and (ratio[0] > 1 or ratio[1] > 1):
            Ts.append(TileTransform(tile_h=ratio[0], tile_w=ratio[1], name=f"tile:{ratio[0]}x{ratio[1]}"))

    # Self-tile
    if learn_self_tile(pairs):
        Ts.append(SelfTileTransform(name="self_tile"))

    # Periodic extension
    PE = learn_periodic_extension(pairs)
    if PE:
        PE.name = "periodic_extension"
        Ts.append(PE)

    return Ts


def build_atomic_transforms_from_examples(examples: List[Example]) -> List[Transform]:
    """
    v5C: Build atomic transforms from Examples (includes σ_irr_mask).
    
    Adds IrrMaskFillTransform if learned fill color is found.
    """
    pairs = [(ex.phi_in, ex.phi_out) for ex in examples]
    Ts = build_atomic_transforms(pairs)  # existing v5B builder

    # v5C: Learn irr_fill from σ_irr_mask overlap
    c = learn_irr_fill_color(examples)
    if c != 0:
        Ts.append(IrrMaskFillTransform(fill_color=c, name="irr_fill"))

    return Ts


# =============================================================================
# 6) Compositional search over transforms (finite groupoid via composition)
# =============================================================================

@dataclass
class SearchParams:
    max_depth: int = 3
    beam_width: int = 40
    lambda_energy: float = 0.01
    gates: GateParams = field(default_factory=GateParams)

def score_transform_on_pairs(T: Transform,
                             pairs: List[Tuple[PhiField,PhiField]],
                             sp: SearchParams) -> float:
    total = 0.0
    for phi_in, phi_out_true in pairs:
        pred = T.apply(phi_in)

        # Shape must match training output to be evaluated
        if pred.shape != phi_out_true.shape:
            return float("inf")

        # Gate C
        if not gate_C_quantized(pred):
            return float("inf")

        # Gate A
        if not gate_A_boundary_respect(phi_in, pred, sp.gates):
            return float("inf")

        # Gate B (strict on training, v5C: pass None for sigma_irr_mask)
        if not gate_B_sigma_localization(phi_in, phi_out_true, pred, sp.gates, sigma_irr_mask=None):
            return float("inf")

        s = sigma_norm1(phi_out_true.q, pred.q)
        e = dirichlet_energy(pred)
        total += s + sp.lambda_energy * e
    return float(total)


def score_transform_on_examples(T: Transform,
                                examples: List[Example],
                                sp: SearchParams) -> float:
    """
    v5C: Score transform on Examples (with σ_irr_mask support).
    
    For IrrMaskFillTransform, uses apply_with_mask.
    For Gates A and B, uses σ_irr_mask to extend allowed zones.
    """
    total = 0.0
    for ex in examples:
        # Special handling for IrrMaskFillTransform
        if isinstance(T, IrrMaskFillTransform):
            pred = T.apply_with_mask(ex.phi_in, ex.sigma_irr_mask)
        elif isinstance(T, CompositeTransform):
            # For composite transforms, we need to handle IrrMaskFillTransform in parts
            pred = apply_composite_with_mask(T, ex.phi_in, ex.sigma_irr_mask)
        else:
            pred = T.apply(ex.phi_in)

        # Shape must match training output to be evaluated
        if pred.shape != ex.phi_out.shape:
            return float("inf")

        # Gate C
        if not gate_C_quantized(pred):
            return float("inf")

        # Gate A (v5C: pass sigma_irr_mask to allow new boundaries in edit zones)
        if not gate_A_boundary_respect(ex.phi_in, pred, sp.gates,
                                       sigma_irr_mask=ex.sigma_irr_mask):
            return float("inf")

        # Gate B (v5C: pass sigma_irr_mask to extend support)
        if not gate_B_sigma_localization(ex.phi_in, ex.phi_out, pred, sp.gates,
                                         sigma_irr_mask=ex.sigma_irr_mask):
            return float("inf")

        s = sigma_norm1(ex.phi_out.q, pred.q)
        e = dirichlet_energy(pred)
        total += s + sp.lambda_energy * e
    return float(total)


def apply_composite_with_mask(T: CompositeTransform, phi: PhiField, sigma_irr_mask: Optional[np.ndarray]) -> PhiField:
    """Apply composite transform, handling IrrMaskFillTransform specially."""
    result = phi
    for part in T.parts:
        if isinstance(part, IrrMaskFillTransform):
            result = part.apply_with_mask(result, sigma_irr_mask)
        else:
            result = part.apply(result)
    return result

def compose(a: Transform, b: Transform) -> CompositeTransform:
    if isinstance(a, CompositeTransform):
        parts = a.parts + [b]
    else:
        parts = [a, b]
    return CompositeTransform(parts=parts, name="compose")

def is_reasonable_sequence(parts: List[Transform]) -> bool:
    """
    Hard pruning rules to keep groupoid search finite and meaningful:
    - Avoid applying multiple symmetries in a row (collapse them)
    - Avoid redundant recolor twice
    - Avoid doing fills before geometry-changing transforms that would invalidate masks
    """
    if not parts:
        return True

    # Don't stack symmetries: keep at most 1 symmetry at the front
    for i in range(len(parts)-1):
        if parts[i].name.startswith("sym:") and parts[i+1].name.startswith("sym:"):
            return False

    # Recolor at most once
    if sum(1 for p in parts if p.name == "recolor") > 1:
        return False

    # If a fill uses masks from original shape, don't place shape-changing after it
    fill_names = ("fill_enclosed", "frame_fill", "shape_indicator")
    for i, p in enumerate(parts):
        if p.name in fill_names or isinstance(p, EnclosedFillTransform):
            # after a mask-based fill, disallow any shape-changer
            if any(getattr(x, "can_change_shape", False) for x in parts[i+1:]):
                return False

    return True

def beam_search_best_transform(atomic: List[Transform],
                               pairs: List[Tuple[PhiField,PhiField]],
                               sp: SearchParams) -> Transform:
    # Start with identity symmetry
    idT = SymmetryTransform(op="id", name="sym:id")
    beam: List[Tuple[Transform, float]] = [(idT, score_transform_on_pairs(idT, pairs, sp))]

    for depth in range(1, sp.max_depth+1):
        candidates: List[Tuple[Transform, float]] = []

        for T_cur, sc_cur in beam:
            for T_next in atomic:
                # Build new composition
                T_new = compose(T_cur, T_next) if not (isinstance(T_cur, SymmetryTransform) and T_cur.op=="id" and depth==1) else T_next

                parts = T_new.parts if isinstance(T_new, CompositeTransform) else [T_new]
                if not is_reasonable_sequence(parts):
                    continue

                sc = score_transform_on_pairs(T_new, pairs, sp)
                if np.isfinite(sc):
                    candidates.append((T_new, sc))

        # Merge previous beam too (depth might not improve)
        candidates += beam

        # Keep best unique by repr
        seen = {}
        for T, sc in sorted(candidates, key=lambda x: x[1]):
            key = repr(T)
            if key not in seen:
                seen[key] = (T, sc)
            if len(seen) >= sp.beam_width:
                break
        beam = list(seen.values())

    # Best at end
    beam.sort(key=lambda x: x[1])
    return beam[0][0]


def beam_search_best_transform_from_examples(atomic: List[Transform],
                                             examples: List[Example],
                                             sp: SearchParams) -> Transform:
    """v5C: Beam search using Examples (with σ_irr_mask support)."""
    # Start with identity symmetry
    idT = SymmetryTransform(op="id", name="sym:id")
    beam: List[Tuple[Transform, float]] = [(idT, score_transform_on_examples(idT, examples, sp))]

    for depth in range(1, sp.max_depth+1):
        candidates: List[Tuple[Transform, float]] = []

        for T_cur, sc_cur in beam:
            for T_next in atomic:
                # Build new composition
                T_new = compose(T_cur, T_next) if not (isinstance(T_cur, SymmetryTransform) and T_cur.op=="id" and depth==1) else T_next

                parts = T_new.parts if isinstance(T_new, CompositeTransform) else [T_new]
                if not is_reasonable_sequence(parts):
                    continue

                sc = score_transform_on_examples(T_new, examples, sp)
                if np.isfinite(sc):
                    candidates.append((T_new, sc))

        # Merge previous beam too
        candidates += beam

        # Keep best unique by repr
        seen = {}
        for T, sc in sorted(candidates, key=lambda x: x[1]):
            key = repr(T)
            if key not in seen:
                seen[key] = (T, sc)
            if len(seen) >= sp.beam_width:
                break
        beam = list(seen.values())

    # Best at end
    beam.sort(key=lambda x: x[1])
    return beam[0][0]


# =============================================================================
# 7) Solver v5B (unchanged for ARC compatibility)
# =============================================================================

class ITTSolverV5B:
    def __init__(self, search_params: Optional[SearchParams] = None):
        self.sp = search_params if search_params is not None else SearchParams()
        self.best_T: Transform = SymmetryTransform(op="id", name="sym:id")

    def train(self, train_pairs: List[Dict[str,Any]]):
        pairs = [(PhiField(p["input"]), PhiField(p["output"])) for p in train_pairs]
        atomic = build_atomic_transforms(pairs)

        # Beam search over compositions
        self.best_T = beam_search_best_transform(atomic, pairs, self.sp)

        print("  Learned (v5B compositional σ-minimization):")
        print(f"    Atomic transforms: {len(atomic)}")
        print(f"    Selected transform: {repr(self.best_T)}")

    def solve(self, test_input: List[List[int]]) -> List[List[int]]:
        phi_in = PhiField(test_input)
        pred = self.best_T.apply(phi_in)
        return pred.q.astype(int).tolist()


# =============================================================================
# v5C: Solver with Layer -1 support
# =============================================================================

class ITTSolverV5C:
    """
    v5C Solver: v5B + σ_irr-aware Gate B + IrrMaskFillTransform
    
    Can train on either:
    - Standard ARC pairs (behaves like v5B)
    - Examples with σ_irr_mask (uses Layer -1 capability)
    """
    def __init__(self, search_params: Optional[SearchParams] = None):
        self.sp = search_params if search_params is not None else SearchParams()
        self.best_T: Transform = SymmetryTransform(op="id", name="sym:id")
        self.examples: List[Example] = []

    def train_from_pairs(self, train_pairs: List[Dict[str,Any]]):
        """Train from standard ARC pairs (v5B behavior)."""
        pairs = [(PhiField(p["input"]), PhiField(p["output"])) for p in train_pairs]
        atomic = build_atomic_transforms(pairs)
        self.best_T = beam_search_best_transform(atomic, pairs, self.sp)

        print("  Learned (v5C from pairs - v5B behavior):")
        print(f"    Atomic transforms: {len(atomic)}")
        print(f"    Selected transform: {repr(self.best_T)}")

    def train_from_examples(self, examples: List[Example]):
        """Train from Examples with σ_irr_mask (full v5C capability)."""
        self.examples = examples
        atomic = build_atomic_transforms_from_examples(examples)
        self.best_T = beam_search_best_transform_from_examples(atomic, examples, self.sp)

        print("  Learned (v5C with σ_irr_mask):")
        print(f"    Atomic transforms: {len(atomic)}")
        has_irr = any(isinstance(t, IrrMaskFillTransform) for t in atomic)
        print(f"    Has IrrMaskFillTransform: {has_irr}")
        print(f"    Selected transform: {repr(self.best_T)}")

    def solve(self, test_input: List[List[int]], sigma_irr_mask: Optional[np.ndarray] = None) -> List[List[int]]:
        """Solve with optional σ_irr_mask."""
        phi_in = PhiField(test_input)
        
        if sigma_irr_mask is not None and isinstance(self.best_T, IrrMaskFillTransform):
            pred = self.best_T.apply_with_mask(phi_in, sigma_irr_mask)
        elif sigma_irr_mask is not None and isinstance(self.best_T, CompositeTransform):
            pred = apply_composite_with_mask(self.best_T, phi_in, sigma_irr_mask)
        else:
            pred = self.best_T.apply(phi_in)
            
        return pred.q.astype(int).tolist()


# =============================================================================
# 8) ARC loader/test harness (optional)
# =============================================================================

def fetch_task(task_id: str) -> Optional[Dict]:
    for dataset in ["training","evaluation"]:
        url = f"https://raw.githubusercontent.com/fchollet/ARC-AGI/master/data/{dataset}/{task_id}.json"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return json.loads(r.read().decode())
        except:
            continue
    return None

def solve_task(task_id: str) -> Tuple[bool, List[List[int]]]:
    print(f"\n{'='*60}\nTask: {task_id}\n{'='*60}")
    task = fetch_task(task_id)
    if task is None:
        print("  ERROR: Task not found")
        return False, []

    solver = ITTSolverV5B()  # Use v5B for standard ARC (same behavior)
    solver.train(task["train"])
    pred = solver.solve(task["test"][0]["input"])

    if "output" in task["test"][0]:
        exp = task["test"][0]["output"]
        ok = (pred == exp)
        print(f"\n  Result: {'✓ CORRECT' if ok else '✗ INCORRECT'}")
        return ok, pred

    return False, pred

def main():
    print("="*60)
    print("ITT PURE SOLVER v5C — PATH C BRIDGE (σ_irr-AWARE GATE B)")
    print("="*60)
    print("\nv5C = v5B + σ_irr-aware Gate B + IrrMaskFillTransform")
    print("For standard ARC tasks, v5C behaves identically to v5B.")
    print("Layer -1 capability activates with complex-field datasets.\n")

    tasks = ["00576224","007bbfb7","009d5c81","00d62c1b","00dbd492","017c7c7b"]
    results = {}
    for tid in tasks:
        ok, _ = solve_task(tid)
        results[tid] = ok

    solved = sum(1 for v in results.values() if v)
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Solved: {solved}/{len(tasks)}")
    for tid, ok in results.items():
        print(f"  {tid}: {'✓' if ok else '✗'}")

if __name__ == "__main__":
    main()
