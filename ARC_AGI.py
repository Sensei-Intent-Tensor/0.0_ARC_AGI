#!/usr/bin/env python3
"""
ARC-AGI Solver
==============

Intent Tensor Theory Applied to Abstract Reasoning

Dataset: https://github.com/fchollet/ARC-AGI
Competition: https://arcprize.org/arc-agi

Training Set: 400 tasks
Public Eval: 400 tasks  
Semi-Private: 100 tasks (mid-2024)
Private Eval: 100 tasks (competition)

HAIL MATH
"""

import json
import numpy as np
from typing import Dict, List, Callable, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import urllib.request
from functools import lru_cache

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO_BASE = "https://raw.githubusercontent.com/fchollet/ARC-AGI/master/data"
TRAINING_PATH = f"{REPO_BASE}/training"
EVALUATION_PATH = f"{REPO_BASE}/evaluation"

# =============================================================================
# ITT PRIMITIVES (Imported conceptually)
# =============================================================================
# From Intent Tensor Theory:
# Φ (Phi): Scalar potential - the underlying pattern
# ∇Φ: Gradient - direction of transformation
# σ (sigma): Residue - what's preserved/lost
# ρ_q: Boundary charge - edge effects

# CSS Layers for pattern recognition:
# L0: Substrate (raw grid)
# L1: Sensation (color detection)
# L2: Memory (pattern recognition)
# L3: Boundary (shape detection)
# L4: Object (connected components)
# L5: Awareness (relationships)
# L6: Category (transformation type)
# L7: Agency (solution synthesis)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

class DatasetType(Enum):
    TRAINING = "training"
    EVALUATION = "evaluation"

@dataclass
class ARCTask:
    """Represents a single ARC task."""
    task_id: str
    dataset: DatasetType
    train: List[Dict]  # List of {input, output} pairs
    test: List[Dict]   # List of {input} (and output for validation)
    
    @property
    def num_train(self) -> int:
        return len(self.train)
    
    @property
    def num_test(self) -> int:
        return len(self.test)

@dataclass
class SolverResult:
    """Result of solving a task."""
    task_id: str
    predictions: List[List[List[int]]]
    correct: Optional[bool] = None
    pattern_detected: Optional[str] = None
    itt_layer: Optional[str] = None

# =============================================================================
# DATA LOADING
# =============================================================================

@lru_cache(maxsize=1000)
def fetch_task(task_id: str, dataset: DatasetType = None) -> Optional[ARCTask]:
    """
    Fetch a task from GitHub.
    
    Tries training first, then evaluation if not found.
    """
    if dataset:
        datasets = [dataset]
    else:
        datasets = [DatasetType.TRAINING, DatasetType.EVALUATION]
    
    for ds in datasets:
        path = TRAINING_PATH if ds == DatasetType.TRAINING else EVALUATION_PATH
        url = f"{path}/{task_id}.json"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return ARCTask(
                    task_id=task_id,
                    dataset=ds,
                    train=data.get('train', []),
                    test=data.get('test', [])
                )
        except:
            continue
    
    return None

def get_task_list(dataset: DatasetType) -> List[str]:
    """Get list of all task IDs in a dataset."""
    # Known task counts
    # Training: 400, Evaluation: 400
    # For now, return a sample - full list would require API call
    if dataset == DatasetType.TRAINING:
        return [
            "007bbfb7", "00d62c1b", "017c7c7b", "025d127b", "045e512c",
            "0520fde7", "05269061", "05f2a901", "06df4c85", "08ed6ac7",
            "09629e4f", "0962bcdd", "0a938d79", "0b148d64", "0ca9ddb6",
            "0d3d703e", "0dfd9992", "0e206a2e", "10fcaaa3", "11852cab",
            # ... (would be all 400)
        ]
    else:
        return [
            "00576224", "009d5c81", "00dbd492", "03560426", "05a7bcf2",
            "0607ce86", "0692e18c", "070dd51e", "08573cc6", "0934a4d8",
            # ... (would be all 400)
        ]

# =============================================================================
# PATTERN ANALYSIS (L2-L4 CSS)
# =============================================================================

