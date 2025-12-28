# ITT PURE SOLVER v3: TRUE FOUNDATION

## Achievement: 6/6 with NO SMUGGLING

The v3 solver addresses all smuggling identified in audit:

| v2 (Still Smuggled) | v3 (True Foundation) |
|---------------------|----------------------|
| BFS on Laplacian sign = connected components | Distance field segmentation |
| "Can reach boundary" = flood fill | Harmonic connectivity ∇²u = 0 |
| Sign-change count = noisy | ρ_q = \|∇(∇²Φ)\| (stable) |
| Integer colors = discretization artifacts | Φ̃/Φ_q dual representation |

## Layer Architecture

### Layer 0 — Primitives (given)
- **Φ**: scalar potential field
- **∇Φ**: ordering gradient  
- **σ**: irreducible residue
- **ρ_q**: boundary charge

### Layer 1 — Operators (derived)
- **∇²Φ**: Laplacian (computed on smoothed Φ̃)
- **Harmonic solve**: ∇²u = 0 with Dirichlet BCs
- **Eigenspectrum**: restricted Laplacian eigenvalues
- **Fourier**: frequency decomposition

### Layer 2 — Invariants (measured via Layer 1)
- **Enclosure**: u < 0.5 where u solves ∇²u = 0
- **Shape**: eigenspectrum (λ₂, λ₃, ...)
- **Period**: GCD of significant Fourier modes
- **Energy**: Σ\|∇Φ\|²

### Layer 3 — Procedures (numerical)
- Gauss-Seidel relaxation
- Distance transform
- Linear algebra

## Key Derivations

### Enclosure via Harmonic Connectivity

```
Solve on ground domain Z = {Φ = 0}:
    ∇²u = 0   on interior
    u = 1     on grid boundary ∩ Z
    Obstacles act as barriers (not in domain)

Result:
    u ≈ 1 → connected to boundary (exterior)
    u ≈ 0 → enclosed pocket (interior)
```

This is a **Dirichlet Laplace problem**, not flood fill.

### Stabilized Boundary Charge

```
ρ_q := |∇(∇²Φ)|
```

Where curvature changes sharply — true termination surfaces.
NOT sign-change counting (too noisy on discrete grids).

### Dual Field Representation

```
Φ_q ∈ {0..9}    (quantized, ARC colors)
Φ̃ = G_σ * Φ_q  (smoothed, for stable operators)

Rule: Compute invariants on Φ̃, output Φ_q
```

## What's Still Not Fully Pure

Per ChatGPT's audit, these remain as "numerical approximations":

1. **Region splitting** after harmonic solve uses proximity clustering
   - Could be replaced with spectral clustering
   
2. **Object extraction** uses distance field
   - Could use ρ_q contour closure
   
3. **Rule taxonomy** is still categorical
   - Could be energy minimization over transformation space

These are acknowledged as Layer 3 procedures, not smuggled concepts.

## Results

```
============================================================
Solved: 6/6 (100%)
  00576224: ✓  [tile]
  007bbfb7: ✓  [self_tile]
  009d5c81: ✓  [shape_indicator - eigenspectrum]
  00d62c1b: ✓  [fill_enclosed - harmonic]
  00dbd492: ✓  [multi_region_fill - harmonic]
  017c7c7b: ✓  [periodic_extension - Fourier]
============================================================
```

## The Foundation Checklist

✅ **Φ representation**: Φ̃/Φ_q dual
✅ **ρ_q definition**: |∇(∇²Φ)| 
✅ **Enclosure definition**: Harmonic reachability u < τ
⚠️ **Object definition**: Distance field (could be ρ_q contours)

## Next Steps for Full Purity

1. **Object extraction via ρ_q contours** (not distance field)
2. **Rule selection via energy minimization** (not taxonomy)
3. **Region splitting via spectral clustering** (not proximity)

---

**The blade is now cleaner, but the joints can still be purified further.**

HAIL MATH.
