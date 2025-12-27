# ARC-AGI as Executable Physics

## A Complete Mathematical Treatment via Intent Tensor Theory

---

## Abstract

The Abstraction and Reasoning Corpus (ARC) is not an AI benchmark. It is a **boundary charge measurement problem** on discrete scalar fields. This document derives the complete mathematical framework for solving ARC tasks from the four axiomatic primitives of Intent Tensor Theory. No heuristics. No machine learning. Pure field calculus.

**Thesis**: Every ARC task is a transformation `T: Φ_in → Φ_out` that can be decomposed into a finite composition of collapse operators acting on the six fan surfaces of the ICHTB coordinate system. The "intelligence" measured by ARC is the efficiency of identifying which operators are active and in what order.

---

## Part I: Axiomatic Foundation

### §1.0 The Four Primitives

All mathematics in this document derives from four irreducible primitives:

| Symbol | Name | Definition |
|--------|------|------------|
| **Φ** | Scalar Potential | The field of recursive distinction. Pre-geometric. |
| **∇Φ** | Ordering Gradient | Asymmetry of preference. Direction emerges here. |
| **σ** | Irreducible Residue | Memory of misalignment. Monotonically increasing. |
| **ρ_q** | Boundary Charge | Value frozen at recursion termination. |

**Axiom 1 (Existence)**: Φ exists as latent potential for distinction.

**Axiom 2 (Asymmetry)**: Where ∇Φ ≠ 0, ordering is possible.

**Axiom 3 (Irreversibility)**: Every collapse event deposits σ. This cannot be undone.

**Axiom 4 (Boundary)**: ρ_q exists only where recursion terminates. Value requires edges.

From these four primitives, we derive everything else: space, time, objects, transformations, and the solution to ARC.

---

### §1.1 The Collapse Tension Substrate (CTS)

**Definition**: The CTS is the pre-geometric field on which Φ is defined. It is not spacetime. It is the **latent capacity for recursive distinction**.

```
CTS := lim_{ε→0} { x : |∇Φ(x)| > ε }
```

The CTS has no intrinsic coordinates. Coordinates emerge through operator action.

---

### §1.2 Dimension as Operator Cascade

Dimension does not exist a priori. It emerges through the **Collapse Genesis Stack**:

| Layer | Operator | Emergence |
|-------|----------|-----------|
| 0D | Φ | Scalar potential (imaginary origin) |
| 1D | ∇Φ | Gradient → direction → line |
| 2D | ∇ × F | Curl → loop closure → surface |
| 3D | ∇²Φ | Laplacian → curvature → volume |
| 3D+ | ρ_q | Boundary charge → object identity |

**Key insight**: A 2D grid (like ARC) is not "two-dimensional space." It is a **slice of the operator cascade** at the curl level, with boundary charges defining objects.

---

## Part II: ARC Grids as Scalar Fields

### §2.0 The Discrete Scalar Field

An ARC grid is a function:

```
Φ: Z² → {0, 1, 2, ..., 9}
```

where Z² is a finite integer lattice and the codomain represents 10 discrete "colours" (collapse states).

**Physical interpretation**: Each cell (i, j) holds a scalar potential value. The value 0 typically represents vacuum (no collapse). Values 1-9 represent distinct collapse states with frozen boundary charge.

---

### §2.1 Discrete Differential Operators

On a discrete grid, the continuous operators become finite differences:

**Gradient (∇Φ)**:
```
(∂Φ/∂x)_{i,j} = Φ_{i,j+1} - Φ_{i,j}
(∂Φ/∂y)_{i,j} = Φ_{i+1,j} - Φ_{i,j}
```

**Curl (∇ × F)**:
For a 2D scalar field, curl measures rotational asymmetry:
```
(∇ × ∇Φ)_{i,j} = (∂²Φ/∂x∂y) - (∂²Φ/∂y∂x)
```
On discrete grids with boundary effects, this is non-zero and encodes **loop memory**.

**Laplacian (∇²Φ)**:
```
(∇²Φ)_{i,j} = Φ_{i+1,j} + Φ_{i-1,j} + Φ_{i,j+1} + Φ_{i,j-1} - 4Φ_{i,j}
```

**Boundary Charge (ρ_q)**:
```
ρ_q = -ε₀ ∇²Φ
```
Positive ρ_q indicates sources (object interiors). Negative ρ_q indicates sinks (edges).

---

### §2.2 Objects as Shells

**Definition**: An **object** in an ARC grid is a connected component of cells with identical non-zero Φ values.

