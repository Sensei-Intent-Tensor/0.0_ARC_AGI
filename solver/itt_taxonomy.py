#!/usr/bin/env python3
"""
ITT Task Taxonomy
=================

Formalizing the two levels of abstraction in ARC tasks:

LEVEL 1: PATTERN CLASS (Universal - Derived from ITT)
  These are the "what type of transformation is this" questions.
  They correspond to specific fan surface activations (Δ₁-Δ₆).
  
  Pattern classes are FINITE and DERIVABLE from the axioms.

LEVEL 2: PARAMETER BINDING (Task-Specific - Learned from Examples)
  These are the "what specific values" questions.
  They are INFERRED from training examples.
  
  Parameters are INFINITE but CONSTRAINED by the pattern class.

Example:
  Task 009d5c81 (shape encodes color)
  
  LEVEL 1 (Pattern Class):
    - Indicator object (small, one color) encodes target color
    - Main object (large, different color) gets recolored
    - Indicator is removed, main gets filled
    → This is the Δ₆ GLYPH pattern: geometric form → scalar value
  
  LEVEL 2 (Parameters):
    - Indicator color = 1
    - Main color = 8  
    - Down-arrow → 7, Up-arrow → 3, Plus → 2
    → These are learned from training examples

The breakthrough insight:
  If we can DERIVE all Level 1 pattern classes from ITT,
  then Level 2 becomes simple inductive inference.
  
  The "hard" part of ARC is recognizing the pattern class.
  The "easy" part is learning the parameters.

This is why ITT matters:
  Other approaches try to learn both levels simultaneously.
  ITT gives us Level 1 for free (derived from axioms).
  We only need to learn Level 2.
"""

from typing import Dict, List, Set, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum, auto
import numpy as np

# =============================================================================
# PATTERN CLASSES (Level 1)
# =============================================================================

class PatternClass(Enum):
    """
    The finite set of pattern classes derivable from ITT.
    
    Each corresponds to specific fan surface activations.
    """
    # Δ₁: Gradient-based (translation, position)
    TRANSLATION = auto()      # Object moves
    POSITION_DEPENDENT = auto()  # Output depends on position
    
    # Δ₂: Curl-based (rotation, reflection)
    ROTATION = auto()         # Rotate by 90°, 180°, 270°
    REFLECTION = auto()       # Flip horizontal or vertical
    TRANSPOSE = auto()        # Swap rows and columns
    
    # Δ₃: Laplacian-based (scale, tiling)
    SCALE = auto()            # Enlarge or shrink
    TILE = auto()             # Repeat pattern
    TILE_WITH_TRANSFORM = auto()  # Tile + reflection/rotation
    FRACTAL_TILE = auto()     # Self-similar tiling (input IS the map)
    
    # Δ₄: Compression (object detection, grouping)
    FILL_ENCLOSED = auto()    # Fill interior regions
    EXTRACT_OBJECT = auto()   # Pull out specific object
    COUNT_OBJECTS = auto()    # Count and encode
    
    # Δ₅: Boundary-based (edge detection, outline)
    OUTLINE = auto()          # Draw boundary
    BOUNDARY_TRANSFORM = auto()  # Transform based on boundary
    
    # Δ₆: Scalar mapping (color, value)
    COLOR_REMAP = auto()      # Simple color substitution
    SIZE_TO_COLOR = auto()    # Size determines color
    GLYPH_TO_SCALAR = auto()  # Shape encodes value
    POSITION_TO_COLOR = auto()  # Position determines color
    
    # Composite patterns
    PERIOD_EXTENSION = auto()  # Detect period, extend
    CONDITIONAL = auto()      # If-then rules
    RELATIONAL = auto()       # Object-to-object relationships
    
    # Unknown (requires new derivation)
    UNKNOWN = auto()


@dataclass
class PatternSignature:
    """
    A pattern signature captures Level 1 information.
    
    This is what we DERIVE from ITT, not learn from examples.
    """
    pattern_class: PatternClass
    
    # Which fan surfaces activate
    delta_1: bool = False  # Gradient
    delta_2: bool = False  # Curl (rotation/reflection)
    delta_3: bool = False  # Laplacian (scale)
    delta_4: bool = False  # Compression (objects)
    delta_5: bool = False  # Boundary
    delta_6: bool = False  # Scalar mapping
    
    # Shape relationship
    shape_preserved: bool = True
    shape_scaled: bool = False
    scale_factor: Optional[Tuple[int, int]] = None
    
    # Color relationship
    colors_preserved: bool = True
    colors_remapped: bool = False
    new_colors_introduced: bool = False
    
    # Topological
    requires_component_analysis: bool = False
    requires_boundary_detection: bool = False


