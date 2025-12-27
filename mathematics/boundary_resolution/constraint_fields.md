# Constraint Fields (Φ)

**Structure Without Signal — The Abstract Pattern Behind ARC Grids**

---

## Definition

A **constraint field** Φ is a relational structure imposed by a stable configuration. It is NOT:
- The pixel values themselves
- A "representation" of the pattern
- A stored copy of the input

It IS:
- The set of relationships between elements
- The invariant structure that produces appearances
- The "thing itself" that different boundaries resolve differently

---

## Formal Definition

```
Φ: M → V

Where:
  M = abstract manifold of relationships
  V = value space (in ARC: {0,1,...,9} colors)
  
The constraint field encodes:
  - Adjacency relations: which elements are "next to" which
  - Value relations: which elements share properties
  - Structural relations: symmetry, periodicity, hierarchy
```

---

## Constraint Field vs. Grid

| Aspect | Grid (Ψ) | Constraint Field (Φ) |
|--------|----------|----------------------|
| Nature | Concrete array | Abstract structure |
| Dimension | Fixed (h×w) | Dimension-free |
| Values | Specific integers | Relationships |
| Storage | Requires memory | Is the pattern itself |
| Transformation | Changes | Invariant |

---

## Types of Constraints in ARC

### 1. Topological Constraints

**Definition:** Relationships that survive continuous deformation.

```
Φ_topo = {
  connectivity: which regions touch
  holes: enclosed areas
  components: disconnected parts
  boundaries: edges between regions
}
```

**Example:** "The blue region surrounds the red region" is topological—it survives scaling, rotation, translation.

### 2. Geometric Constraints

**Definition:** Relationships involving shape and measurement.

```
Φ_geom = {
  symmetry: reflection, rotation invariance
  alignment: rows, columns, diagonals
  proportions: size ratios
  regularity: periodic patterns
}
```

**Example:** "The pattern has 4-fold rotational symmetry" is geometric.

### 3. Chromatic Constraints

**Definition:** Relationships between colors/values.

```
Φ_chrom = {
  adjacency: which colors touch which
  frequency: how many cells of each color
  mapping: color A always becomes color B
  dominance: background vs foreground
}
```

**Example:** "Red cells never touch blue cells" is chromatic.

### 4. Structural Constraints

**Definition:** Higher-order relationships between objects.

```
Φ_struct = {
  objects: identified coherent regions
  relations: spatial relationships between objects
  hierarchy: containment, nesting
  roles: anchor, template, fill
}
```

**Example:** "Small shapes are placed at the corners of large shapes" is structural.

---

## Extracting Φ from Training Pairs

Given training pairs {(Φ_in^i, Φ_out^i)}:

### Step 1: Identify Invariants

What remains constant across all input-output pairs?

```python
def extract_invariants(pairs):
    invariants = {
        'topology': [],
        'geometry': [],
        'chromatic': [],
        'structural': []
    }
    
    for (inp, out) in pairs:
        # Topological: component count, connectivity
        invariants['topology'].append(
            compare_topology(inp, out)
        )
        
        # Geometric: symmetry preservation, alignment
        invariants['geometry'].append(
            compare_geometry(inp, out)
        )
        
        # Chromatic: color mapping consistency
        invariants['chromatic'].append(
            infer_color_map(inp, out)
        )
        
        # Structural: object relationships
        invariants['structural'].append(
            compare_structure(inp, out)
        )
    
    return consensus(invariants)
```

### Step 2: Build Constraint Graph

```
Φ_graph = {
    nodes: identified elements (cells, objects, regions)
    edges: relationships between elements
    labels: constraint types on edges
}
```

### Step 3: Verify Constraint

Test that Φ is consistent across all examples:

```
∀i: Φ_in^i and Φ_out^i are both resolutions of Φ
```

If verification fails, Φ is incomplete—refine.

---

## The Constraint Decomposition

Any constraint field can be decomposed:

```
Φ = Φ_local ⊕ Φ_global ⊕ Φ_relational

Where:
  Φ_local     = per-cell constraints (color rules)
  Φ_global    = whole-grid constraints (dimensions, symmetry)
  Φ_relational = inter-cell constraints (adjacency, alignment)
```

---

## Mathematical Properties

### Property 1: Resolution Invariance

```
If Ψ₁ = R_B₁[Φ] and Ψ₂ = R_B₂[Φ], then:
  
  Φ = Infer(Ψ₁) = Infer(Ψ₂)  (up to boundary effects)
```

The constraint is the same regardless of how it's resolved.

### Property 2: Compositional Structure

```
Φ_composite = Φ₁ ⊗ Φ₂

Resolution distributes:
  R_B[Φ₁ ⊗ Φ₂] = R_B[Φ₁] ⊗ R_B[Φ₂]
```

Complex constraints decompose into simpler ones.

### Property 3: Threshold Stability

```
Small perturbations in Ψ do not change Φ:

  ‖Ψ' - Ψ‖ < ε  →  Φ(Ψ') = Φ(Ψ)
```

Constraints are robust to noise (within threshold).

---

## Connection to Fans

Each constraint type activates specific fans:

| Constraint Type | Fan Detection Method |
|-----------------|----------------------|
| Φ_topo | Component analysis, boundary tracing |
| Φ_geom | Symmetry detection, Δ₂ curl analysis |
| Φ_chrom | Color histogram, Δ₆ scalar analysis |
| Φ_struct | Object detection, bridge tensor analysis |

---

## Example: Pattern Extraction

**Task:** Grid has red squares at corners, blue square in center.

**Constraint Field:**
```
Φ = {
  objects: {corner_squares, center_square}
  relations: {
    corner_squares.position = corners(grid)
    center_square.position = center(grid)
    corner_squares.color = RED
    center_square.color = BLUE
  }
  invariants: {
    count(corner_squares) = 4
    count(center_square) = 1
    no_overlap(corner_squares, center_square)
  }
}
```

This Φ can resolve to any grid size—the boundary determines the actual positions.

---

## Key Insight

The constraint field Φ is not "in" the grid. The grid is a **resolution** of Φ.

Different grids can be resolutions of the same Φ. The ARC task is to find Φ such that:
1. Input is R_B₁[Φ]
2. Output is R_B₂[Φ]
3. B₁ → B₂ is consistent across training examples

---

*"The constraint is not stored. It is the pattern itself."*
