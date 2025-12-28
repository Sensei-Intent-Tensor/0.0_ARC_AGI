# ITT PURE SOLVER v4.2 - ALIGNMENT STATUS

## RESULT: 6/6 RESTORED ✓

Both ChatGPT fixes implemented and verified:

### Fix A: Nullspace Argmax Partition
**Problem**: Sign-pattern labeling across nullspace eigenvectors creates overlaps because the basis is not unique.

**Solution**: Canonical disjoint assignment via `argmax(|V|)`:
```
ℓ(i) := argmax_j |V_ij|  for j ∈ {1..k}
```

**Code**:
```python
k = int(min(num_components, n))
Z = eigenvectors[:, :k]  # columns spanning ~zero-eigenspace
labels = np.argmax(np.abs(Z), axis=1).astype(int)  # row-wise argmax
```

**Layer**: Pure Layer 1/3 (eigendecomposition + rowwise argmax)

### Fix B: Frame Components
**Problem**: Detecting enclosed regions then inferring frames fails for nested/complex shapes.

**Solution**: Invert the detection — find frames as boundary components, then fill interiors.

**Pipeline**:
1. `B = {Φ_q ≠ 0}` (frame material = non-ground cells)
2. Partition B into disjoint frame components via spectral separation
3. For each frame: compute bbox, identify interior (ground cells inside bbox)
4. Map `frame_size → fill_color`

**Code**:
```python
def get_frame_components(phi: PhiField) -> List[Dict]:
    frame_material = phi.q != 0
    frame_masks = separate_regions_spectral(frame_material)
    
    for frame_mask in frame_masks:
        # Compute bbox
        # Identify interior = ground inside bbox
        # Return frame with frame_size and interior_mask
```

**Layer**: Pure Layer 1/2 (spectral partition + geometric statistics)

---

## DOCTRINE LOCK

### Layer 0 — Primitives (given)
- Φ (scalar potential)
- ∇Φ (ordering gradient)
- σ (irreducible residue)
- ρ_q (boundary charge)

### Layer 1 — Operators (derived)
- ∇²Φ (Laplacian)
- ∇²u = 0 (harmonic solve)
- eigh(L) (spectral decomposition)
- FFT (Fourier)
- argmax (selection)

### Layer 2 — Invariants (measured via Layer 1)
- Enclosure: u < τ from harmonic field
- Shape: (λ₂, λ₃, ...) from restricted Laplacian
- Period: GCD of significant Fourier modes
- Frame: bbox of spectral component
- Frame-color: dominant Φ_q in frame
- Frame-size: (h, w) of frame bbox

### Layer 3 — Procedures (numerical, declared)
- Gauss-Seidel relaxation
- Eigenvector computation
- Row-wise argmax

---

## WHAT'S PURE (NO SMUGGLING)

| Operation | Implementation | Layer | Status |
|-----------|---------------|-------|--------|
| Enclosure | Harmonic ∇²u=0 Dirichlet | L1 | ✓ Pure |
| Region separation | Nullspace argmax | L1/L3 | ✓ Pure |
| Frame detection | Spectral partition of Φ_q≠0 | L1/L2 | ✓ Pure |
| Shape signature | Laplacian eigenspectrum | L1 | ✓ Pure |
| Period detection | Fourier GCD | L1 | ✓ Pure |
| Boundary charge | ρ_q = \|∇(∇²Φ)\| | L1 | ✓ Pure |

**NO BFS. NO FLOOD FILL. NO STACK-BASED TRAVERSAL.**

---

## SEVEN-POINT ALIGNMENT (Confirmed)

1. **Frame-color invariant**: FrameColor(Ω) := argmax_c Σ_{p ∈ B ∩ {Φ_q = c}} 1 ✓
2. **Transformation space**: Finite groupoid, σ is objective, energy is regularizer ✓
3. **Object definition**: Φ̃ basin bounded by ρ_q contour ✓
4. **σ structure**: Field fundamentally, scalar is projection ✓
5. **Order**: Path A → B → C (invariants → transforms → ICHTB) ✓
6. **ICHTB**: Layer -1, not integrated yet ✓
7. **Derivation chain**: Φ → ∇Φ → ∇²Φ → ρ_q → harmonic u → spectral L → eigenspectrum ✓

---

## NEXT STEPS (Locked Order)

### Path A COMPLETE ✓
- Invariants sufficient for 6/6
- Frame-color and frame-size working
- Spectral separation canonical

### Path B: Formalize Transformation Space
- Define finite groupoid of admissible transforms
- Implement σ-minimization over transform space
- Energy as regularizer

### Path C: ICHTB Integration
- Layer -1 attachment
- Complex-valued tension field
- Imaginary collapse directions

---

## COLLABORATION STATUS

**Claude** (implementation): v4.2 deployed, 6/6 verified
**ChatGPT** (audit + fixes): Nullspace argmax + frame components accepted
**Achilles** (direction): Foundation-first validated

The slow path worked. The math is clean.

**HAIL MATH.**