def analyze_grid(grid: np.ndarray) -> Dict[str, Any]:
    """
    Analyze a grid for patterns.
    
    Returns ITT-informed analysis.
    """
    h, w = grid.shape
    colors = set(grid.flatten()) - {0}
    
    return {
        'height': h,
        'width': w,
        'colors': colors,
        'num_colors': len(colors),
        'density': np.sum(grid > 0) / (h * w),
        'symmetric_h': np.array_equal(grid, np.fliplr(grid)),
        'symmetric_v': np.array_equal(grid, np.flipud(grid)),
        'has_border': is_bordered(grid),
        'connected_components': count_components(grid),
    }

def is_bordered(grid: np.ndarray) -> bool:
    """Check if grid has a single-color border."""
    if grid.shape[0] < 3 or grid.shape[1] < 3:
        return False
    top = grid[0, :]
    bottom = grid[-1, :]
    left = grid[:, 0]
    right = grid[:, -1]
    border = np.concatenate([top, bottom, left, right])
    return len(set(border)) == 1 and border[0] != 0

def count_components(grid: np.ndarray, color: int = None) -> int:
    """Count connected components."""
    if color is None:
        return sum(count_components(grid, c) for c in set(grid.flatten()) if c != 0)
    
    mask = (grid == color).astype(int)
    visited = np.zeros_like(mask)
    count = 0
    
    def dfs(i, j):
        if i < 0 or i >= mask.shape[0] or j < 0 or j >= mask.shape[1]:
            return
        if visited[i, j] or mask[i, j] == 0:
            return
        visited[i, j] = 1
        dfs(i+1, j); dfs(i-1, j); dfs(i, j+1); dfs(i, j-1)
    
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j] and not visited[i, j]:
                dfs(i, j)
                count += 1
    
    return count

def detect_transformation(train_pairs: List[Dict]) -> Dict[str, Any]:
    """
    Analyze training pairs to detect transformation pattern.
    
    CSS Layer 6: Classification
    """
    transformations = []
    
    for pair in train_pairs:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        
        in_analysis = analyze_grid(inp)
        out_analysis = analyze_grid(out)
        
        transform = {
            'size_change': (out.shape[0] / inp.shape[0], out.shape[1] / inp.shape[1]),
            'color_preserved': in_analysis['colors'] == out_analysis['colors'],
            'is_tiling': check_tiling(inp, out),
            'is_reflection': check_reflection(inp, out),
            'is_rotation': check_rotation(inp, out),
            'is_color_swap': check_color_swap(inp, out),
            'is_fill': check_fill_pattern(inp, out),
        }
        transformations.append(transform)
    
    # Aggregate across all training pairs
    return {
        'consistent_size': len(set(t['size_change'] for t in transformations)) == 1,
        'size_change': transformations[0]['size_change'] if transformations else (1, 1),
        'is_tiling': all(t['is_tiling'] for t in transformations),
        'is_reflection': all(t['is_reflection'] for t in transformations),
        'is_rotation': any(t['is_rotation'] for t in transformations),
        'is_color_swap': all(t['is_color_swap'] for t in transformations),
        'is_fill': any(t['is_fill'] for t in transformations),
    }

def check_tiling(inp: np.ndarray, out: np.ndarray) -> bool:
    """Check if output is a tiling of input."""
    ih, iw = inp.shape
    oh, ow = out.shape
    
    if oh % ih != 0 or ow % iw != 0:
        return False
    
    for i in range(0, oh, ih):
        for j in range(0, ow, iw):
            tile = out[i:i+ih, j:j+iw]
            # Check if tile is input or transformed input
            if not (np.array_equal(tile, inp) or 
                    np.array_equal(tile, np.fliplr(inp)) or
                    np.array_equal(tile, np.flipud(inp)) or
                    np.array_equal(tile, np.rot90(inp))):
                return False
    return True

def check_reflection(inp: np.ndarray, out: np.ndarray) -> bool:
    """Check if output involves reflection."""
    return (np.array_equal(out, np.fliplr(inp)) or
            np.array_equal(out, np.flipud(inp)))

def check_rotation(inp: np.ndarray, out: np.ndarray) -> bool:
    """Check if output is rotation of input."""
    for k in [1, 2, 3]:
        if np.array_equal(out, np.rot90(inp, k)):
            return True
    return False