@dataclass 
class ParameterBinding:
    """
    A parameter binding captures Level 2 information.
    
    This is what we LEARN from training examples.
    """
    # Color mappings (if applicable)
    color_map: Optional[Dict[int, int]] = None
    
    # Size thresholds (if applicable)
    size_thresholds: Optional[List[Tuple[int, int]]] = None  # [(threshold, color), ...]
    
    # Shape templates (if applicable)
    shape_templates: Optional[Dict[Tuple, int]] = None  # {shape_tuple: value}
    
    # Scale factors (if applicable)
    scale: Optional[Tuple[int, int]] = None
    
    # Period (if applicable)
    period: Optional[int] = None
    
    # Other task-specific parameters
    custom: Optional[Dict] = None


# =============================================================================
# PATTERN SIGNATURES FOR SOLVED TASKS
# =============================================================================

TASK_SIGNATURES = {
    "00576224": PatternSignature(
        pattern_class=PatternClass.TILE_WITH_TRANSFORM,
        delta_2=True,  # Reflection involved
        delta_3=True,  # Scaling/tiling
        shape_preserved=False,
        shape_scaled=True,
        scale_factor=(3, 3),
    ),
    
    "007bbfb7": PatternSignature(
        pattern_class=PatternClass.FRACTAL_TILE,
        delta_3=True,  # Scaling
        delta_6=True,  # Value determines placement
        shape_preserved=False,
        shape_scaled=True,
        # Scale factor is N² where N is input size
    ),
    
    "009d5c81": PatternSignature(
        pattern_class=PatternClass.GLYPH_TO_SCALAR,
        delta_4=True,  # Object detection
        delta_6=True,  # Shape → color mapping
        shape_preserved=True,
        colors_preserved=False,
        new_colors_introduced=True,
        requires_component_analysis=True,
    ),
    
    "00d62c1b": PatternSignature(
        pattern_class=PatternClass.FILL_ENCLOSED,
        delta_4=True,  # Component analysis
        delta_5=True,  # Boundary detection
        shape_preserved=True,
        colors_preserved=False,
        new_colors_introduced=True,
        requires_component_analysis=True,
        requires_boundary_detection=True,
    ),
    
    "00dbd492": PatternSignature(
        pattern_class=PatternClass.SIZE_TO_COLOR,
        delta_4=True,  # Component analysis (σ accumulation)
        delta_6=True,  # Size → color mapping
        shape_preserved=True,
        colors_preserved=False,
        new_colors_introduced=True,
        requires_component_analysis=True,
    ),
    
    "017c7c7b": PatternSignature(
        pattern_class=PatternClass.PERIOD_EXTENSION,
        delta_3=True,  # Extension (tiling in one direction)
        delta_6=True,  # Color remapping
        shape_preserved=False,
        colors_remapped=True,
    ),
}


# =============================================================================
# PATTERN DETECTION (Deriving Level 1 from Task Structure)
# =============================================================================

def detect_pattern_signature(task: Dict) -> PatternSignature:
    """
    Analyze a task and derive its pattern signature.
    
    This is the key function: given training examples,
    what PATTERN CLASS does this task belong to?
    
    We derive this from structural properties, not by learning.
    """
    analyses = []
    for pair in task['train']:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        analyses.append(_analyze_pair(inp, out))
    
    # Aggregate structural properties
    all_same_shape = all(a['same_shape'] for a in analyses)
    all_scaled = all(a['is_scaled'] for a in analyses)
    any_new_colors = any(a['new_colors'] for a in analyses)
    all_color_remap = all(a['is_color_remap'] for a in analyses)
    
    # Detect specific patterns
    
    # Check geometric transforms (Δ₂)
    if all_same_shape:
        for transform in ['flip_lr', 'flip_ud', 'rot90', 'rot180', 'rot270', 'transpose']:
            if all(a.get(f'is_{transform}', False) for a in analyses):
                if transform in ['flip_lr', 'flip_ud']:
                    return PatternSignature(
                        pattern_class=PatternClass.REFLECTION,
                        delta_2=True,
                        shape_preserved=True,
                    )
                elif transform.startswith('rot'):
                    return PatternSignature(
                        pattern_class=PatternClass.ROTATION,
                        delta_2=True,
                        shape_preserved=True,
                    )
                elif transform == 'transpose':
                    return PatternSignature(
                        pattern_class=PatternClass.TRANSPOSE,
                        delta_2=True,
                        shape_preserved=True,
                    )
    
    # Check tiling (Δ₃)
    if all_scaled:
        ratios = [a['scale_ratio'] for a in analyses]
        if len(set(ratios)) == 1:
            ratio = ratios[0]
            if ratio[0] == ratio[1]:
                # Check if fractal (self-similar)
                # This requires deeper analysis
                pass
            return PatternSignature(
                pattern_class=PatternClass.TILE,
                delta_3=True,
                shape_preserved=False,
                shape_scaled=True,
                scale_factor=ratio,
            )
    
    # Check filling patterns (Δ₄ + Δ₅)
    if all_same_shape and any_new_colors:
        # Likely a fill operation
        return PatternSignature(
            pattern_class=PatternClass.FILL_ENCLOSED,
            delta_4=True,
            delta_5=True,
            shape_preserved=True,
            new_colors_introduced=True,
            requires_component_analysis=True,
        )
    
    # Check color remapping (Δ₆)
    if all_same_shape and all_color_remap:
        return PatternSignature(
            pattern_class=PatternClass.COLOR_REMAP,
            delta_6=True,
            shape_preserved=True,
            colors_remapped=True,
        )
    
    # Default: unknown
    return PatternSignature(pattern_class=PatternClass.UNKNOWN)


