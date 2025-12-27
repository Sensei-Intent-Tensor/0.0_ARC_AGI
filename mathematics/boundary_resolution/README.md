# Boundary-Conditioned Constraint Resolution (BCCR)

**Resolution Without Representation — Applied to ARC**

---

## 「水面は真似をしない。制約を共有する。」
*The surface does not imitate. It shares constraint.*

---

## The Central Thesis

**A transformation is not a mapping. It is the same constraint field resolved through different admissibility boundaries.**

```
Input grid  = R_B₁[Φ]    (resolution through boundary B₁)
Output grid = R_B₂[Φ]    (resolution through boundary B₂)

Same Φ. Different B. No "transformation function." No "rule learning."
The task is constraint inference.
```

---

## Why This Matters for ARC

Current approaches treat ARC as:
- Pattern matching (fails on novel patterns)
- Rule learning (fails on compositional rules)
- Neural synthesis (fails on abstract logic)

BCCR treats ARC as:
- **Constraint field inference**: What is Φ?
- **Boundary detection**: What is B₂?
- **Resolution computation**: Apply R_B₂[Φ]

The "impossible" synchronization between input and output is not mysterious—it is **tautological**. They share the same Φ.

---

## Core Mathematical Objects

| Symbol | Name | ARC Meaning |
|--------|------|-------------|
| Φ | Constraint Field | The abstract pattern structure (color relationships, spatial logic) |
| B | Admissibility Boundary | The resolution conditions (grid dimensions, transformation type) |
| R_B[Φ] | Resolution Operator | The actual grid you see |
| B(t) | Dynamic Boundary | Time-varying or iteration-dependent conditions |
| Ψ | Resolved Appearance | Output of R_B[Φ] |

---

## The Core Equation

```
R_B[Φ] → Ψ

For ARC:
  Φ_in  = R_B₁[Φ]   (input grid)
  Φ_out = R_B₂[Φ]   (output grid)
  
  Training: Given {(Φ_in, Φ_out)} pairs, infer Φ and the boundary transformation B₁ → B₂
  Testing:  Apply R_B₂ to new inputs
```

---

## Boundary Types in ARC

### Type 1: Geometric Boundaries
```
B_scale(s)     : Resolution at scale factor s
B_rotate(θ)   : Resolution at rotation angle θ
B_reflect(a)  : Resolution reflected across axis a
B_crop(r)     : Resolution within region r
```

### Type 2: Value Boundaries
```
B_color(m)    : Resolution under color mapping m
B_threshold(τ): Resolution with value threshold τ
B_replace(k,v): Resolution replacing k with v
```

### Type 3: Structural Boundaries
```
B_tile(n,m)   : Resolution tiled n×m times
B_extract(p)  : Resolution extracting pattern p
B_compose(f)  : Resolution composing with function f
```

### Type 4: Iterative Boundaries
```
B_iterate(n)  : Resolution after n iterations
B_converge(ε) : Resolution when change < ε
B_until(c)    : Resolution until condition c
```

---

## The Resolution Process

### Step 1: Constraint Field Inference

Given training pairs {(Φ_in^i, Φ_out^i)}, extract the shared constraint:

```
Φ = ∩ᵢ Infer(Φ_in^i, Φ_out^i)
```

The constraint field Φ is what remains invariant across all examples.

### Step 2: Boundary Difference Detection

Compute the boundary transformation:

```
ΔB = B₂ ○ B₁⁻¹

Where:
  B₁ = boundary conditions of input
  B₂ = boundary conditions of output
```

### Step 3: Resolution Application

For test input Φ_test:

```
Φ_result = R_B₂[Infer(Φ_test, Φ)]
```

---

## Connection to Fan Surfaces

Each boundary type activates specific fan surfaces:

| Boundary Type | Primary Fan | Secondary Fans |
|---------------|-------------|----------------|
| B_scale | Δ₃ (+∇²Φ) | Δ₄ (-∇²Φ) |
| B_rotate | Δ₂ (∇×F) | Δ₁ (∇Φ) |
| B_reflect | Δ₂ (∇×F) | Δ₆ (Φ=i₀) |
| B_translate | Δ₁ (∇Φ) | — |
| B_color | Δ₆ (Φ=i₀) | — |
| B_iterate | Δ₅ (∂Φ/∂t) | varies |

The boundary transformation ΔB determines which fans activate.

---

## Why Identity Persists

Because identity IS the constraint pattern Φ, not the resolved image Ψ.

```
B(t) varies continuously     → boundary changes
R_B(t)[Φ] varies continuously → appearance changes

But topological invariants of Φ are preserved
until boundary perturbations exceed critical threshold
```

In ARC: the "rule" you're learning is not a function—it's the constraint field Φ itself. The function is just the boundary difference ΔB.

---

## Example: Scaling Task

```
Input:  2×2 grid with pattern P
Output: 6×6 grid with pattern P repeated 3×3

BCCR Analysis:
  Φ = pattern P (the constraint)
  B₁ = B_grid(2,2)
  B₂ = B_grid(6,6) ○ B_tile(3,3)
  ΔB = B_tile(3,3) ○ B_scale(3)
  
Resolution:
  R_B₂[Φ] = tile(P, 3, 3)
```

The "scaling rule" is not learned—it's detected as boundary difference.

---

## Files in This Folder

- [constraint_fields.md](./constraint_fields.md) — What Φ means and how to extract it
- [resolution_operators.md](./resolution_operators.md) — The R_B formalism
- [admissibility.md](./admissibility.md) — Boundary conditions and their algebra

---

## Key Insight

**「像は存在しない。毎回、解かれている。」**
*The image does not exist. It is solved each time.*

The ARC output is not "computed from" the input. Both are resolutions of the same underlying constraint. The task is to find that constraint and the boundary that produces the output.

---

*"The surface does not imitate. It shares constraint."*