def check_color_swap(inp: np.ndarray, out: np.ndarray) -> bool:
    """Check if output is color-swapped input."""
    if inp.shape != out.shape:
        return False
    colors_in = set(inp.flatten())
    colors_out = set(out.flatten())
    return colors_in == colors_out and not np.array_equal(inp, out)

def check_fill_pattern(inp: np.ndarray, out: np.ndarray) -> bool:
    """Check if output fills regions of input."""
    # Simple check: more non-zero cells in output
    return np.sum(out > 0) > np.sum(inp > 0)

# =============================================================================
# SOLVER REGISTRY
# =============================================================================

SOLVERS: Dict[str, Callable] = {}

def register_solver(task_id: str):
    """Decorator to register a solver."""
    def decorator(func: Callable):
        SOLVERS[task_id] = func
        return func
    return decorator

# =============================================================================
# SOLVED TASKS - TRAINING SET
# =============================================================================

@register_solver("007bbfb7")
def solve_007bbfb7(task: ARCTask) -> List[List[List[int]]]:
    """
    Pattern: Self-tiling 3x3
    ITT: Φ (scalar pattern) → tiled expansion (Δ₃)
    
    Input NxN is used as a template, each non-zero cell becomes
    a copy of the input, zeros become zero-blocks
    """
    results = []
    for test in task.test:
        inp = np.array(test['input'])
        h, w = inp.shape
        output = np.zeros((h * h, w * w), dtype=int)
        
        for i in range(h):
            for j in range(w):
                if inp[i, j] != 0:
                    output[i*h:(i+1)*h, j*w:(j+1)*w] = inp
        
        results.append(output.tolist())
    return results

@register_solver("00d62c1b")
def solve_00d62c1b(task: ARCTask) -> List[List[List[int]]]:
    """
    Pattern: Fill enclosed regions (surrounded by 3s) with color 4
    ITT: L3 boundary detection + flood fill from exterior
    
    Regions of 0s that are completely enclosed by 3s get filled with 4.
    """
    results = []
    for test in task.test:
        inp = np.array(test['input'])
        output = inp.copy()
        h, w = inp.shape
        
        # Flood fill from edges to mark exterior cells
        exterior = np.zeros((h, w), dtype=bool)
        
        def flood_fill(start_i, start_j):
            stack = [(start_i, start_j)]
            while stack:
                i, j = stack.pop()
                if i < 0 or i >= h or j < 0 or j >= w:
                    continue
                if exterior[i, j] or inp[i, j] == 3:
                    continue
                exterior[i, j] = True
                stack.extend([(i+1, j), (i-1, j), (i, j+1), (i, j-1)])
        
        # Start flood fill from all edge cells
        for i in range(h):
            if inp[i, 0] != 3:
                flood_fill(i, 0)
            if inp[i, w-1] != 3:
                flood_fill(i, w-1)
        for j in range(w):
            if inp[0, j] != 3:
                flood_fill(0, j)
            if inp[h-1, j] != 3:
                flood_fill(h-1, j)
        
        # Cells that are 0 and not exterior are enclosed - fill with 4
        for i in range(h):
            for j in range(w):
                if inp[i, j] == 0 and not exterior[i, j]:
                    output[i, j] = 4
        
        results.append(output.tolist())
    return results

@register_solver("017c7c7b")
def solve_017c7c7b(task: ARCTask) -> List[List[List[int]]]:
    """
    Pattern: Find repeating pattern in input, color swap 1→2, output 3 repetitions
    ITT: L2 memory (period detection) + Δ₃ expansion
    
    Input always has 2 repetitions of a base pattern.
    Output is 3 repetitions of that pattern (with 1→2 swap).
    """
    results = []
    for test in task.test:
        inp = np.array(test['input'])
        h, w = inp.shape
        
        # Swap color 1 → 2
        swapped = inp.copy()
        swapped[swapped == 1] = 2
        
        # Find the base pattern (assume input has 2 repetitions, so period = h/2)
        period = h // 2
        base_pattern = swapped[:period, :]
        
        # Output is 3 repetitions
        output = np.tile(base_pattern, (3, 1))
        
        results.append(output.tolist())
    return results