def _analyze_pair(inp: np.ndarray, out: np.ndarray) -> Dict:
    """Analyze a single input-output pair."""
    analysis = {
        'same_shape': inp.shape == out.shape,
        'is_scaled': (
            out.shape[0] % inp.shape[0] == 0 and
            out.shape[1] % inp.shape[1] == 0
        ) if inp.shape[0] > 0 and inp.shape[1] > 0 else False,
        'scale_ratio': (
            out.shape[0] // inp.shape[0],
            out.shape[1] // inp.shape[1]
        ) if inp.shape[0] > 0 and inp.shape[1] > 0 else (0, 0),
        'input_colors': set(np.unique(inp)),
        'output_colors': set(np.unique(out)),
        'new_colors': bool(set(np.unique(out)) - set(np.unique(inp))),
    }
    
    # Check transforms
    if analysis['same_shape']:
        analysis['is_flip_lr'] = np.array_equal(np.fliplr(inp), out)
        analysis['is_flip_ud'] = np.array_equal(np.flipud(inp), out)
        analysis['is_rot90'] = np.array_equal(np.rot90(inp, 1), out)
        analysis['is_rot180'] = np.array_equal(np.rot90(inp, 2), out)
        analysis['is_rot270'] = np.array_equal(np.rot90(inp, 3), out)
        analysis['is_transpose'] = inp.shape == out.T.shape and np.array_equal(inp.T, out)
        
        # Check color remap
        color_map = {}
        is_remap = True
        for r in range(inp.shape[0]):
            for c in range(inp.shape[1]):
                i, o = inp[r, c], out[r, c]
                if i in color_map:
                    if color_map[i] != o:
                        is_remap = False
                        break
                else:
                    color_map[i] = o
            if not is_remap:
                break
        analysis['is_color_remap'] = is_remap
        if is_remap:
            analysis['color_map'] = color_map
    
    return analysis


# =============================================================================
# THE KEY INSIGHT
# =============================================================================

"""
Why this matters for ARC:

1. The 25% ceiling exists because current approaches treat Level 1 and Level 2
   as the same problem - they try to learn BOTH the pattern class AND the
   parameters from examples.

2. ITT gives us Level 1 for free. The pattern classes are DERIVABLE from
   the axioms (Φ, ∇Φ, σ, ρ_q). We don't need to learn them.

3. With Level 1 fixed, Level 2 becomes simple:
   - For COLOR_REMAP: learn the mapping from examples
   - For SIZE_TO_COLOR: learn the thresholds from examples
   - For GLYPH_TO_SCALAR: learn the shape→value mapping from examples

4. The "wacky" variation between tasks that Achilles noticed is actually
   just Level 2 variation. The Level 1 pattern classes are finite.

5. This is why the Paper Prize is interesting: we can demonstrate that
   ALL ARC tasks decompose into a finite set of pattern classes, and
   each class corresponds to specific ITT operations.

The competition rules allow pre-computation and pattern libraries.
What they don't allow is task-specific training on the test set.

Our approach:
  - Derive all pattern classes from ITT (pre-computation, allowed)
  - Build solvers for each pattern class (allowed)
  - At test time: detect pattern class → apply solver → learn parameters from train
"""


if __name__ == "__main__":
    import json
    
    with open('/home/claude/arc_data/prize2025/arc-agi_training_challenges.json') as f:
        challenges = json.load(f)
    
    print("Pattern Signatures for Solved Tasks:")
    print("=" * 60)
    
    for task_id, sig in TASK_SIGNATURES.items():
        print(f"\n{task_id}:")
        print(f"  Pattern: {sig.pattern_class.name}")
        fans = []
        if sig.delta_1: fans.append("Δ₁")
        if sig.delta_2: fans.append("Δ₂")
        if sig.delta_3: fans.append("Δ₃")
        if sig.delta_4: fans.append("Δ₄")
        if sig.delta_5: fans.append("Δ₅")
        if sig.delta_6: fans.append("Δ₆")
        print(f"  Fan Surfaces: {', '.join(fans)}")
        print(f"  Shape preserved: {sig.shape_preserved}")
        if sig.requires_component_analysis:
            print(f"  Requires: component analysis (σ-accumulation)")
        if sig.requires_boundary_detection:
            print(f"  Requires: boundary detection (∇Φ ≠ 0)")