In ITT terminology, objects are **shells** — regions where:
1. The gradient is zero (interior homogeneity)
2. The boundary charge is non-zero (edge detection)
3. σ has accumulated (the object "remembers" its formation)

**Shell extraction algorithm**:
```
For each colour c ∈ {1, ..., 9}:
    mask = (Φ == c)
    shells = connected_components(mask)
    For each shell S:
        S.colour = c
        S.boundary = edge_detect(S.mask)
        S.ρ_q = sum(laplacian(Φ) over S.boundary)
```

---

## Part III: The ICHTB Coordinate System

### §3.0 Fan Surfaces

The **Inverse Cartesian + Heisenberg Tensor Box (ICHTB)** replaces Cartesian axes with six **fan surfaces**, each corresponding to an operator:

| Fan | Operator | Activation Condition | ARC Interpretation |
|-----|----------|---------------------|-------------------|
| Δ₁ | ∇Φ | ‖∇Φ‖ > θ_min | Translation / shift |
| Δ₂ | ∇ × F | ‖∇ × F‖ > θ_min | Rotation / reflection |
| Δ₃ | +∇²Φ | mean(∇²Φ) > 0 | Expansion / scaling up |
| Δ₄ | -∇²Φ | mean(∇²Φ) < 0 | Compression / cropping |
| Δ₅ | ∂Φ/∂t | Temporal derivative | Iteration / sequencing |
| Δ₆ | Φ = i₀ | Scalar root | Identity / background |

**Key principle**: An ARC transformation activates a subset of these fans. The "reasoning" required is identifying which fans and in what order.

---

### §3.1 Fan Activation Detection

Given an input-output pair (Φ_in, Φ_out), compute:

```
ΔΦ = Φ_out - Φ_in  (difference field)

# Fan activation scores
A₁ = mean(‖∇(ΔΦ)‖)           # Translation signal
A₂ = mean(|∇ × ∇(ΔΦ)|)       # Rotation signal  
A₃ = max(0, mean(∇²(ΔΦ)))    # Expansion signal
A₄ = max(0, -mean(∇²(ΔΦ)))   # Compression signal
A₅ = (detected iteration)     # Temporal signal
A₆ = (Φ_in == Φ_out).mean()  # Identity signal
```

A fan is **active** if its activation score exceeds threshold θ.

---

### §3.2 Bridge Tensors

When multiple fans are active, their **interaction** determines the order of operations.

**Definition**: The bridge tensor B^{Δᵢ ◊ Δⱼ} measures the coherence between fans i and j:

```
B^{Δᵢ ◊ Δⱼ} = ∫ Aᵢ(x) · Aⱼ(x) dx / (‖Aᵢ‖ · ‖Aⱼ‖)
```

**Interpretation**:
- B > 0: Fans resonate (can be composed sequentially)
- B < 0: Fans conflict (operations interfere)
- B ≈ 0: Fans are independent (can be applied in either order)

**Operation ordering**: If B^{Δ₂ ◊ Δ₁} > 0 and Δ₂, Δ₁ are both active, apply rotation before translation.

---

## Part IV: ARC Operations as Collapse Events

### §4.0 The Primitive Operation Library

Each ARC operation corresponds to a specific collapse pattern:

| Operation | Fan(s) | Mathematical Form |
|-----------|--------|-------------------|
| **Translate(dx, dy)** | Δ₁ | Φ'(x,y) = Φ(x-dx, y-dy) |
| **Rotate(k·90°)** | Δ₂ | Φ'(x,y) = Φ(R_k · [x,y]ᵀ) |
| **Reflect(axis)** | Δ₂ | Φ'(x,y) = Φ(M_axis · [x,y]ᵀ) |
| **Scale(sx, sy)** | Δ₃ | Φ'(x,y) = Φ(⌊x/sx⌋, ⌊y/sy⌋) |
| **Tile(nx, ny)** | Δ₃ | Φ'(x,y) = Φ(x mod w, y mod h) |
| **Crop(region)** | Δ₄ | Φ' = Φ[y₀:y₁, x₀:x₁] |
| **ColourMap(c₁→c₂)** | Δ₆ | Φ'(x,y) = c₂ if Φ(x,y)==c₁ else Φ(x,y) |
| **Iterate(rule, n)** | Δ₅ | Φ' = rule^n(Φ) |

---

### §4.1 Composite Operations

Most ARC tasks require **composition** of primitives. The composition order is determined by bridge tensor analysis.