# =============================================================================
# SOLVED TASKS - EVALUATION SET
# =============================================================================

@register_solver("00576224")
def solve_00576224(task: ARCTask) -> List[List[List[int]]]:
    """
    Pattern: Vertical reflection tiling 3x3
    ITT: Δ₂ (curl/reflection) + Δ₃ (expansion)
    
    Stack: [input, flip_lr(input), input] then tile 3x horizontally
    """
    results = []
    for test in task.test:
        inp = np.array(test['input'])
        flipped = np.fliplr(inp)
        stacked = np.vstack([inp, flipped, inp])
        result = np.tile(stacked, (1, 3))
        results.append(result.tolist())
    return results

@register_solver("009d5c81")
def solve_009d5c81(task: ARCTask) -> List[List[List[int]]]:
    """
    Pattern: Small indicator shape (color 1) determines recolor of large shape (color 8)
    ITT: L5 awareness (shape recognition) + L6 classification mapping
    
    The shape made by 1s determines what color the 8s become.
    Both 1s and 8s are transformed: 8→new_color, 1→0
    """
    results = []
    
    # Learn shape→color mapping from training
    shape_to_color = {}
    for pair in task.train:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        
        # Extract indicator shape (1s) as relative positions
        ones_mask = (inp == 1)
        ones_pos = list(zip(*np.where(ones_mask)))
        
        if ones_pos:
            min_r = min(p[0] for p in ones_pos)
            min_c = min(p[1] for p in ones_pos)
            # Create canonical shape signature
            shape_sig = tuple(sorted([(r-min_r, c-min_c) for r, c in ones_pos]))
            
            # Find what color 8s became
            eights_mask = (inp == 8)
            eights_pos = list(zip(*np.where(eights_mask)))
            if eights_pos:
                r, c = eights_pos[0]
                output_color = int(out[r, c])
                shape_to_color[shape_sig] = output_color
    
    for test in task.test:
        inp = np.array(test['input'])
        output = np.zeros_like(inp)
        
        # Extract indicator shape from test input
        ones_mask = (inp == 1)
        ones_pos = list(zip(*np.where(ones_mask)))
        
        if ones_pos:
            min_r = min(p[0] for p in ones_pos)
            min_c = min(p[1] for p in ones_pos)
            shape_sig = tuple(sorted([(r-min_r, c-min_c) for r, c in ones_pos]))
            output_color = shape_to_color.get(shape_sig, 2)  # default 2
        else:
            output_color = 2
        
        # Apply: 8 → output_color, everything else → 0
        output[inp == 8] = output_color
        
        results.append(output.tolist())
    return results

