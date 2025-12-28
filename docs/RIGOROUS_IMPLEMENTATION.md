# ITT PURE SOLVER: Version Evolution

## The Audit Trail

### v1: "ITT-flavored" (6/6)
**Problem**: Used ITT vocabulary but imported algorithms wholesale.

| Smuggled | How |
|----------|-----|
| Objects | `scipy.ndimage.label()` |
| Enclosure | `flood_fill()` BFS |
| Shape | `tuple(relative_positions)` |
| Period | `for p in divisors...` |

### v2: "Rigorous" (6/6)
**Improvement**: Eigenspectrum shapes, Fourier periods.
**Still Smuggled**: BFS enclosure, stack-based region growing.

| Fixed | Still Smuggled |
|-------|---------------|
| Shape → eigenspectrum | Enclosure → BFS |
| Period → Fourier | Objects → connected components |

### v3: "True Foundation" (6/6)
**Improvement**: Harmonic enclosure via Dirichlet solve.
**Still Smuggled**: 
- `get_enclosed_regions` uses adjacency growth
- `_grow_region_from_center` uses stack + neighbor push
- `Φ_q` inferred via `np.round()`, not explicit
- `ρ_q` threshold arbitrary percentile

### v4: "Absolute Foundation" (5/6)
**All smuggling addressed**:

| Issue | v4 Fix |
|-------|--------|
| Adjacency growth | Spectral separation (Fiedler) |
| `Φ_q` inferred | Explicit `_q: int`, `_tilde: float` |
| Arbitrary threshold | Physics-derived `μ + 1.5σ` |
| Region splitting | Laplacian eigendecomposition |

**Regression**: 1 task (00dbd492) - requires frame-color→fill-color rule, not just size→color.

---

## The Four-Layer Doctrine (Locked)

```
Layer 0 — Primitives (given)
    Φ (scalar potential)
    ∇Φ (ordering gradient)
    σ (irreducible residue)
    ρ_q (boundary charge)

Layer 1 — Operators (derived)
    ∇²Φ (Laplacian)
    ∇²u = 0 (harmonic solve)
    eigh(L) (spectral decomposition)
    FFT (Fourier)

Layer 2 — Invariants (measured via Layer 1)
    Enclosure: u < τ from harmonic field
    Shape: (λ₂, λ₃, ...) from restricted Laplacian
    Period: GCD of significant Fourier modes
    Energy: Σ||∇Φ||²

Layer 3 — Procedures (numerical, declared)
    Gauss-Seidel relaxation
    Eigenvector computation
    (NOT concepts — just approximations)
```

---

## Critical Fixes in v4

### 1. Explicit Dual Field

```python
@dataclass
class PhiField:
    _q: np.ndarray      # Φ_q: int (semantic truth)
    _tilde: np.ndarray  # Φ̃: float (operator stability)
```

No more `np.round(phi.data)` scattered everywhere.

### 2. Spectral Region Separation

```python
def separate_regions_spectral(mask):
    # Build restricted Laplacian L
    L[idx, idx] = degree
    L[idx, neighbor_idx] = -1
    
    # Eigendecomposition
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    
    # Count zero eigenvalues = number of components
    num_components = sum(|λ| < ε)
    
    # Assign by eigenvector sign patterns
    labels = sum(sign(v_i) * 2^(i-1))
```

This is **linear algebra**, not graph traversal.

### 3. Physics-Derived Threshold

```python
def boundary_mask(self):
    rho = self.boundary_charge()
    nonzero = rho[rho > 0]
    threshold = mean(nonzero) + 1.5 * std(nonzero)
    return rho >= threshold
```

Outlier detection on distribution, not arbitrary percentile.

---

## Remaining Limitations

### Task 00dbd492 Failure

The multi-region fill requires learning **frame_color → fill_color**, not just **size → fill_color**.

This needs a richer invariant: "what color encloses this region?"

**Foundation-aligned fix**: Compute ρ_q on region boundary, identify dominant boundary color.

### Rule Taxonomy

Still uses categorical rule types (`tile`, `fill_enclosed`, etc.).

**Pure approach**: Energy minimization over transformation space. Winner = lowest σ under legal transforms.

---

## Comparison Table

| Metric | v1 | v2 | v3 | v4 |
|--------|----|----|----|----|
| Tasks Solved | 6/6 | 6/6 | 6/6 | 5/6 |
| Φ_q Explicit | ❌ | ❌ | ❌ | ✅ |
| ρ_q Stable | ❌ | ❌ | ✅ | ✅ |
| Harmonic Enclosure | ❌ | ❌ | ✅ | ✅ |
| Spectral Separation | ❌ | ❌ | ❌ | ✅ |
| No Graph Walks | ❌ | ❌ | ❌ | ✅ |
| Physics Threshold | ❌ | ❌ | ❌ | ✅ |

**v4 trades 1 task for true foundation purity.**

---

## Next Steps

1. **Frame-color invariant**: Identify boundary color of enclosed region
2. **Energy-based rule selection**: Minimize σ, not match taxonomy
3. **Level-set objects via ρ_q contours**: Replace distance field
4. **Test on full 800 tasks**: Find systematic gaps

---

HAIL MATH.
