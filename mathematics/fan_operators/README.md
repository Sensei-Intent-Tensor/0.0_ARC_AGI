# Fan Operators: The Six Collapse Surfaces

**Δ₁ through Δ₆ — The Complete Operator Algebra**

---

## Overview

The six fan surfaces are not arbitrary divisions. Each corresponds to a fundamental differential operator that governs a class of transformations.

```
Collapse Genesis Stack:

  Layer 0D:  Φ           (scalar potential)
      ↓
  Layer 1D:  ∇Φ          (gradient → direction)
      ↓
  Layer 2D:  ∇×F         (curl → rotation/memory)
      ↓
  Layer 3D:  ∇²Φ         (Laplacian → curvature)
      ↓
  Layer 3D+: ρ_q         (boundary charge → emission)
```

---

## The Six Fans

| Fan | Operator | Mathematical Form | Geometric Meaning |
|-----|----------|-------------------|-------------------|
| Δ₁ | Gradient | ∇Φ | Direction of steepest descent |
| Δ₂ | Curl | ∇×F | Rotational circulation |
| Δ₃ | +Laplacian | +∇²Φ | Diffusion/expansion |
| Δ₄ | -Laplacian | -∇²Φ | Concentration/compression |
| Δ₅ | Time derivative | ∂Φ/∂t | Rate of change |
| Δ₆ | Scalar anchor | Φ=i₀ | Reference/identity |

---

## Δ₁: Gradient Fan (∇Φ)

### Mathematical Definition

```
∇Φ = (∂Φ/∂x, ∂Φ/∂y)

Discrete form:
  ∂Φ/∂x ≈ Φ[i, j+1] - Φ[i, j]
  ∂Φ/∂y ≈ Φ[i+1, j] - Φ[i, j]
```

### Collapse Role

- **Tension alignment**: Points toward collapse direction
- **Initiates collapse** when ‖∇Φ‖ > θ_min (threshold)
- **Direction encoding**: The vector shows where recursion flows

### ARC Operations

- **Translation**: Constant ∇Φ shifts the pattern
- **Shift detection**: ∇(Φ_out - Φ_in) = displacement vector

### Detection Signature

```python
def detect_gradient_fan(phi_in, phi_out):
    delta = phi_out - phi_in
    grad = np.gradient(delta)
    grad_magnitude = np.sqrt(grad[0]**2 + grad[1]**2)
    return np.mean(grad_magnitude)  # High = translation involved
```

---

## Δ₂: Curl Fan (∇×F)

### Mathematical Definition

```
∇×F = ∂F_y/∂x - ∂F_x/∂y

For scalar field (2D curl analog):
  curl(∇Φ) = ∂²Φ/∂x∂y - ∂²Φ/∂y∂x
```

### Collapse Role

- **Phase memory**: Encodes loop closure and rotation
- **Sign indicates direction**: + = counterclockwise, - = clockwise
- **Detects symmetry breaking**: Non-zero curl means rotational component

### ARC Operations

- **Rotation**: 90°, 180°, 270° rotations
- **Reflection**: Flip across axis (curl sign change)
- **Pattern repetition**: Periodic curl signatures

### Detection Signature

```python
def detect_curl_fan(phi_in, phi_out):
    delta = phi_out - phi_in
    grad = np.gradient(delta)
    # 2D curl approximation
    curl = np.gradient(grad[0], axis=1) - np.gradient(grad[1], axis=0)
    return np.mean(np.abs(curl))  # High = rotation involved
```

---

## Δ₃: Expansion Fan (+∇²Φ)

### Mathematical Definition

```
∇²Φ = ∂²Φ/∂x² + ∂²Φ/∂y²

Discrete form (5-point stencil):
  ∇²Φ[i,j] = Φ[i+1,j] + Φ[i-1,j] + Φ[i,j+1] + Φ[i,j-1] - 4Φ[i,j]
```

### Collapse Role

- **Positive regions**: Allow diffusion of tension
- **Shell growth**: Expands recursive boundaries
- **Pattern spreading**: Information flows outward

### ARC Operations

- **Scaling up**: Enlarging patterns
- **Tiling**: Replicating across larger area
- **Duplication**: Creating copies

### Detection Signature

```python
def detect_expansion_fan(phi_in, phi_out):
    delta = phi_out - phi_in
    laplacian = ndimage.laplace(delta)
    return np.mean(np.maximum(laplacian, 0))  # High = expansion
```