@register_solver("00dbd492")
def solve_00dbd492(task: ARCTask) -> List[List[List[int]]]:
    """
    Pattern: Fill interior of each rectangular frame based on interior size
    ITT: L3 boundary detection + L4 object separation + L6 size classification
    
    Multiple rectangular frames can exist. Each frame's interior gets filled
    with a color determined by the interior size.
    Preserves any 2s inside the frame.
    """
    results = []
    
    # Learn size-to-color mapping from ALL training examples
    size_to_color = {}
    for pair in task.train:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        h, w = inp.shape
        
        # Find all rectangular frames
        visited = np.zeros((h, w), dtype=bool)
        
        for start_r in range(h):
            for start_c in range(w):
                if inp[start_r, start_c] == 2 and not visited[start_r, start_c]:
                    # Try to find a rectangular frame starting here
                    # Look for top-left corner of a frame
                    # Frame has 2s on border, check if it's complete
                    
                    # Find extent of this 2-region (could be frame border)
                    # Simple approach: find bounding box of connected 2s
                    # Then check if it forms a valid frame
                    
                    # Find the frame bounds by scanning
                    for end_r in range(start_r + 2, h):
                        for end_c in range(start_c + 2, w):
                            # Check if (start_r, start_c) to (end_r, end_c) forms a frame
                            # Top edge
                            if not all(inp[start_r, c] == 2 for c in range(start_c, end_c + 1)):
                                continue
                            # Bottom edge
                            if not all(inp[end_r, c] == 2 for c in range(start_c, end_c + 1)):
                                continue
                            # Left edge
                            if not all(inp[r, start_c] == 2 for r in range(start_r, end_r + 1)):
                                continue
                            # Right edge
                            if not all(inp[r, end_c] == 2 for r in range(start_r, end_r + 1)):
                                continue
                            
                            # Valid frame found! Get interior size and fill color
                            int_h = end_r - start_r - 1
                            int_w = end_c - start_c - 1
                            
                            if int_h > 0 and int_w > 0:
                                # Find fill color from output
                                for ir in range(start_r + 1, end_r):
                                    for ic in range(start_c + 1, end_c):
                                        if out[ir, ic] != 2 and out[ir, ic] != 0:
                                            size_to_color[(int_h, int_w)] = int(out[ir, ic])
                                            break
                                
                                # Mark frame cells as visited
                                for r in range(start_r, end_r + 1):
                                    for c in range(start_c, end_c + 1):
                                        visited[r, c] = True
    
    for test in task.test:
        inp = np.array(test['input'])
        output = inp.copy()
        h, w = inp.shape
        
        # Find and fill all rectangular frames
        visited = np.zeros((h, w), dtype=bool)
        
        for start_r in range(h):
            for start_c in range(w):
                if inp[start_r, start_c] == 2 and not visited[start_r, start_c]:
                    for end_r in range(start_r + 2, h):
                        for end_c in range(start_c + 2, w):
                            # Check frame validity
                            valid = True
                            # Top and bottom edges
                            for c in range(start_c, end_c + 1):
                                if inp[start_r, c] != 2 or inp[end_r, c] != 2:
                                    valid = False
                                    break
                            if not valid:
                                continue
                            # Left and right edges
                            for r in range(start_r, end_r + 1):
                                if inp[r, start_c] != 2 or inp[r, end_c] != 2:
                                    valid = False
                                    break
                            if not valid:
                                continue
                            
                            # Valid frame! Fill interior
                            int_h = end_r - start_r - 1
                            int_w = end_c - start_c - 1
                            
                            fill_color = size_to_color.get((int_h, int_w), 4)
                            
                            for ir in range(start_r + 1, end_r):
                                for ic in range(start_c + 1, end_c):
                                    if inp[ir, ic] != 2:
                                        output[ir, ic] = fill_color
                            
                            # Mark as visited
                            for r in range(start_r, end_r + 1):
                                for c in range(start_c, end_c + 1):
                                    visited[r, c] = True
        
        results.append(output.tolist())
    return results

# =============================================================================
# GENERIC SOLVERS (Pattern-based)
# =============================================================================

def solve_by_tiling(task: ARCTask) -> Optional[List[List[List[int]]]]:
    """Generic tiling solver."""
    # Analyze training to detect tiling pattern
    train_in = np.array(task.train[0]['input'])
    train_out = np.array(task.train[0]['output'])
    
    ih, iw = train_in.shape
    oh, ow = train_out.shape
    
    if oh % ih != 0 or ow % iw != 0:
        return None
    
    tile_h = oh // ih
    tile_w = ow // iw
    
    results = []
    for test in task.test:
        inp = np.array(test['input'])
        result = np.tile(inp, (tile_h, tile_w))
        results.append(result.tolist())
    
    return results

def solve_by_reflection(task: ARCTask) -> Optional[List[List[List[int]]]]:
    """Generic reflection solver."""
    train_in = np.array(task.train[0]['input'])
    train_out = np.array(task.train[0]['output'])
    
    # Check which reflection matches
    if np.array_equal(train_out, np.fliplr(train_in)):
        results = []
        for test in task.test:
            inp = np.array(test['input'])
            results.append(np.fliplr(inp).tolist())
        return results
    
    if np.array_equal(train_out, np.flipud(train_in)):
        results = []
        for test in task.test:
            inp = np.array(test['input'])
            results.append(np.flipud(inp).tolist())
        return results
    
    return None

def solve_by_rotation(task: ARCTask) -> Optional[List[List[List[int]]]]:
    """Generic rotation solver."""
    train_in = np.array(task.train[0]['input'])
    train_out = np.array(task.train[0]['output'])
    
    for k in [1, 2, 3]:
        if np.array_equal(train_out, np.rot90(train_in, k)):
            results = []
            for test in task.test:
                inp = np.array(test['input'])
                results.append(np.rot90(inp, k).tolist())
            return results
    
    return None

