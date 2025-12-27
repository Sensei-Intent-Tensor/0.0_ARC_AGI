# Bridge Tensors: Fan Interactions

**B^{Δᵢ◊Δⱼ} — The Algebra of Composite Operations**

---

## Definition

A **bridge tensor** encodes the interaction between two fan surfaces:

```
B^{Δᵢ◊Δⱼ} : Δᵢ × Δⱼ → ℝ

Where:
  Δᵢ, Δⱼ = fan surfaces
  ◊ = interaction operator (diamond product)
  B = strength and type of interaction
```

---

## Why Bridge Tensors Matter

Most ARC tasks involve **composite operations**:
- Rotate then translate
- Scale then crop
- Color map then tile
- Extract then iterate

The order matters. The interactions matter. Bridge tensors encode both.

---

## Mathematical Formalism

### The Bridge Tensor

```
B^{Δᵢ◊Δⱼ}(x) = ∫_Ω ⟨∇_i Φ(y), ∇_j Φ(x-y)⟩ dy

Where:
  ∇_i = operator associated with fan Δᵢ
  Ω = domain of integration
  ⟨·,·⟩ = inner product
```

### Discrete Approximation

```python
def compute_bridge_tensor(phi, fan_i, fan_j):
    # Compute field from each fan's perspective
    field_i = apply_fan_operator(phi, fan_i)
    field_j = apply_fan_operator(phi, fan_j)
    
    # Cross-correlate
    bridge = np.correlate(field_i.flatten(), field_j.flatten(), mode='full')
    
    # Normalize
    return bridge / (np.linalg.norm(field_i) * np.linalg.norm(field_j))
```

---

## Bridge Types

### Resonant Bridges (B > 0)

Fans **reinforce** each other:
- Rotation + Translation: rotate aligns with shift direction
- Expansion + Identity: expand while preserving core

### Conflict Bridges (B < 0)

Fans **oppose** each other:
- Expansion + Compression: fighting for same region
- Rotation + Identity: rotation breaks preserved pattern

### Orthogonal Bridges (B ≈ 0)

Fans are **independent**:
- Color + Rotation: color change independent of geometry
- Scale + Background: scaling doesn't affect background detection

---

## Common Bridge Signatures in ARC

### B^{Δ₂◊Δ₁}: Rotate-Translate

```
Pattern: Rotate object, then shift to new position

Detection:
  - High curl (Δ₂) activation
  - High gradient (Δ₁) activation
  - Bridge shows rotation center offset from translation vector

Example: Rotate 90° then move to corner
```

### B^{Δ₃◊Δ₄}: Scale-Crop

```
Pattern: Scale up, then extract region

Detection:
  - High positive Laplacian (Δ₃) in source
  - High negative Laplacian (Δ₄) in output bounds
  - Bridge shows scale factor and crop region

Example: Scale 3x then take center third
```

### B^{Δ₆◊Δ₃}: Color-Tile

```
Pattern: Remap colors, then tile pattern

Detection:
  - High scalar preservation (Δ₆) modulo color map
  - High expansion (Δ₃) in output
  - Bridge shows color map consistency across tiles

Example: Swap red/blue then tile 2×2
```

### B^{Δ₅◊Δ₄}: Iterate-Stabilize

```
Pattern: Apply rule repeatedly until stable

Detection:
  - High temporal (Δ₅) showing iteration
  - Compression (Δ₄) stabilizing final state
  - Bridge shows convergence trajectory

Example: Grow pattern until it fills region
```

---

## Computing Bridge Tensors for ARC

```python
def analyze_bridges(phi_in, phi_out, active_fans):
    """
    Given active fans, compute pairwise bridge tensors
    to determine operation ordering.
    """
    bridges = {}
    
    for i, fan_i in enumerate(active_fans):
        for j, fan_j in enumerate(active_fans):
            if i < j:  # Upper triangle only
                bridge_key = f"B^{{Δ{fan_i}◊Δ{fan_j}}}"
                
                # Compute field operators
                op_i = get_fan_operator(phi_in, phi_out, fan_i)
                op_j = get_fan_operator(phi_in, phi_out, fan_j)
                
                # Compute bridge strength
                bridges[bridge_key] = {
                    'strength': compute_correlation(op_i, op_j),
                    'order': infer_order(phi_in, phi_out, fan_i, fan_j),
                    'type': classify_bridge(op_i, op_j)
                }
    
    return bridges
```

---

## Order Inference from Bridges

The bridge tensor encodes which fan acts first:

```python
def infer_order(phi_in, phi_out, fan_i, fan_j):
    """
    Determine if fan_i acts before fan_j or vice versa.
    """
    # Try fan_i first
    intermediate_i = apply_fan(phi_in, fan_i)
    match_i = compare(apply_fan(intermediate_i, fan_j), phi_out)
    
    # Try fan_j first
    intermediate_j = apply_fan(phi_in, fan_j)
    match_j = compare(apply_fan(intermediate_j, fan_i), phi_out)
    
    if match_i > match_j:
        return (fan_i, fan_j)  # i before j
    else:
        return (fan_j, fan_i)  # j before i
```

---

## Bridge Coherence Across Training Pairs

For a valid program, bridges must be **consistent** across all training examples:

```python
def verify_bridge_coherence(training_pairs, program):
    """
    Check that inferred program explains all training pairs.
    """
    for pair in training_pairs:
        phi_in = pair['input']
        phi_out = pair['output']
        
        # Apply program
        phi_pred = apply_program(phi_in, program)
        
        # Check match
        if not np.array_equal(phi_pred, phi_out):
            return False, "Incoherent at pair"
    
    return True, "All pairs explained"
```

---

## The Bridge Tensor Algebra

### Composition

```
B^{Δᵢ◊Δⱼ} ∘ B^{Δⱼ◊Δₖ} = B^{Δᵢ◊Δₖ}  (transitive)
```

### Inversion

```
B^{Δᵢ◊Δⱼ} = -B^{Δⱼ◊Δᵢ}  (antisymmetric order)
```

### Identity

```
B^{Δᵢ◊Δᵢ} = 0  (fan doesn't interact with itself)
```

---

## Files in This Folder

- [composite_operations.md](./composite_operations.md) — Multi-fan programs

---

## Key Insight

Bridge tensors answer the question: **"In what order do the fans activate?"**

The ARC program is not a list of operations—it's a path through the fan interaction graph, with bridge tensors as edge weights.

```
Task → Fan Activations → Bridge Analysis → Ordered Program → Execution
```

---

*"Interactions between fan surfaces are described by bridge tensors that detect resonance or conflict."*
