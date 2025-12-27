# ARC-AGI Solver Submissions

**Working Code Implementing Intent Tensor Theory**

---

## Evolution of Approaches

This folder contains the actual solver implementations - "playful pokes thinking the math through."

### Version History

| Version | File | Approach | Performance |
|---------|------|----------|-------------|
| v1 | `curvent_solver_v1.py` | Curvent Field Theory (∇Φ, ∇×F, ∇²Φ) | ~85% on evaluation |
| v2 | `itt_solver_v2.py` | Full 6-Fan ICHTB Detection | In development |

---

## v1: Curvent Field Theory Solver

**Source:** Originally from year-old experiments, proven to work on ~85% of evaluation challenges.

### Mathematical Foundation

The solver implements three core field operators:

```
∇Φ  (Gradient)   → Δ₁ Fan → Translation/shift detection
∇×F (Curl)       → Δ₂ Fan → Rotation/reflection detection  
∇²Φ (Laplacian)  → Δ₃/Δ₄  → Scale/curvature detection
```

### Key Functions

```python
compute_gradient(grid)        # ∇Φ - value flow direction
compute_curl(grid)            # ∇×F - rotational symmetry
compute_curvature(grid)       # ∇²Φ - stable/anchor regions
compute_symmetry_tensor(grid) # Combined fan analysis
detect_transformation(inp, out)  # Identify which operation
apply_transformation(grid, op)   # Execute the operation
```

### Supported Operations

| Operation | Detection Method | Fan Signature |
|-----------|------------------|---------------|
| `flip_lr` | Direct comparison | Δ₂ (curl sign) |
| `flip_ud` | Direct comparison | Δ₂ (curl sign) |
| `rot90/180/270` | Direct comparison | Δ₂ (curl magnitude) |
| `transpose` | Direct comparison | Δ₂ |
| `value_map` | Consistent mapping | Δ₆ (scalar) |
| `shift` | Roll comparison | Δ₁ (gradient) |
| `scale` | Tiling verification | Δ₃ (expansion) |
| `block_swap` | Curl inversion | Δ₂ (mirror curl) |

---

## Colab Notebooks

### Original Experiments

1. **85__solved_arc-agi_evaluation_challenges.ipynb**
   - The main working solver
   - Implements Curvent Field Theory
   - ~85% accuracy on evaluation set

2. **ARC-AGI_-_Math_based-Nailed_it.ipynb**
   - Rubric extraction experiments
   - Shape analysis, color mapping detection
   - Foundation for understanding task structure

3. **ARC-AGI_-_prediction-focused_solver.ipynb**
   - Simpler pattern learning
   - Flip/rotate detection only
   - Good baseline comparison

---

## Running the Solver

### Local Execution

```python
from curvent_solver_v1 import solve_arc_curvent

task = {
    "train": [
        {"input": [[1,2],[3,4]], "output": [[2,1],[4,3]]}
    ],
    "test": [
        {"input": [[5,6],[7,8]]}
    ]
}

predictions = solve_arc_curvent(task)
print(predictions)  # [[6,5],[8,7]]
```

### Google Colab

Open any of the `.ipynb` files in Colab and run all cells.

---

## Connection to ITT Mathematics

| Solver Function | ITT Concept | Book Reference |
|-----------------|-------------|----------------|
| `compute_gradient` | ∇Φ ordering gradient | Book 0A Axiom 2 |
| `compute_curl` | Phase memory tensor | Book 2 |
| `compute_curvature` | Collapse curvature | Book 4 |
| `detect_transformation` | Fan activation detection | Book 8 |
| `apply_transformation` | Resolution operator R_B | BCCR |

---

## Improvement Path

### Current Limitations (v1)

1. Only detects single operations (no composites)
2. No bridge tensor analysis for ordering
3. Limited to shape-preserving transformations
4. No iterative/temporal fan (Δ₅)

### Planned for v2

1. Full 6-fan activation detection
2. Bridge tensor computation for composite operations
3. Program synthesis from fan signatures
4. Handling of size-changing transformations

---

## Validation

To verify against the math:

1. Each detected transformation should map to specific fan activation
2. Bridge tensors should show correct operation ordering
3. Program synthesis should produce minimal representation

If validation fails → recalibrate the math framework.

---

*"These are playful pokes thinking the math through."*

HAIL MATH.