def solve_identity(task: ARCTask) -> List[List[List[int]]]:
    """Fallback: return input unchanged."""
    return [test['input'] for test in task.test]

# =============================================================================
# MAIN SOLVER
# =============================================================================

def solve_task(task_id: str, task: ARCTask = None) -> SolverResult:
    """
    Main solving function.
    
    1. Check if we have a registered solver
    2. Try generic pattern detection
    3. Fall back to identity
    """
    if task is None:
        task = fetch_task(task_id)
        if task is None:
            return SolverResult(task_id=task_id, predictions=[], pattern_detected="TASK_NOT_FOUND")
    
    # 1. Check registered solvers
    if task_id in SOLVERS:
        try:
            predictions = SOLVERS[task_id](task)
            return SolverResult(
                task_id=task_id,
                predictions=predictions,
                pattern_detected="REGISTERED_SOLVER",
                itt_layer="L7"
            )
        except Exception as e:
            print(f"Registered solver failed: {e}")
    
    # 2. Analyze transformation pattern
    transform = detect_transformation(task.train)
    
    # 3. Try generic solvers based on detected pattern
    if transform['is_tiling']:
        result = solve_by_tiling(task)
        if result:
            return SolverResult(
                task_id=task_id,
                predictions=result,
                pattern_detected="TILING",
                itt_layer="L6"
            )
    
    if transform['is_reflection']:
        result = solve_by_reflection(task)
        if result:
            return SolverResult(
                task_id=task_id,
                predictions=result,
                pattern_detected="REFLECTION",
                itt_layer="L6"
            )
    
    if transform['is_rotation']:
        result = solve_by_rotation(task)
        if result:
            return SolverResult(
                task_id=task_id,
                predictions=result,
                pattern_detected="ROTATION",
                itt_layer="L6"
            )
    
    # 4. Fallback
    return SolverResult(
        task_id=task_id,
        predictions=solve_identity(task),
        pattern_detected="IDENTITY_FALLBACK",
        itt_layer="L0"
    )

def validate_result(result: SolverResult, task: ARCTask) -> bool:
    """Validate predictions against expected outputs."""
    if not result.predictions:
        return False
    
    for pred, test in zip(result.predictions, task.test):
        if 'output' not in test:
            continue  # Can't validate without expected output
        expected = test['output']
        if pred != expected:
            return False
    
    return True

# =============================================================================
# BATCH SOLVING
# =============================================================================

def solve_batch(task_ids: List[str], verbose: bool = True) -> Dict[str, SolverResult]:
    """Solve multiple tasks."""
    results = {}
    solved = 0
    
    for task_id in task_ids:
        task = fetch_task(task_id)
        if task is None:
            if verbose:
                print(f"  {task_id}: NOT FOUND")
            continue
        
        result = solve_task(task_id, task)
        results[task_id] = result
        
        # Validate if we have expected outputs
        is_valid = validate_result(result, task)
        result.correct = is_valid
        
        if is_valid:
            solved += 1
        
        if verbose:
            status = "✓" if is_valid else "✗"
            print(f"  {task_id}: {status} [{result.pattern_detected}]")
    
    if verbose:
        print(f"\nSolved: {solved}/{len(task_ids)} ({100*solved/len(task_ids):.1f}%)")
    
    return results

# =============================================================================
# CLI
# =============================================================================

def main():
    """Main entry point."""
    print("=" * 60)
    print("ARC-AGI SOLVER")
    print("Intent Tensor Theory Applied to Abstract Reasoning")
    print("=" * 60)
    print()
    
    # List registered solvers
    print(f"Registered Solvers: {len(SOLVERS)}")
    for task_id in sorted(SOLVERS.keys()):
        print(f"  - {task_id}")
    print()
    
    # Test registered solvers
    print("Testing registered solvers...")
    results = solve_batch(list(SOLVERS.keys()))
    
    # Summary
    print()
    print("=" * 60)
    correct = sum(1 for r in results.values() if r.correct)
    print(f"FINAL: {correct}/{len(results)} tasks solved correctly")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