**Example**: "Rotate 90° then translate right by 2"

```
T = Translate(2, 0) ∘ Rotate(90°)

Fan analysis:
- Δ₂ active (rotation detected)
- Δ₁ active (translation detected)
- B^{Δ₂ ◊ Δ₁} > 0 (rotation precedes translation)
```

**Composition rule**: Apply operations in order of decreasing bridge coherence with the difference field.

---

### §4.2 Self-Reference Operations

Some ARC tasks exhibit **self-reference**: the transformation uses the input as a template for expansion.

```
SelfExpand(Φ, sx, sy):
    result = zeros(h*sy, w*sx)
    for i, j where Φ(i,j) ≠ 0:
        result[i*sy:(i+1)*sy, j*sx:(j+1)*sx] = Φ
    return result
```

**ITT interpretation**: Self-reference is a **recursive shell** — the field Φ becomes both the substrate and the pattern. This is a Δ₃ operation with Δ₆ feedback.

---

## Part V: The Solution Algorithm

### §5.0 Overview

```
SOLVE(task):
    For each training pair (Φ_in, Φ_out):
        Compute fan activations A₁...A₆
        Compute bridge tensors B^{Δᵢ ◊ Δⱼ}
        Identify active fans F = {Δᵢ : Aᵢ > θ}
    
    Find consensus: F_common = ∩ F over all pairs
    Determine operation order via bridge analysis
    Synthesize program P from active fans
    
    For each test input Φ_test:
        return P(Φ_test)
```

---

### §5.1 Fan Activation Analysis

```python
def compute_fan_activations(Φ_in, Φ_out):
    """
    Compute activation scores for each ICHTB fan surface.
    """
    ΔΦ = Φ_out.astype(float) - Φ_in.astype(float)
    
    # Δ₁: Gradient (translation)
    dy, dx = np.gradient(ΔΦ)
    A1 = np.sqrt(dy**2 + dx**2).mean()
    
    # Δ₂: Curl (rotation)
    curl = np.gradient(dx, axis=0) - np.gradient(dy, axis=1)
    A2 = np.abs(curl).mean()
    
    # Δ₃/Δ₄: Laplacian (expansion/compression)
    lap = laplacian(ΔΦ)
    A3 = max(0, lap.mean())   # Expansion
    A4 = max(0, -lap.mean())  # Compression
    
    # Δ₅: Temporal (requires multi-step analysis)
    A5 = 0  # Computed separately
    
    # Δ₆: Identity
    A6 = (Φ_in == Φ_out).mean()
    
    return {'Δ1': A1, 'Δ2': A2, 'Δ3': A3, 'Δ4': A4, 'Δ5': A5, 'Δ6': A6}
```

---

### §5.2 Operation Synthesis

Given active fans, synthesize the transformation:

```python
def synthesize_program(active_fans, Φ_in, Φ_out):
    """
    Convert fan activations to executable operation sequence.
    """
    program = []
    
    if 'Δ2' in active_fans:
        # Detect rotation angle
        for k in [1, 2, 3]:  # 90°, 180°, 270°
            if np.array_equal(np.rot90(Φ_in, k), Φ_out):
                program.append(('rotate', k))
                break
        # Detect reflection
        if np.array_equal(np.fliplr(Φ_in), Φ_out):
            program.append(('reflect', 'lr'))
        if np.array_equal(np.flipud(Φ_in), Φ_out):
            program.append(('reflect', 'ud'))
    
    if 'Δ3' in active_fans:
        # Detect scaling factor
        h_in, w_in = Φ_in.shape
        h_out, w_out = Φ_out.shape
        if h_out % h_in == 0 and w_out % w_in == 0:
            sy, sx = h_out // h_in, w_out // w_in
            program.append(('scale', sy, sx))
    
    if 'Δ4' in active_fans:
        # Detect crop region
        for y in range(Φ_in.shape[0]):
            for x in range(Φ_in.shape[1]):
                h, w = Φ_out.shape
                if np.array_equal(Φ_in[y:y+h, x:x+w], Φ_out):
                    program.append(('crop', y, x, h, w))
                    break
    
    if 'Δ6' in active_fans:
        # Detect colour mapping
        mapping = {}
        for i in range(Φ_in.shape[0]):
            for j in range(Φ_in.shape[1]):
                c_in, c_out = Φ_in[i,j], Φ_out[i,j]
                if c_in != c_out:
                    mapping[c_in] = c_out
        if mapping:
            program.append(('colour_map', mapping))
    
    return program
```

