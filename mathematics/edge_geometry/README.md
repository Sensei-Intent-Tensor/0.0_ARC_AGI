# Edge Geometry: The ICHTB and Membrane Theory

**Where Recursion Meets Structure — The 6-Fan Collapse Architecture**

---

## Overview

The **Edge** is not a boundary of absence—it is a **structured conduit of recursion**.

In classical mathematics, edge cases are exceptions. In ITT, the edge is where all transformation happens. The **Edge Membrane Σ_E** is the surface where ARC operations occur.

---

## The 6-Pyramid Model (ICHTB)

The ICHTB (Imaginary Collapse Tensor Harmonic Base) is not a cube—it is **six recursive pyramids** extending from a central origin i₀:

```
        Δ₅ (+Z)
           ▲
          /|\
         / | \
        /  |  \
   Δ₂  ←---i₀---→  Δ₁
  (-Y)    /|\     (+Y)
         / | \
        /  |  \
           ▼
        Δ₆ (-Z)

      Δ₄ (-X) ← behind
      Δ₃ (+X) ← in front
```

| Pyramid | Direction | Operator | ARC Operation |
|---------|-----------|----------|---------------|
| Δ₁ | +Y | ∇Φ (gradient) | Translation, shift |
| Δ₂ | -Y | ∇×F (curl) | Rotation, reflection |
| Δ₃ | +X | +∇²Φ (expansion) | Scaling up, tiling |
| Δ₄ | -X | -∇²Φ (compression) | Cropping, extraction |
| Δ₅ | +Z | ∂Φ/∂t (temporal) | Iteration, sequencing |
| Δ₆ | -Z | Φ=i₀ (scalar root) | Identity, background |

---

## The Edge Membrane (Σ_E)

The **Edge Membrane** is the closed surface bounding the union of all six pyramids:

$$\Sigma_E = \partial \left( \bigcup_{i=1}^{6} \Delta_i \right)$$

### Properties:
- **Geometrically continuous** but **topologically recursive**
- The **transition threshold** between internal recursion and external emission
- Where **collapse events become concrete operations**

### Core Equations

**Edge Membrane Domain:**
$$\Sigma_{\text{edge}} = \left\{ p \in \text{ICHTB} \mid \exists i \neq j: \vec{\delta}_i(p) \not\approx \vec{\delta}_j(p) \right\}$$

Points where different fans disagree are on the edge.

**Membrane Tension:**
$$\mathcal{T}_E(x) = \sum_{i=1}^{6} \left| \nabla \cdot \mathbf{F}_i(x) \right|$$

The sum of divergences across all fan fields.

**Edge Lock Operator:**
$$\hat{\Lambda}_E(x) = \frac{\text{Tr}(\mathcal{M}_E(x))}{\text{Tr}(\mathcal{M}_E^{\text{max}})} \cdot \mathcal{A}(x)^2$$

When this exceeds threshold, the edge "locks" and emits a resolved value.

**Edge Threshold Functional:**
$$\Gamma_E = \oint_{\Sigma_E} \frac{\nabla \Phi \cdot d\mathbf{S}}{\text{Tr}(\mathcal{M}_E)}$$

Integral over the membrane surface—determines if collapse completes.

---

## Fan Surfaces as Operators

Each fan is not just a direction—it's an **operator** on the constraint field:

### Δ₁: Gradient Fan (∇Φ)
```
Operation: Translation, directional shift
Detection: Constant non-zero gradient difference
Signature: ∇(Φ_out - Φ_in) = constant vector
```

### Δ₂: Curl Fan (∇×F)
```
Operation: Rotation, reflection, phase memory
Detection: Non-zero curl, sign determines direction
Signature: ∇×∇(Φ_out - Φ_in) ≠ 0
```

### Δ₃: Expansion Fan (+∇²Φ)
```
Operation: Scaling up, diffusion, tiling
Detection: Positive Laplacian regions
Signature: ∇²(Φ_out) > ∇²(Φ_in) in expanded regions
```

