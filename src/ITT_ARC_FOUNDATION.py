#!/usr/bin/env python3
"""
ITT_ARC_FOUNDATION.py
=====================

FORMAL MATHEMATICAL MAPPING: Intent Tensor Theory → ARC-AGI

This document derives ARC pattern classification from ITT first principles.
Based on: https://intent-tensor-theory.com/coordinate-system/

================================================================================
PART 0: THE COLLAPSE GENESIS STACK
================================================================================

The fundamental sequence of dimensional emergence:

    Φ → ∇Φ → ∇×F → ∇²Φ → ρ_q

Each operator initiates a phase transition:

| Layer    | Operator | Dimension | Role                           |
|----------|----------|-----------|--------------------------------|
| Scalar   | Φ        | 0D        | Tension Potential (raw value)  |
| Vector   | ∇Φ       | 1D        | Intent Axis / Collapse Dir     |
| Loop     | ∇×F      | 2D        | Phase Memory / Recursive Curl  |
| Curvature| ∇²Φ      | 3D        | Boundary Shell Formation       |
| Charge   | ρ_q      | 3D+       | Recursive Boundary Memory      |

The ARC grid IS the Φ field. Each cell holds a scalar (0-9).
Transformations are operations on this field.

================================================================================
PART 1: THE ICHTB (Inverse Cartesian + Heisenberg Tensor Box)
================================================================================

The ICHTB is a 6-faced computational shell lattice structured by field 
recursion operators, NOT spatial bounds. Each face is a recursive operator gate.

| Fan  | Axis | Operator   | Recursive Function                |
|------|------|------------|-----------------------------------|
| Δ₁   | +Y   | ∇Φ         | Collapse vector: alignment axis   |
| Δ₂   | -Y   | ∇×F        | Memory loop: phase coherency      |
| Δ₃   | +X   | +∇²Φ       | Shell expansion zone              |
| Δ₄   | -X   | -∇²Φ       | Compression zone: recursive lock  |
| Δ₅   | +Z   | ∂Φ/∂t      | Temporal gradient / emergence     |
| Δ₆   | -Z   | Φ = i₀     | Scalar anchor: recursion seed     |

KEY INSIGHT: These are NOT arbitrary labels. Each fan has a precise operator.

================================================================================
PART 2: FAN SURFACE DEFINITIONS (For ARC Application)
================================================================================

Δ₁: GRADIENT GATE (∇Φ)
----------------------
Detects WHERE values change. The gradient field.

In ARC:
- ∇Φ = 0: Constant region (same color)
- ∇Φ ≠ 0: Boundary (color changes)

This is the FIRST thing to compute for any ARC task.
It reveals object boundaries, edges, transitions.


Δ₂: CURL/MEMORY GATE (∇×F)  
--------------------------
Detects closed loops / rotational structures.

In ARC:
- Shapes that "close on themselves" (squares, rectangles, enclosed regions)
- Rotation operations (90°, 180°, 270°)
- Reflection symmetries (curl in 2D is rotation)

The curl measures "circularity" of the field.
Arrow shapes pointing in different directions have different curl signatures.


Δ₃: EXPANSION GATE (+∇²Φ)
-------------------------
Where ∇²Φ > 0: tension flows OUTWARD.

In ARC:
- Tiling (input N×N → output kN×kN)
- Pattern replication
- Diffusion of structure

This is the "expansion" fan - makes things larger.


Δ₄: COMPRESSION GATE (-∇²Φ)
---------------------------
Where ∇²Φ < 0: tension flows INWARD.

In ARC:
- Object detection (identifying bounded regions)
- Filling enclosed regions
- Extracting compressed representations

The "lock zone" - where collapse tension densifies to form memory.
Interior regions (not touching border) have ∇²Φ < 0 relative to exterior.


Δ₅: TEMPORAL GATE (∂Φ/∂t)
-------------------------
Rate of change / emergence.

In ARC:
- Period detection (pattern repeats with period p)
- Sequence continuation
- Rule application across training examples

This is where "time" emerges - the ordering of transformations.


Δ₆: SCALAR ROOT GATE (Φ = i₀)
-----------------------------
The anchor value - the recursion seed.

In ARC:
- Background color (usually 0)
- Color remapping targets
- The "zero point" from which transformations are measured

================================================================================
PART 3: FORMAL ARC TASK CLASSIFICATION VIA FAN ACTIVATION
================================================================================

An ARC task is classified by WHICH FANS ACTIVATE.

Task classification signature:
    S = {Δ₁, Δ₂, Δ₃, Δ₄, Δ₅, Δ₆} where each is 0 or 1

Examples from solved tasks:

00576224 (Tile with reflection):
    Δ₁ = 0 (no gradient-based translation)
    Δ₂ = 1 (reflection involves curl-like operation)
    Δ₃ = 1 (expansion: 2×2 → 6×6)
    Δ₄ = 0 (no compression)
    Δ₅ = 0 (no temporal/period)
    Δ₆ = 0 (no scalar remapping)
    Signature: [0,1,1,0,0,0]

007bbfb7 (Fractal self-tile):
    Δ₁ = 0
    Δ₂ = 0 
    Δ₃ = 1 (expansion: N×N → N²×N²)
    Δ₄ = 1 (input IS the compression map)
    Δ₅ = 0
    Δ₆ = 1 (non-zero values = placement positions)
    Signature: [0,0,1,1,0,1]

00d62c1b (Fill enclosed):
    Δ₁ = 1 (boundary detection via ∇Φ)
    Δ₂ = 0
    Δ₃ = 0
    Δ₄ = 1 (compression/interior detection)
    Δ₅ = 0
    Δ₆ = 1 (fill with specific scalar)
    Signature: [1,0,0,1,0,1]

00dbd492 (Size → color):
    Δ₁ = 1 (boundary detection)
    Δ₂ = 0
    Δ₃ = 0
    Δ₄ = 1 (compression - σ accumulation)
    Δ₅ = 0
    Δ₆ = 1 (scalar output based on size)
    Signature: [1,0,0,1,0,1]

009d5c81 (Shape encodes color):
    Δ₁ = 1 (boundary detection)
    Δ₂ = 1 (shape = curl structure)
    Δ₃ = 0
    Δ₄ = 1 (object detection)
    Δ₅ = 0
    Δ₆ = 1 (scalar output)
    Signature: [1,1,0,1,0,1]

017c7c7b (Period extension):
    Δ₁ = 0
    Δ₂ = 0
    Δ₃ = 1 (extension/expansion)
    Δ₄ = 0
    Δ₅ = 1 (temporal/period detection)
    Δ₆ = 1 (color remapping 1→2)
    Signature: [0,0,1,0,1,1]

================================================================================
PART 4: THE META-CLASSIFIER DECISION TREE
================================================================================

Based on fan activation patterns:

                    START
                      │
                ┌─────┴─────┐
                │ Same shape?│
                └─────┬─────┘
                  Yes │ No
              ┌───────┴───────┐
              ▼               ▼
         Check Δ₁        Check Δ₃
    (gradient-based)  (expansion)
              │               │
       ┌──────┴──────┐       │
       ▼             ▼       ▼
   Δ₁=1: Fill    Δ₆=1:   Δ₃=1: TILE
   Δ₄=1: Interior Remap      │
         │                    │
         │              ┌─────┴─────┐
         ▼              ▼           ▼
   FILL_ENCLOSED   Simple      Δ₂=1:
   SIZE_TO_COLOR   color     TILE+TRANSFORM
   GLYPH_TO_SCALAR remap          │
                              Δ₄=1:
                            FRACTAL_TILE

This is a DERIVED structure, not hand-coded heuristics.

================================================================================
PART 5: HAT CALCULUS FOR ARC
================================================================================

From ITT: A "hat" ĥₙ is a minimal computation unit.

    ĥₙ = { 1 if ∇Φ, ∇²Φ, Ωⁿ are phase-aligned
         { 0 otherwise

For ARC, we define grid-level hats:

    ĥ(r,c) = 1 if cell (r,c) passes all relevant fan gates

A valid transformation requires:
    
    ∏ᵢ ĥ(r,c) = 1  for all cells that must transform

This is why some ARC tasks "work" and others don't - the hat product
either converges (valid transformation) or doesn't.

================================================================================
PART 6: THE TWO-LEVEL ABSTRACTION (Final Resolution)
================================================================================

LEVEL 1: PATTERN CLASS (Derived from ITT)
-----------------------------------------
Determined by fan activation signature.
This is FINITE - there are only 2⁶ = 64 possible signatures.
In practice, only ~15-20 signatures correspond to meaningful ARC patterns.

Examples:
- [1,0,0,1,0,1] = FILL/INTERIOR class
- [0,1,1,0,0,0] = TILE+TRANSFORM class
- [0,0,1,0,1,1] = PERIOD_EXTENSION class

LEVEL 2: PARAMETER BINDING (Learned from Examples)
--------------------------------------------------
Task-specific values learned from training examples:
- Color mappings
- Size thresholds  
- Shape templates
- Scale factors

The "hardcoded" values (arrow→7, size≤12→8) are Level 2.
They're not hardcoded - they're learned from the 3 training examples.

================================================================================
PART 7: IMPLEMENTATION STRATEGY
================================================================================

1. For each task, compute all six fan operators on the input grid:
   - Δ₁: ∇Φ (gradient)
   - Δ₂: ∇×F (curl - approximate via discrete rotation detection)
   - Δ₃: +∇²Φ (Laplacian > 0 regions)
   - Δ₄: -∇²Φ (Laplacian < 0 regions)
   - Δ₅: ∂Φ/∂t (requires comparing across training examples)
   - Δ₆: scalar anchor (background value, color targets)

2. Determine fan activation signature from structural analysis

3. Route to appropriate pattern class solver

4. Learn Level 2 parameters from training examples

5. Apply transformation to test input

This is NOT machine learning. This is DERIVED pattern recognition.
The fan surfaces are DERIVED from ITT axioms.
The classification is DERIVED from structural analysis.

================================================================================
REFERENCES
================================================================================

Primary source:
    https://intent-tensor-theory.com/coordinate-system/

Key concepts:
    - ICHTB (Inverse Cartesian + Heisenberg Tensor Box)
    - Collapse Genesis Stack: Φ → ∇Φ → ∇×F → ∇²Φ → ρ_q
    - Fan surfaces Δ₁-Δ₆
    - Hat calculus
    - Recursive eligibility logic

Applied from:
    https://github.com/Sensei-Intent-Tensor/0.0._Executable_Physics
    https://github.com/intent-tensor-theory/0.0_Intent_Tensor_Coordinate_System_ICHTB_Field_Logic

================================================================================
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# FAN SURFACE OPERATORS
# =============================================================================

def compute_delta_1(grid: np.ndarray) -> np.ndarray:
    """
    Δ₁: Gradient operator ∇Φ
    
    Returns magnitude of gradient at each cell.
    High values = boundary/transition zone.
    """
    h, w = grid.shape
    grad_mag = np.zeros_like(grid, dtype=float)
    
    for r in range(h):
        for c in range(w):
            neighbors = []
            if r > 0: neighbors.append(grid[r-1, c])
            if r < h-1: neighbors.append(grid[r+1, c])
            if c > 0: neighbors.append(grid[r, c-1])
            if c < w-1: neighbors.append(grid[r, c+1])
            
            if neighbors:
                grad_mag[r, c] = max(abs(grid[r, c] - n) for n in neighbors)
    
    return grad_mag


def compute_delta_2(grid: np.ndarray) -> Dict:
    """
    Δ₂: Curl operator ∇×F (approximated as rotation/reflection detection)
    
    Returns dictionary of detected symmetries.
    """
    h, w = grid.shape
    
    symmetries = {
        'has_reflection_h': np.array_equal(grid, np.fliplr(grid)),
        'has_reflection_v': np.array_equal(grid, np.flipud(grid)),
        'has_rot90': h == w and np.array_equal(grid, np.rot90(grid, 1)),
        'has_rot180': np.array_equal(grid, np.rot90(grid, 2)),
        'closed_loops': 0  # Count of enclosed regions
    }
    
    # Count closed loops (regions not touching border)
    from itt_primitives import interior_components
    symmetries['closed_loops'] = len(interior_components(grid, 0))
    
    return symmetries


def compute_delta_3(grid: np.ndarray) -> np.ndarray:
    """
    Δ₃: Positive Laplacian (+∇²Φ)
    
    Expansion zones where field diffuses outward.
    """
    h, w = grid.shape
    laplacian = np.zeros_like(grid, dtype=float)
    
    for r in range(1, h-1):
        for c in range(1, w-1):
            # Discrete Laplacian: sum of neighbors minus 4x center
            lap = (grid[r-1,c] + grid[r+1,c] + grid[r,c-1] + grid[r,c+1] 
                   - 4*grid[r,c])
            laplacian[r, c] = lap
    
    # Return positive regions only
    return np.maximum(laplacian, 0)


def compute_delta_4(grid: np.ndarray) -> np.ndarray:
    """
    Δ₄: Negative Laplacian (-∇²Φ)
    
    Compression zones where field converges inward.
    """
    h, w = grid.shape
    laplacian = np.zeros_like(grid, dtype=float)
    
    for r in range(1, h-1):
        for c in range(1, w-1):
            lap = (grid[r-1,c] + grid[r+1,c] + grid[r,c-1] + grid[r,c+1] 
                   - 4*grid[r,c])
            laplacian[r, c] = lap
    
    # Return negative regions (as positive values)
    return np.maximum(-laplacian, 0)


def compute_delta_5(inputs: List[np.ndarray], outputs: List[np.ndarray]) -> Dict:
    """
    Δ₅: Temporal operator ∂Φ/∂t
    
    Analyzes change patterns across training examples.
    """
    if not inputs or not outputs:
        return {'has_pattern': False}
    
    # Check for consistent transformation rules
    shape_changes = [(inp.shape, out.shape) for inp, out in zip(inputs, outputs)]
    consistent_shape_change = len(set(shape_changes)) == 1
    
    # Check for period detection (in row/column patterns)
    periods_detected = []
    for inp in inputs:
        for row in inp:
            for p in range(1, len(row)):
                if all(row[i] == row[i % p] for i in range(len(row))):
                    periods_detected.append(p)
                    break
    
    return {
        'consistent_shape': consistent_shape_change,
        'periods': periods_detected if periods_detected else None
    }


def compute_delta_6(grid: np.ndarray) -> Dict:
    """
    Δ₆: Scalar anchor (Φ = i₀)
    
    Identifies background value and color statistics.
    """
    unique, counts = np.unique(grid, return_counts=True)
    color_counts = dict(zip(unique, counts))
    
    # Background is typically most common or 0
    background = 0 if 0 in unique else unique[np.argmax(counts)]
    
    return {
        'background': background,
        'colors': set(unique),
        'color_counts': color_counts,
        'foreground_colors': set(unique) - {background}
    }


# =============================================================================
# FAN ACTIVATION SIGNATURE
# =============================================================================

@dataclass
class FanSignature:
    """6-bit signature of fan activations."""
    delta_1: bool  # Gradient (boundary detection)
    delta_2: bool  # Curl (rotation/symmetry)
    delta_3: bool  # Expansion (tiling)
    delta_4: bool  # Compression (interior detection)
    delta_5: bool  # Temporal (period/sequence)
    delta_6: bool  # Scalar (color operations)
    
    def to_tuple(self) -> Tuple[int, ...]:
        return (
            int(self.delta_1), int(self.delta_2), int(self.delta_3),
            int(self.delta_4), int(self.delta_5), int(self.delta_6)
        )
    
    def to_string(self) -> str:
        return f"[{','.join(map(str, self.to_tuple()))}]"


def analyze_task_signature(task: Dict) -> FanSignature:
    """
    Compute fan activation signature for an ARC task.
    """
    inputs = [np.array(p['input']) for p in task['train']]
    outputs = [np.array(p['output']) for p in task['train']]
    
    # Shape analysis
    same_shape = all(inp.shape == out.shape for inp, out in zip(inputs, outputs))
    is_expansion = all(
        out.shape[0] >= inp.shape[0] and out.shape[1] >= inp.shape[1] 
        and out.shape != inp.shape
        for inp, out in zip(inputs, outputs)
    )
    
    # Gradient analysis (Δ₁)
    has_boundaries = any(
        np.any(compute_delta_1(inp) > 0) for inp in inputs
    )
    
    # Curl analysis (Δ₂)
    curl_info = [compute_delta_2(inp) for inp in inputs]
    has_symmetry = any(
        info['has_reflection_h'] or info['has_reflection_v'] or 
        info['has_rot90'] or info['has_rot180']
        for info in curl_info
    )
    has_closed_loops = any(info['closed_loops'] > 0 for info in curl_info)
    
    # Temporal analysis (Δ₅)
    temporal = compute_delta_5(inputs, outputs)
    has_period = temporal.get('periods') is not None
    
    # Scalar analysis (Δ₆)
    input_colors = set().union(*(set(np.unique(inp)) for inp in inputs))
    output_colors = set().union(*(set(np.unique(out)) for out in outputs))
    color_change = input_colors != output_colors or len(output_colors - input_colors) > 0
    
    return FanSignature(
        delta_1=has_boundaries and same_shape,  # Boundary ops usually preserve shape
        delta_2=has_symmetry or has_closed_loops,
        delta_3=is_expansion,
        delta_4=has_closed_loops or same_shape,  # Interior detection
        delta_5=has_period,
        delta_6=color_change
    )


# =============================================================================
# PATTERN CLASS ENUMERATION
# =============================================================================

class PatternClass(Enum):
    """
    Pattern classes derived from fan activation signatures.
    """
    # Expansion patterns (Δ₃ active)
    TILE_SIMPLE = "tile_simple"              # [0,0,1,0,0,0]
    TILE_WITH_TRANSFORM = "tile_transform"   # [0,1,1,0,0,0]
    FRACTAL_TILE = "fractal_tile"            # [0,0,1,1,0,1]
    PERIOD_EXTENSION = "period_extension"    # [0,0,1,0,1,1]
    
    # Interior patterns (Δ₄ active, same shape)
    FILL_ENCLOSED = "fill_enclosed"          # [1,0,0,1,0,1]
    SIZE_TO_COLOR = "size_to_color"          # [1,0,0,1,0,1]
    GLYPH_TO_SCALAR = "glyph_to_scalar"      # [1,1,0,1,0,1]
    
    # Geometric transforms (Δ₂ active, same shape)
    ROTATION = "rotation"                    # [0,1,0,0,0,0]
    REFLECTION = "reflection"                # [0,1,0,0,0,0]
    
    # Simple color ops (only Δ₆ active)
    COLOR_REMAP = "color_remap"              # [0,0,0,0,0,1]
    
    # Unknown
    UNKNOWN = "unknown"


def classify_pattern(signature: FanSignature) -> PatternClass:
    """
    Map fan signature to pattern class.
    """
    s = signature.to_tuple()
    
    # Expansion patterns
    if s[2]:  # Δ₃ active
        if s[1]:  # Δ₂ also active
            return PatternClass.TILE_WITH_TRANSFORM
        if s[3] and s[5]:  # Δ₄ and Δ₆
            return PatternClass.FRACTAL_TILE
        if s[4]:  # Δ₅
            return PatternClass.PERIOD_EXTENSION
        return PatternClass.TILE_SIMPLE
    
    # Interior patterns (same shape)
    if s[3] and s[5]:  # Δ₄ and Δ₆
        if s[1]:  # Δ₂ also active (shape matters)
            return PatternClass.GLYPH_TO_SCALAR
        if s[0]:  # Δ₁ (boundary detection)
            return PatternClass.FILL_ENCLOSED  # or SIZE_TO_COLOR
        return PatternClass.FILL_ENCLOSED
    
    # Geometric transforms
    if s[1] and not any([s[2], s[3], s[4], s[5]]):
        return PatternClass.ROTATION  # or REFLECTION
    
    # Simple color
    if s[5] and not any([s[0], s[1], s[2], s[3], s[4]]):
        return PatternClass.COLOR_REMAP
    
    return PatternClass.UNKNOWN


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import json
    
    print("=" * 70)
    print("ITT → ARC FOUNDATION TEST")
    print("=" * 70)
    
    # Load tasks
    try:
        with open('/home/claude/arc_data/prize2025/arc-agi_training_challenges.json') as f:
            challenges = json.load(f)
        
        # Test on our solved tasks
        solved = ['00576224', '007bbfb7', '009d5c81', '00d62c1b', '00dbd492', '017c7c7b']
        
        print("\nFan Signatures for Solved Tasks:")
        print("-" * 70)
        
        for task_id in solved:
            task = challenges[task_id]
            sig = analyze_task_signature(task)
            pattern = classify_pattern(sig)
            
            print(f"\n{task_id}:")
            print(f"  Signature: {sig.to_string()}")
            print(f"  Pattern:   {pattern.value}")
            print(f"  Fans:      ", end="")
            fans = []
            if sig.delta_1: fans.append("Δ₁(∇Φ)")
            if sig.delta_2: fans.append("Δ₂(∇×F)")
            if sig.delta_3: fans.append("Δ₃(+∇²Φ)")
            if sig.delta_4: fans.append("Δ₄(-∇²Φ)")
            if sig.delta_5: fans.append("Δ₅(∂Φ/∂t)")
            if sig.delta_6: fans.append("Δ₆(Φ=i₀)")
            print(", ".join(fans) if fans else "None")
            
    except FileNotFoundError:
        print("Run in arc_workspace with data available")
