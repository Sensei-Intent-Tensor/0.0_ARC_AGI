#!/usr/bin/env python3
"""
ITT Primitives for ARC-AGI
==========================

Building block operations derived from Intent Tensor Theory.
No scipy. No borrowed abstractions. Built from the axioms.

The Four Primitives:
  Φ   - Scalar potential of distinction (the value at a cell)
  ∇Φ  - Ordering gradient (where values change)
  σ   - Irreducible residue (accumulated quantity)
  ρ_q - Boundary charge (value frozen at termination)

From these, we derive:
  - Connected components (σ-accumulation through constant-Φ regions)
  - Boundaries (where ∇Φ ≠ 0)
  - Interior vs exterior (topological classification)
  - Object detection (bounded σ-regions)
"""

import numpy as np
from typing import List, Tuple, Set, Dict, Optional
from collections import deque

# =============================================================================
# LAYER 0: THE PRIMITIVES
# =============================================================================

def phi(grid: np.ndarray) -> np.ndarray:
    """
    Φ: Scalar potential of distinction.
    
    The raw value field. Each cell holds a scalar that distinguishes it.
    In ARC, this is the color (0-9).
    
    This is the GIVEN. Everything else is DERIVED.
    """
    return np.array(grid, dtype=int)


def grad_phi(grid: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    ∇Φ: The gradient field (ordering asymmetry).
    
    Returns (dy, dx) - the change in Φ along each axis.
    
    Where ∇Φ = 0, the field is constant (same value).
    Where ∇Φ ≠ 0, there is a boundary (value changes).
    
    This is Δ₁ in the fan surface framework.
    """
    grid = phi(grid)
    h, w = grid.shape
    
    # Gradient in y direction (down is positive)
    dy = np.zeros_like(grid)
    dy[1:, :] = grid[1:, :] - grid[:-1, :]
    
    # Gradient in x direction (right is positive)
    dx = np.zeros_like(grid)
    dx[:, 1:] = grid[:, 1:] - grid[:, :-1]
    
    return dy, dx


def boundary_field(grid: np.ndarray) -> np.ndarray:
    """
    Boundary detection: where ∇Φ ≠ 0.
    
    Returns a boolean field: True where the cell is adjacent to a different value.
    This is where ρ_q (boundary charge) can exist.
    """
    grid = phi(grid)
    dy, dx = grad_phi(grid)
    
    # A cell is on a boundary if ANY adjacent cell differs
    # Check all 4 directions
    h, w = grid.shape
    boundary = np.zeros((h, w), dtype=bool)
    
    # Has different neighbor above
    boundary[1:, :] |= (dy[1:, :] != 0)
    # Has different neighbor below
    boundary[:-1, :] |= (dy[1:, :] != 0)
    # Has different neighbor left
    boundary[:, 1:] |= (dx[:, 1:] != 0)
    # Has different neighbor right
    boundary[:, :-1] |= (dx[:, 1:] != 0)
    
    return boundary


# =============================================================================
# LAYER 1: σ-ACCUMULATION (Connected Components from First Principles)
# =============================================================================

def sigma_flood(grid: np.ndarray, start: Tuple[int, int], 
                visited: np.ndarray) -> Tuple[Set[Tuple[int, int]], int]:
    """
    σ-accumulation: Flood through constant-Φ region.
    
    Starting from a cell, accumulate all connected cells with the same Φ value.
    This is the fundamental operation of "claiming" a region.
    
    Returns:
        cells: Set of (row, col) tuples in this component
        sigma: The accumulated count (|σ|)
    
    ITT Interpretation:
        - We start at a point with potential Φ₀
        - σ flows through all adjacent cells where Φ = Φ₀ (zero gradient path)
        - σ stops at boundaries where Φ ≠ Φ₀ (non-zero gradient)
        - The accumulated σ is the "mass" of this component
    """
    grid = phi(grid)
    h, w = grid.shape
    r0, c0 = start
    
    if visited[r0, c0]:
        return set(), 0
    
    target_phi = grid[r0, c0]
    cells = set()
    queue = deque([(r0, c0)])
    
    while queue:
        r, c = queue.popleft()
        
        # Bounds check
        if r < 0 or r >= h or c < 0 or c >= w:
            continue
        
        # Already visited
        if visited[r, c]:
            continue
        
        # Boundary: different Φ value (gradient ≠ 0)
        if grid[r, c] != target_phi:
            continue
        
        # Accumulate this cell
        visited[r, c] = True
        cells.add((r, c))
        
        # Propagate σ to neighbors (4-connectivity)
        queue.extend([(r-1, c), (r+1, c), (r, c-1), (r, c+1)])
    
    return cells, len(cells)


def find_components(grid: np.ndarray, target_value: Optional[int] = None) -> List[Dict]:
    """
    Find all connected components in the grid.
    
    If target_value is specified, only find components of that value.
    Otherwise, find all components for all values.
    
    Returns list of component dictionaries:
        {
            'phi': the Φ value of this component,
            'cells': set of (r, c) tuples,
            'sigma': accumulated count,
            'bbox': (r_min, r_max, c_min, c_max),
            'touches_border': bool
        }
    
    ITT Interpretation:
        Each component is a σ-accumulation region bounded by ∇Φ ≠ 0.
        The component's identity (ρ_q) is its Φ value.
    """
    grid = phi(grid)
    h, w = grid.shape
    visited = np.zeros((h, w), dtype=bool)
    components = []
    
    for r in range(h):
        for c in range(w):
            if visited[r, c]:
                continue
            
            cell_phi = grid[r, c]
            if target_value is not None and cell_phi != target_value:
                visited[r, c] = True  # Skip but mark visited
                continue
            
            cells, sigma = sigma_flood(grid, (r, c), visited)
            
            if sigma == 0:
                continue
            
            # Compute bounding box
            rows = [cell[0] for cell in cells]
            cols = [cell[1] for cell in cells]
            bbox = (min(rows), max(rows), min(cols), max(cols))
            
            # Check if touches border
            touches_border = any(
                r == 0 or r == h-1 or c == 0 or c == w-1 
                for r, c in cells
            )
            
            components.append({
                'phi': cell_phi,
                'cells': cells,
                'sigma': sigma,
                'bbox': bbox,
                'touches_border': touches_border
            })
    
    return components


def label_grid(grid: np.ndarray, target_value: Optional[int] = None) -> Tuple[np.ndarray, int]:
    """
    Label connected components with integers.
    
    Like scipy.ndimage.label, but built from ITT primitives.
    
    Returns:
        labeled: Grid where each component has a unique integer label
        num_components: Total number of components found
    """
    grid = phi(grid)
    h, w = grid.shape
    labeled = np.zeros((h, w), dtype=int)
    
    components = find_components(grid, target_value)
    
    for i, comp in enumerate(components, 1):
        for r, c in comp['cells']:
            labeled[r, c] = i
    
    return labeled, len(components)


# =============================================================================
# LAYER 2: TOPOLOGICAL OPERATIONS
# =============================================================================

def interior_components(grid: np.ndarray, background: int = 0) -> List[Dict]:
    """
    Find components that don't touch the grid border.
    
    These are "interior" or "enclosed" regions.
    
    ITT Interpretation:
        Interior = σ-accumulation that terminates before reaching grid boundary
        The grid boundary is a special ρ_q surface - the "edge of the world"
    """
    components = find_components(grid, background)
    return [c for c in components if not c['touches_border']]


def exterior_component(grid: np.ndarray, background: int = 0) -> Optional[Dict]:
    """
    Find the exterior (border-touching) background component.
    
    This is the "outside" of all enclosed regions.
    """
    components = find_components(grid, background)
    border_components = [c for c in components if c['touches_border']]
    
    if not border_components:
        return None
    
    # Return the largest border-touching component
    return max(border_components, key=lambda c: c['sigma'])


def extract_region(grid: np.ndarray, cells: Set[Tuple[int, int]]) -> np.ndarray:
    """
    Extract a rectangular region containing the specified cells.
    
    Returns the minimal bounding subgrid.
    """
    if not cells:
        return np.array([[]])
    
    rows = [c[0] for c in cells]
    cols = [c[1] for c in cells]
    r_min, r_max = min(rows), max(rows)
    c_min, c_max = min(cols), max(cols)
    
    return grid[r_min:r_max+1, c_min:c_max+1].copy()


# =============================================================================
# LAYER 3: OBJECT DETECTION
# =============================================================================

def find_objects(grid: np.ndarray, background: int = 0) -> List[Dict]:
    """
    Find discrete objects (non-background components).
    
    An "object" is a connected component of non-background cells.
    
    ITT Interpretation:
        Objects are σ-accumulations where Φ ≠ 0 (assuming 0 is background).
        Each object has its own ρ_q (identity) determined by its Φ values.
    """
    grid = phi(grid)
    h, w = grid.shape
    visited = np.zeros((h, w), dtype=bool)
    
    # Mark background as visited so we skip it
    visited[grid == background] = True
    
    objects = []
    
    for r in range(h):
        for c in range(w):
            if visited[r, c]:
                continue
            
            # Flood fill for ANY non-background (8-connectivity for objects)
            cells = set()
            queue = deque([(r, c)])
            
            while queue:
                rr, cc = queue.popleft()
                
                if rr < 0 or rr >= h or cc < 0 or cc >= w:
                    continue
                if visited[rr, cc]:
                    continue
                if grid[rr, cc] == background:
                    continue
                
                visited[rr, cc] = True
                cells.add((rr, cc))
                
                # 8-connectivity for objects
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        queue.append((rr + dr, cc + dc))
            
            if cells:
                rows = [cell[0] for cell in cells]
                cols = [cell[1] for cell in cells]
                
                # Get the Φ values in this object
                phi_values = set(grid[r, c] for r, c in cells)
                
                objects.append({
                    'cells': cells,
                    'sigma': len(cells),
                    'bbox': (min(rows), max(rows), min(cols), max(cols)),
                    'phi_values': phi_values,
                    'touches_border': any(
                        r == 0 or r == h-1 or c == 0 or c == w-1 
                        for r, c in cells
                    )
                })
    
    return objects


# =============================================================================
# LAYER 4: PATTERN DETECTION (Meta-Analysis)
# =============================================================================

def analyze_transformation(input_grid: np.ndarray, output_grid: np.ndarray) -> Dict:
    """
    Analyze the transformation from input to output.
    
    This is meta-analysis: what TYPE of transformation is this?
    
    Returns a dictionary of detected properties.
    """
    inp = phi(input_grid)
    out = phi(output_grid)
    
    analysis = {
        # Shape analysis
        'input_shape': inp.shape,
        'output_shape': out.shape,
        'same_shape': inp.shape == out.shape,
        'shape_ratio': (out.shape[0] / inp.shape[0], out.shape[1] / inp.shape[1]) if inp.shape[0] > 0 and inp.shape[1] > 0 else (0, 0),
        
        # Color analysis
        'input_colors': set(np.unique(inp)),
        'output_colors': set(np.unique(out)),
        'new_colors': set(np.unique(out)) - set(np.unique(inp)),
        'removed_colors': set(np.unique(inp)) - set(np.unique(out)),
        
        # Component analysis
        'input_components': len(find_components(inp)),
        'output_components': len(find_components(out)),
        
        # Tiling detection
        'is_integer_scale': (
            out.shape[0] % inp.shape[0] == 0 and 
            out.shape[1] % inp.shape[1] == 0
        ) if inp.shape[0] > 0 and inp.shape[1] > 0 else False,
    }
    
    # Check for simple transforms if same shape
    if analysis['same_shape']:
        analysis['is_identity'] = np.array_equal(inp, out)
        analysis['is_flip_lr'] = np.array_equal(np.fliplr(inp), out)
        analysis['is_flip_ud'] = np.array_equal(np.flipud(inp), out)
        analysis['is_rot90'] = np.array_equal(np.rot90(inp, 1), out)
        analysis['is_rot180'] = np.array_equal(np.rot90(inp, 2), out)
        analysis['is_rot270'] = np.array_equal(np.rot90(inp, 3), out)
        analysis['is_transpose'] = inp.shape == out.T.shape and np.array_equal(inp.T, out)
        
        # Color remapping detection
        if analysis['input_colors'] == analysis['output_colors'] or len(analysis['new_colors']) > 0:
            # Check if it's a simple color remapping
            color_map = {}
            is_color_map = True
            for r in range(inp.shape[0]):
                for c in range(inp.shape[1]):
                    in_val = inp[r, c]
                    out_val = out[r, c]
                    if in_val in color_map:
                        if color_map[in_val] != out_val:
                            is_color_map = False
                            break
                    else:
                        color_map[in_val] = out_val
                if not is_color_map:
                    break
            
            analysis['is_color_remap'] = is_color_map
            if is_color_map:
                analysis['color_map'] = color_map
    
    return analysis


def classify_task(task: Dict) -> Dict:
    """
    Classify a task based on its training examples.
    
    This is the META-CLASSIFIER: what pattern family does this task belong to?
    
    Returns classification with confidence scores.
    """
    classifications = {
        'tiling': 0.0,
        'filling': 0.0,
        'recoloring': 0.0,
        'geometric_transform': 0.0,
        'object_manipulation': 0.0,
        'pattern_extension': 0.0,
        'unknown': 0.0,
    }
    
    analyses = []
    for pair in task['train']:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        analyses.append(analyze_transformation(inp, out))
    
    # Aggregate analyses
    all_same_shape = all(a['same_shape'] for a in analyses)
    all_integer_scale = all(a['is_integer_scale'] for a in analyses)
    any_new_colors = any(len(a['new_colors']) > 0 for a in analyses)
    
    # Classify based on patterns
    
    # Geometric transform: same shape, matches a known transform
    if all_same_shape:
        transforms = ['is_flip_lr', 'is_flip_ud', 'is_rot90', 'is_rot180', 'is_rot270', 'is_transpose']
        for t in transforms:
            if all(a.get(t, False) for a in analyses):
                classifications['geometric_transform'] = 1.0
                classifications['detected_transform'] = t
                break
    
    # Tiling: output is integer multiple of input
    if all_integer_scale and not all_same_shape:
        classifications['tiling'] = 0.8
    
    # Filling: same shape, new colors appear
    if all_same_shape and any_new_colors:
        classifications['filling'] = 0.7
    
    # Recoloring: color map exists
    if all_same_shape and all(a.get('is_color_remap', False) for a in analyses):
        classifications['recoloring'] = 0.9
    
    # Pattern extension: output larger, periodic structure
    if not all_same_shape:
        ratios = [a['shape_ratio'] for a in analyses]
        if len(set(ratios)) == 1 and ratios[0][0] > 1:
            classifications['pattern_extension'] = 0.6
    
    # If nothing classified, mark unknown
    if max(classifications.values()) == 0:
        classifications['unknown'] = 1.0
    
    return classifications


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test with a simple grid
    test_grid = np.array([
        [0, 0, 1, 1, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [2, 2, 0, 3, 3],
        [2, 2, 0, 3, 3],
    ])
    
    print("Test Grid:")
    print(test_grid)
    
    print("\n=== Gradient Field ===")
    dy, dx = grad_phi(test_grid)
    print("dy (vertical):")
    print(dy)
    print("dx (horizontal):")
    print(dx)
    
    print("\n=== Boundary Field ===")
    print(boundary_field(test_grid).astype(int))
    
    print("\n=== Components (all) ===")
    for comp in find_components(test_grid):
        print(f"  Φ={comp['phi']}, σ={comp['sigma']}, bbox={comp['bbox']}, border={comp['touches_border']}")
    
    print("\n=== Components (value=0 only) ===")
    for comp in find_components(test_grid, 0):
        print(f"  Φ={comp['phi']}, σ={comp['sigma']}, border={comp['touches_border']}")
    
    print("\n=== Interior Components (value=0) ===")
    for comp in interior_components(test_grid, 0):
        print(f"  Φ={comp['phi']}, σ={comp['sigma']}")
    
    print("\n=== Objects ===")
    for obj in find_objects(test_grid, 0):
        print(f"  σ={obj['sigma']}, Φ_values={obj['phi_values']}, bbox={obj['bbox']}")
    
    print("\n=== Label Grid ===")
    labeled, n = label_grid(test_grid)
    print(f"Found {n} components")
    print(labeled)