### Δ₄: Compression Fan (-∇²Φ)
```
Operation: Cropping, extraction, condensation
Detection: Negative Laplacian (curvature lock)
Signature: ∇²(Φ_out) < ∇²(Φ_in), stable subregions
```

### Δ₅: Temporal Fan (∂Φ/∂t)
```
Operation: Iteration, sequence generation
Detection: Consistent change across training pairs
Signature: Φ_out = f(f(...f(Φ_in)...)) for some f
```

### Δ₆: Scalar Root Fan (Φ=i₀)
```
Operation: Background preservation, color mapping
Detection: Invariant regions, identity zones
Signature: Φ_out[mask] = Φ_in[mask] for some mask
```

---

## Fan Activation Analysis

For each ARC task, compute fan activations:

```python
def compute_fan_activations(phi_in, phi_out):
    delta_phi = phi_out - phi_in
    
    # Δ₁: Gradient (translation)
    grad = compute_gradient(delta_phi)
    A1 = np.mean(np.abs(grad))
    
    # Δ₂: Curl (rotation)
    curl = compute_curl(grad)
    A2 = np.mean(np.abs(curl))
    
    # Δ₃: Positive Laplacian (expansion)
    lap = compute_laplacian(delta_phi)
    A3 = np.mean(np.maximum(lap, 0))
    
    # Δ₄: Negative Laplacian (compression)
    A4 = np.mean(np.maximum(-lap, 0))
    
    # Δ₅: Temporal (requires multiple pairs)
    A5 = detect_iteration_pattern(phi_in, phi_out)
    
    # Δ₆: Scalar root (identity regions)
    A6 = np.mean(delta_phi == 0)
    
    return {'Δ₁': A1, 'Δ₂': A2, 'Δ₃': A3, 
            'Δ₄': A4, 'Δ₅': A5, 'Δ₆': A6}
```

**Interpretation:**
- High A₁ → translation involved
- High A₂ → rotation/reflection involved
- High A₃ → expansion/tiling involved
- High A₄ → cropping/extraction involved
- High A₅ → iterative process
- High A₆ → significant identity preservation

---

## Recursive Zone Geometry

### Zone Boundaries

Where one fan meets another, there is a **zone boundary**:

$$\partial(\Delta_i \cap \Delta_j) = \text{edge where fans } i \text{ and } j \text{ interact}$$

### Fan Coherence

Within a zone, the fan vector field should be coherent:

$$\lim_{x \to p^+} \hat{\mathcal{C}}_i(x) = \lim_{x \to p^-} \hat{\mathcal{C}}_i(x)$$

If not, there's a **phase conflict** requiring resolution.

### Zone Drift

When fans misalign, there's **drift**:

$$\mathcal{D}_{ij} = \left\| \vec{\delta}_i - \vec{\delta}_j \right\|$$

High drift indicates composite operations or conflicts.

---

## Connection to ARC Operations

Every ARC primitive maps to fan activations:

| ARC Primitive | Fan Signature |
|---------------|---------------|
| `translate(dx, dy)` | Δ₁ high, others low |
| `rotate_90()` | Δ₂ high |
| `reflect_x()` | Δ₂ high, specific curl sign |
| `scale(n)` | Δ₃ high |
| `tile(m, n)` | Δ₃ high, periodic signature |
| `crop(region)` | Δ₄ high |
| `color_replace(a, b)` | Δ₆ high |
| `iterate(f, n)` | Δ₅ high |

---

## Files in This Folder

- [six_pyramid_model.md](./six_pyramid_model.md) — Detailed geometry of Δ₁-Δ₆
- [membrane_formalism.md](./membrane_formalism.md) — Σ_E equations and operators
- [fan_alignment.md](./fan_alignment.md) — Radial sector dynamics
- [drift_intersections.md](./drift_intersections.md) — Where zones converge

---

## Key Insight

*"In Zoned Collapse Geometry, the edge is real—not just a limit, but a construct."*

ARC operations don't happen "to" the grid. They happen **at the edge membrane**, where fan surfaces meet and collapse events emit resolved values.

---

*"The edge is not a mistake—it is where structure reveals its seams."*