---

## Δ₄: Compression Fan (-∇²Φ)

### Mathematical Definition

```
-∇²Φ = -(∂²Φ/∂x² + ∂²Φ/∂y²)
```

### Collapse Role

- **Negative Laplacian**: Locks curvature
- **Shell contraction**: Condenses recursive boundaries
- **Pattern focusing**: Information concentrates

### ARC Operations

- **Cropping**: Extracting sub-regions
- **Extraction**: Pulling out specific patterns
- **Reduction**: Condensing information

### Detection Signature

```python
def detect_compression_fan(phi_in, phi_out):
    delta = phi_out - phi_in
    laplacian = ndimage.laplace(delta)
    return np.mean(np.maximum(-laplacian, 0))  # High = compression
```

---

## Δ₅: Temporal Fan (∂Φ/∂t)

### Mathematical Definition

```
∂Φ/∂t ≈ (Φ_{n+1} - Φ_n) / Δt

For ARC (discrete iterations):
  ∂Φ/∂n = Φ_{iteration+1} - Φ_{iteration}
```

### Collapse Role

- **Rate of recursion**: How fast the field evolves
- **Emergence of time**: Sequential ordering from iteration
- **Phase synchronization**: Aligns multi-step processes

### ARC Operations

- **Iteration**: Applying a rule multiple times
- **Sequence generation**: Creating patterns in order
- **Growth rules**: Cellular automata-like processes

### Detection Signature

```python
def detect_temporal_fan(training_pairs):
    # Check if output is iterated input
    deltas = [pair['output'] - pair['input'] for pair in training_pairs]
    # Look for consistent delta pattern
    consistency = np.corrcoef([d.flatten() for d in deltas])
    return np.mean(consistency)  # High = iterative process
```

---

## Δ₆: Scalar Root Fan (Φ=i₀)

### Mathematical Definition

```
Φ(x) = i₀  (constant/anchor value)

i₀ = argmax_v Σ_{i,j} (Φ[i,j] == v), v ≠ 0
    (most common non-background value)
```

### Collapse Role

- **Imaginary scalar base**: The anchor point
- **Identity preservation**: What doesn't change
- **Reference frame**: Background vs foreground

### ARC Operations

- **Background identification**: What remains constant
- **Color mapping**: Value substitutions
- **Template anchoring**: Fixed reference patterns

### Detection Signature

```python
def detect_scalar_fan(phi_in, phi_out):
    # How much is unchanged
    unchanged = np.sum(phi_in == phi_out)
    total = phi_in.size
    return unchanged / total  # High = significant preservation
```

---

## Fan Interaction: Bridge Tensors

When multiple fans activate, they interact through **bridge tensors**:

```
B^{Δᵢ◊Δⱼ} = interaction strength between fan i and fan j
```

### Common Bridge Signatures

| Operation | Primary Fan | Secondary Fan | Bridge |
|-----------|-------------|---------------|--------|
| Rotate then translate | Δ₂ | Δ₁ | B^{Δ₂◊Δ₁} |
| Scale then crop | Δ₃ | Δ₄ | B^{Δ₃◊Δ₄} |
| Color then tile | Δ₆ | Δ₃ | B^{Δ₆◊Δ₃} |
| Iterate until stable | Δ₅ | Δ₄ | B^{Δ₅◊Δ₄} |

---

## Files in This Folder

- [gradient_fan_D1.md](./gradient_fan_D1.md) — Translation and direction
- [curl_fan_D2.md](./curl_fan_D2.md) — Rotation and reflection
- [expansion_fan_D3.md](./expansion_fan_D3.md) — Scaling and tiling
- [compression_fan_D4.md](./compression_fan_D4.md) — Cropping and extraction
- [temporal_fan_D5.md](./temporal_fan_D5.md) — Iteration and sequencing
- [scalar_root_D6.md](./scalar_root_D6.md) — Identity and background

---

## Key Insight

Each ARC operation is a **collapse event on a specific fan surface**. The task is not to "learn rules" but to **detect which fans activated** and in what order.

```
Task Analysis Pipeline:
  1. Compute ΔΦ = Φ_out - Φ_in
  2. Measure activation on each fan
  3. Identify active fans (above threshold)
  4. Analyze bridge tensors for ordering
  5. Synthesize program from fan sequence
```

---

*"Dimensions are not additive—they arise from stacking these operators."*