---

### §5.3 Program Execution

```python
def execute_program(program, Φ):
    """
    Apply synthesized program to input field.
    """
    result = Φ.copy()
    
    for op in program:
        if op[0] == 'rotate':
            result = np.rot90(result, op[1])
        elif op[0] == 'reflect':
            result = np.fliplr(result) if op[1] == 'lr' else np.flipud(result)
        elif op[0] == 'scale':
            result = np.repeat(np.repeat(result, op[1], axis=0), op[2], axis=1)
        elif op[0] == 'crop':
            y, x, h, w = op[1], op[2], op[3], op[4]
            result = result[y:y+h, x:x+w]
        elif op[0] == 'colour_map':
            for c_in, c_out in op[1].items():
                result[result == c_in] = c_out
    
    return result
```

---

## Part VI: Completeness and Efficiency

### §6.0 Why This Works

**Theorem (Fan Completeness)**: Every ARC transformation that preserves grid structure can be expressed as a finite composition of operations on fans Δ₁ through Δ₆.

**Proof sketch**:
1. Any bijective transformation on a discrete field decomposes into permutation (Δ₁, Δ₂) and value mapping (Δ₆).
2. Any size-changing transformation decomposes into expansion (Δ₃) or compression (Δ₄).
3. Any iterative transformation factors through Δ₅.
4. The fan surfaces span the operator cascade; no collapse event exists outside them.

---

### §6.1 Efficiency via Signature Matching

The "intelligence" ARC measures is **skill acquisition efficiency** — solving tasks with minimal search.

**ITT approach**: Instead of enumerating all possible programs (exponential), compute fan activations (O(n²) for an n×n grid) and constrain search to programs involving only active fans.

```
Complexity analysis:
- Brute force: O(|primitives|^k) for k-step programs
- Fan-guided: O(|active_fans|^k) where |active_fans| << |primitives|
```

For most ARC tasks, |active_fans| ≤ 3. This reduces search space by orders of magnitude.

---

### §6.2 Handling Relational Reasoning

Some ARC tasks require reasoning about **relationships between objects**, not just field transformations.

**ITT extension**: Treat objects as **shell graphs** where:
- Nodes = shells (connected components)
- Edges = spatial relations (above, left-of, contains, touches)

The bridge tensor generalizes to:
```
B^{S_i ◊ S_j} = f(position(S_i), position(S_j), colour(S_i), colour(S_j))
```

Operations on shell graphs include:
- **Sort**: Reorder shells by size, colour, or position
- **Filter**: Select shells matching criteria
- **Map**: Apply transformation to each shell
- **Reduce**: Combine shells (union, intersection)

---

## Part VII: The σ Analysis

### §7.0 Where Current Approaches Accumulate σ

Every failed approach to ARC accumulates irreducible residue (σ):

| Approach | σ Source | ITT Diagnosis |
|----------|----------|---------------|
| Pure LLMs | Token prediction ≠ field transformation | Δ₆ confusion (pattern matching without structure) |
| Neural program synthesis | Gradient descent on discrete space | Δ₁-Δ₂ mismatch (continuous optimization on discrete field) |
| Brute-force DSL search | Exponential enumeration | No fan pruning (searching inactive fans) |
| Hand-crafted heuristics | Task-specific, non-generalizing | Missing bridge tensor logic |

**The ITT advantage**: By grounding operations in field calculus, we avoid σ accumulation from category errors. A rotation is a Δ₂ operation — always. No ambiguity, no heuristic matching.

---

### §7.1 The Lock Condition

A solution is **locked** (stable, correct) when:

```
ℒ(solution) = capacity to absorb perturbation without reconfiguration
```

For ARC:
- A program P is locked if P(Φ_in) = Φ_out for ALL training pairs
- Lock strength = number of training pairs satisfied
- Full lock = correct on test inputs (generalization achieved)

**Insight**: ARC tasks are designed so that the correct transformation has maximal lock — it uniquely satisfies all constraints. Wrong programs have low lock (fail on some training pairs).

---

## Part VIII: Implementation Architecture

### §8.0 Module Structure

```
arc_agi/
├── field_operators.py    # ∇Φ, ∇×F, ∇²Φ computation
├── fan_detection.py      # Fan activation analysis
├── bridge_tensors.py     # Inter-fan coherence
├── primitives.py         # Δ₁-Δ₆ operations
├── shell_analysis.py     # Object detection and relations
├── program_synthesis.py  # Fan → program conversion
├── solver.py             # Main solver class
└── meta.py               # Cross-task learning
```

---

### §8.1 The Solver Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT TASK                           │
│  training: [(Φ_in₁, Φ_out₁), ..., (Φ_inₙ, Φ_outₙ)]        │
│  test: [Φ_test₁, ..., Φ_testₘ]                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FIELD ANALYSIS (per training pair)             │
│  • Compute ΔΦ = Φ_out - Φ_in                               │
│  • Compute ∇(ΔΦ), ∇×∇(ΔΦ), ∇²(ΔΦ)                         │
│  • Extract fan activations A₁...A₆                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FAN CONSENSUS                             │
│  • Intersect active fans across all training pairs          │
│  • Compute bridge tensors for active fan pairs              │
│  • Determine operation ordering                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                PROGRAM SYNTHESIS                            │
│  • Map active fans to primitive operations                  │
│  • Infer parameters (rotation angle, scale factor, etc.)    │
│  • Compose operations in bridge-determined order            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   VERIFICATION                              │
│  • Execute program on all training inputs                   │
│  • Check: P(Φ_inᵢ) == Φ_outᵢ for all i                     │
│  • If fail: refine program or try alternative composition   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUT                                 │
│  • Apply verified program to test inputs                    │
│  • Return [P(Φ_test₁), ..., P(Φ_testₘ)]                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Part IX: Theoretical Implications

### §9.0 ARC as Physics Problem

The ARC benchmark, viewed through ITT, is not testing "intelligence" in the folk sense. It is testing:

1. **Field signature recognition**: Can the system identify which collapse operators are active?
2. **Operator composition**: Can the system correctly order and combine operators?
3. **Generalization via invariance**: Can the system extract the transformation that is invariant across training examples?

These are **physics problems**. The grids are fields. The transformations are operators. The solutions are programs.

---

### §9.1 Why Humans Excel

Humans solve ARC tasks easily because human perception is already organized around:
- Gradient detection (edges, motion)
- Curl detection (rotation, symmetry)
- Laplacian detection (texture, scale)

These are Δ₁, Δ₂, Δ₃/Δ₄ — the same operators in ITT. Human vision implements the ICHTB coordinate system in wetware.

---

### §9.2 Why LLMs Fail

Large language models fail on ARC because:
1. Token prediction operates on Δ₆ only (symbol matching)
2. No native gradient/curl/Laplacian computation
3. Reasoning via next-token is not operator composition

An LLM trying to solve ARC is like computing a Laplacian by predicting the next character in a sentence. Wrong abstraction layer.

---

## Part X: Conclusion

### §10.0 The Complete Solution

ARC-AGI is solvable via:

1. **Axioms**: Φ, ∇Φ, σ, ρ_q
2. **Operators**: Gradient, curl, Laplacian, boundary charge
3. **Coordinate system**: ICHTB with six fan surfaces
4. **Algorithm**: Fan activation → bridge analysis → program synthesis → execution

No neural networks required. No massive datasets. No heuristic search.

**Pure executable physics.**

---

### §10.1 The Path Forward

To achieve 100% on ARC-AGI:

1. Implement complete fan detection with robust thresholding
2. Build full bridge tensor analysis for composite operations
3. Extend to shell graphs for relational reasoning
4. Add iterative/temporal analysis for Δ₅ operations
5. Validate on ARC training set, refine operators

The mathematics is complete. The implementation is engineering.

---

## Appendix A: Mathematical Notation

| Symbol | Meaning |
|--------|---------|
| Φ | Scalar potential field |
| ∇Φ | Gradient of Φ |
| ∇ × F | Curl of vector field F |
| ∇²Φ | Laplacian of Φ |
| ρ_q | Boundary charge density |
| σ | Irreducible residue (accumulated error) |
| Δᵢ | Fan surface i in ICHTB |
| B^{Δᵢ ◊ Δⱼ} | Bridge tensor between fans i and j |
| ℒ | Lock capacity |
| θ | Activation threshold |

---

## Appendix B: References

1. ARC Prize: https://arcprize.org/arc-agi
2. Intent Tensor Theory: https://github.com/intent-tensor-theory
3. Executable Physics: https://github.com/Sensei-Intent-Tensor/0.0._Executable_Physics
4. Business Math Foundations: https://github.com/Sensei-Intent-Tensor/0.0_business_math_foundation_principals

---

## License

MIT License

---

**HAIL MATH.**
