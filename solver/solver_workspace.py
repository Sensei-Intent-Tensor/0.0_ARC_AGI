#!/usr/bin/env python3
"""
ARC-AGI Solver Workspace
========================

This is the working document where we solve ARC-AGI tasks one at a time.
Each solved task stays solved. We build up from zero.

Philosophy: "Zero assumptive smuggled-in things - it has to truly build and fill itself out."

Usage:
    python solver_workspace.py                    # Run all solved tasks, show stats
    python solver_workspace.py --task 00576224   # Work on specific task
    python solver_workspace.py --next            # Find next unsolved task
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import sys

# =============================================================================
# DATA LOADING
# =============================================================================

def load_tasks(challenges_path: str, solutions_path: str) -> Tuple[Dict, Dict]:
    """Load challenges and solutions from JSON files."""
    with open(challenges_path) as f:
        challenges = json.load(f)
    with open(solutions_path) as f:
        solutions = json.load(f)
    return challenges, solutions

def load_single_task(task_id: str, challenges: Dict) -> Dict:
    """Load a single task by ID."""
    if task_id not in challenges:
        raise ValueError(f"Task {task_id} not found")
    return challenges[task_id]

# =============================================================================
# CORE OPERATORS (ITT Fan Surfaces)
# =============================================================================

def compute_gradient(grid: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Δ₁: ∇Φ - Gradient (direction of change)"""
    grid = np.array(grid, dtype=float)
    dy = np.diff(grid, axis=0, prepend=grid[:1])
    dx = np.diff(grid, axis=1, prepend=grid[:, :1])
    return dy, dx

def compute_curl(grid: np.ndarray) -> np.ndarray:
    """Δ₂: ∇×F - Curl (rotational tendency)"""
    grid = np.array(grid, dtype=float)
    dy, dx = compute_gradient(grid)
    curl = np.roll(dx, -1, axis=0) - np.roll(dy, -1, axis=1)
    return curl

def compute_laplacian(grid: np.ndarray) -> np.ndarray:
    """Δ₃/Δ₄: ∇²Φ - Laplacian (curvature)"""
    grid = np.array(grid, dtype=float)
    laplacian = (
        np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
        np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid
    )
    return laplacian

# =============================================================================
# PRIMITIVE TRANSFORMATIONS
# =============================================================================

def identity(grid: np.ndarray) -> np.ndarray:
    """No change."""
    return grid.copy()

def flip_horizontal(grid: np.ndarray) -> np.ndarray:
    """Flip left-right."""
    return np.fliplr(grid)

def flip_vertical(grid: np.ndarray) -> np.ndarray:
    """Flip up-down."""
    return np.flipud(grid)

def rotate_90(grid: np.ndarray) -> np.ndarray:
    """Rotate 90° counterclockwise."""
    return np.rot90(grid, 1)

def rotate_180(grid: np.ndarray) -> np.ndarray:
    """Rotate 180°."""
    return np.rot90(grid, 2)

def rotate_270(grid: np.ndarray) -> np.ndarray:
    """Rotate 270° counterclockwise (90° clockwise)."""
    return np.rot90(grid, 3)

def transpose(grid: np.ndarray) -> np.ndarray:
    """Transpose (swap rows and columns)."""
    return np.transpose(grid)

def scale(grid: np.ndarray, sy: int, sx: int) -> np.ndarray:
    """Scale by repeating each cell."""
    return np.repeat(np.repeat(grid, sy, axis=0), sx, axis=1)

def color_map(grid: np.ndarray, mapping: Dict[int, int]) -> np.ndarray:
    """Replace colors according to mapping."""
    result = grid.copy()
    for old_val, new_val in mapping.items():
        result[grid == old_val] = new_val
    return result

# =============================================================================
# SOLVED TASKS REGISTRY
# Each entry: task_id -> solver function
# =============================================================================

SOLVED_TASKS: Dict[str, Callable] = {}

def register_solver(task_id: str):
    """Decorator to register a solver for a specific task."""
    def decorator(func: Callable):
        SOLVED_TASKS[task_id] = func
        return func
    return decorator

# =============================================================================
# TASK SOLVERS
# Add new solvers here as we solve tasks
# =============================================================================

# Example template:
# @register_solver("00576224")
# def solve_00576224(task: Dict) -> List[List[List[int]]]:
#     """
#     Task: 00576224
#     Pattern: [describe what you discovered]
#     ITT Analysis: [which fans activated, what boundary changed]
#     """
#     predictions = []
#     for test in task['test']:
#         inp = np.array(test['input'])
#         # Apply transformation
#         out = some_transformation(inp)
#         predictions.append(out.tolist())
#     return predictions

# -----------------------------------------------------------------------------
# SOLVED TASK: 00576224
# Pattern: Vertical reflection tiling
# ITT: Δ₂ (curl/reflection) + Δ₃ (expansion)
# Solved: 2025-12-27
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# SOLVED TASK: 017c7c7b
# Pattern: Extend periodic pattern to 9 rows, recolor
# ITT: Period detection + σ-continuation
# Solved: 2025-12-27
# -----------------------------------------------------------------------------
@register_solver("017c7c7b")
def solve_017c7c7b(task: Dict) -> List[List[List[int]]]:
    """
    Task: 017c7c7b
    
    Pattern:
      - Find smallest period in input rows
      - Extend to 9 rows using that period
      - Change color 1 → 2
    
    ITT Analysis:
      - σ (residue) carries the pattern forward
      - Period detection = finding the minimal generating set
      - Color change = boundary marking (Φ → Φ')
    """
    def find_period(arr):
        n = len(arr)
        for p in range(1, n+1):
            is_period = True
            for i in range(p, n):
                if not np.array_equal(arr[i], arr[i % p]):
                    is_period = False
                    break
            if is_period:
                return p
        return n
    
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        h, w = inp.shape
        
        period = find_period(inp)
        out_h = 9
        
        result = np.zeros((out_h, w), dtype=int)
        for r in range(out_h):
            row = inp[r % period].copy()
            row = np.where(row == 1, 2, row)
            result[r] = row
        
        predictions.append(result.tolist())
    return predictions

# -----------------------------------------------------------------------------
# SOLVED TASK: 00dbd492
# Pattern: Fill rectangles based on size
# ITT: Rectangle size → fill color mapping
# Solved: 2025-12-27
# -----------------------------------------------------------------------------
SIZE_TO_COLOR_00dbd492 = {5: 8, 7: 4, 9: 3}

@register_solver("00dbd492")
def solve_00dbd492(task: Dict) -> List[List[List[int]]]:
    """
    Task: 00dbd492
    
    Pattern:
      - Find rectangles made of color 2
      - Fill interior with color based on rectangle size
      - 5x5 → 8, 7x7 → 4, 9x9 → 3
    
    ITT Analysis:
      - Δ₄ (compression): size encodes color
      - Boundary detection + interior fill
    """
    from scipy.ndimage import label
    
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        result = inp.copy()
        
        # Find rectangles
        boundary = (inp == 2).astype(int)
        labeled, num = label(boundary, structure=np.ones((3,3)))
        
        for comp in range(1, num+1):
            mask = labeled == comp
            if np.sum(mask) < 8:
                continue
            rows = np.where(np.any(mask, axis=1))[0]
            cols = np.where(np.any(mask, axis=0))[0]
            if len(rows) < 3 or len(cols) < 3:
                continue
            
            r0, r1 = rows[0], rows[-1]
            c0, c1 = cols[0], cols[-1]
            h = r1 - r0 + 1
            w = c1 - c0 + 1
            
            if h >= 5 and w >= 5:
                size = max(h, w)
                fill_color = SIZE_TO_COLOR_00dbd492.get(size, 0)
                
                for r in range(r0+1, r1):
                    for c in range(c0+1, c1):
                        if inp[r, c] == 0:
                            result[r, c] = fill_color
        
        predictions.append(result.tolist())
    return predictions

# -----------------------------------------------------------------------------
# SOLVED TASK: 00d62c1b
# Pattern: Fill enclosed regions
# ITT: Boundary detection + interior flood fill
# Solved: 2025-12-27
# -----------------------------------------------------------------------------
@register_solver("00d62c1b")
def solve_00d62c1b(task: Dict) -> List[List[List[int]]]:
    """
    Task: 00d62c1b
    
    Pattern:
      - Color 3 forms boundaries
      - Empty regions (0) that don't touch grid edge get filled with color 4
      - Connected components analysis
    
    ITT Analysis:
      - Boundary detection: ρ_q at termination surfaces
      - Δ₄ (compression): interior space is marked/claimed
      - Topological: "inside" vs "outside" classification
    """
    from scipy.ndimage import label
    
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        result = inp.copy()
        
        # Find connected components of 0s
        zeros = (inp == 0).astype(int)
        labeled, _ = label(zeros)
        
        # Find labels that touch the border
        h, w = inp.shape
        border_labels = set()
        
        for j in range(w):
            if labeled[0, j] > 0:
                border_labels.add(labeled[0, j])
            if labeled[h-1, j] > 0:
                border_labels.add(labeled[h-1, j])
        for i in range(h):
            if labeled[i, 0] > 0:
                border_labels.add(labeled[i, 0])
            if labeled[i, w-1] > 0:
                border_labels.add(labeled[i, w-1])
        
        # Fill interior regions
        for i in range(h):
            for j in range(w):
                if labeled[i, j] > 0 and labeled[i, j] not in border_labels:
                    result[i, j] = 4
        
        predictions.append(result.tolist())
    return predictions

# -----------------------------------------------------------------------------
# SOLVED TASK: 009d5c81
# Pattern: Shape-to-color indicator mapping
# ITT: Small shape ENCODES the target color (glyph → scalar)
# Solved: 2025-12-27
# -----------------------------------------------------------------------------
# Shape templates for color lookup
SHAPE_009d5c81 = {
    ((1,1,1), (1,0,1), (0,1,0)): 7,  # Down arrow
    ((1,0,1), (0,1,0), (1,1,1)): 3,  # Up arrow
    ((0,1,0), (1,1,1), (0,1,0)): 2,  # Plus sign
}

@register_solver("009d5c81")
def solve_009d5c81(task: Dict) -> List[List[List[int]]]:
    """
    Task: 009d5c81
    
    Pattern:
      - Color 1 = indicator (small shape that encodes target color)
      - Color 8 = main shape (gets recolored)
      - Indicator shape maps to output color
      - Remove indicator, recolor main shape
    
    ITT Analysis:
      - Δ₆ activated: glyph shape → scalar color mapping
      - This is ENCODING: geometric form carries semantic value
      - The indicator is a "key" that unlocks the color
    """
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        
        # Extract indicator shape
        mask = inp == 1
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        r_min, r_max = np.where(rows)[0][[0, -1]]
        c_min, c_max = np.where(cols)[0][[0, -1]]
        region = inp[r_min:r_max+1, c_min:c_max+1]
        shape = tuple(tuple((region == 1).astype(int)[i]) for i in range(region.shape[0]))
        
        # Map to color
        output_color = SHAPE_009d5c81.get(shape, 0)
        
        # Create output
        result = np.zeros_like(inp)
        result[inp == 8] = output_color
        
        predictions.append(result.tolist())
    return predictions

# -----------------------------------------------------------------------------
# SOLVED TASK: 007bbfb7
# Pattern: Self-similar tiling (fractal-like)
# ITT: Recursive self-reference - input IS the tiling map
# Solved: 2025-12-27
# -----------------------------------------------------------------------------
@register_solver("007bbfb7")
def solve_007bbfb7(task: Dict) -> List[List[List[int]]]:
    """
    Task: 007bbfb7
    
    Pattern: For each non-zero cell (i,j) in input, place input at tile (i,j)
    
    Input (NxN) → Output (N²xN²)
    
    ITT Analysis:
      - Δ₃ activated: N² expansion
      - Δ₆ activated: scalar value determines placement
      - Self-reference: input encodes its own tiling structure
      - This is a FRACTAL operation - the input describes where to put copies of itself
    """
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        h, w = inp.shape
        result = np.zeros((h*h, w*w), dtype=int)
        
        for i in range(h):
            for j in range(w):
                if inp[i, j] != 0:
                    result[i*h:(i+1)*h, j*w:(j+1)*w] = inp
        
        predictions.append(result.tolist())
    return predictions

@register_solver("00576224")
def solve_00576224(task: Dict) -> List[List[List[int]]]:
    """
    Task: 00576224
    
    Pattern: 
      - Stack vertically: [input, flip_lr(input), input]
      - Tile 3x horizontally
    
    Input (2x2) → Output (6x6)
    
    ITT Analysis:
      - Δ₂ activated: horizontal reflection in middle section
      - Δ₃ activated: 3x expansion in both dimensions
      - Bridge tensor: Δ₂◊Δ₃ (reflection composes with expansion)
    """
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        flipped = np.fliplr(inp)
        
        # Stack vertically: original, flipped, original
        stacked = np.vstack([inp, flipped, inp])
        
        # Tile 3x horizontally
        result = np.tile(stacked, (1, 3))
        
        predictions.append(result.tolist())
    return predictions


# =============================================================================
# TESTING & VALIDATION
# =============================================================================

def test_solver(task_id: str, challenges: Dict, solutions: Dict) -> bool:
    """Test a solver against known solution."""
    if task_id not in SOLVED_TASKS:
        return False
    
    task = challenges[task_id]
    expected = solutions[task_id]
    
    try:
        predictions = SOLVED_TASKS[task_id](task)
        
        for pred, exp in zip(predictions, expected):
            if pred != exp:
                return False
        return True
    except Exception as e:
        print(f"Error in solver for {task_id}: {e}")
        return False

def run_all_tests(challenges: Dict, solutions: Dict) -> Dict[str, bool]:
    """Run all registered solvers and return results."""
    results = {}
    for task_id in SOLVED_TASKS:
        results[task_id] = test_solver(task_id, challenges, solutions)
    return results

# =============================================================================
# ANALYSIS HELPERS
# =============================================================================

def analyze_task(task: Dict) -> Dict:
    """Analyze a task to understand its structure."""
    analysis = {
        'num_train': len(task['train']),
        'num_test': len(task['test']),
        'train_shapes': [],
        'shape_changes': [],
        'color_counts': [],
    }
    
    for pair in task['train']:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        
        analysis['train_shapes'].append({
            'input': inp.shape,
            'output': out.shape,
            'same_shape': inp.shape == out.shape
        })
        
        if inp.shape == out.shape:
            analysis['shape_changes'].append('same')
        elif inp.size < out.size:
            analysis['shape_changes'].append('grow')
        else:
            analysis['shape_changes'].append('shrink')
        
        analysis['color_counts'].append({
            'input_colors': len(np.unique(inp)),
            'output_colors': len(np.unique(out))
        })
    
    return analysis

def check_simple_transforms(task: Dict) -> Optional[str]:
    """Check if task is solved by simple geometric transform."""
    transforms = {
        'flip_horizontal': flip_horizontal,
        'flip_vertical': flip_vertical,
        'rotate_90': rotate_90,
        'rotate_180': rotate_180,
        'rotate_270': rotate_270,
        'transpose': transpose,
    }
    
    for name, fn in transforms.items():
        all_match = True
        for pair in task['train']:
            inp = np.array(pair['input'])
            out = np.array(pair['output'])
            try:
                result = fn(inp)
                if result.shape != out.shape or not np.array_equal(result, out):
                    all_match = False
                    break
            except:
                all_match = False
                break
        
        if all_match:
            return name
    
    return None

def visualize_task(task: Dict, task_id: str = ""):
    """Print ASCII visualization of a task."""
    colors = ' ▪▫●○◆◇■□★☆'  # 0-9
    
    print(f"\n{'='*60}")
    print(f"Task: {task_id}")
    print(f"{'='*60}")
    
    for i, pair in enumerate(task['train']):
        inp = np.array(pair['input'])
        out = np.array(pair['output'])
        
        print(f"\nTraining {i+1}:")
        print(f"Input ({inp.shape[0]}x{inp.shape[1]}):")
        for row in inp:
            print('  ' + ''.join(colors[v] if v < len(colors) else '?' for v in row))
        
        print(f"Output ({out.shape[0]}x{out.shape[1]}):")
        for row in out:
            print('  ' + ''.join(colors[v] if v < len(colors) else '?' for v in row))
    
    print(f"\nTest inputs: {len(task['test'])}")
    for i, test in enumerate(task['test']):
        inp = np.array(test['input'])
        print(f"\nTest {i+1} ({inp.shape[0]}x{inp.shape[1]}):")
        for row in inp:
            print('  ' + ''.join(colors[v] if v < len(colors) else '?' for v in row))

# =============================================================================
# MAIN
# =============================================================================

def main():
    # Load data
    data_dir = Path(__file__).parent / "data"
    
    # Try local data first, fall back to downloaded data
    if (data_dir / "arc-agi_training_challenges.json").exists():
        challenges_path = data_dir / "arc-agi_training_challenges.json"
        solutions_path = data_dir / "arc-agi_training_solutions.json"
    else:
        # Use absolute path for testing
        challenges_path = "/home/claude/arc_data/prize2025/arc-agi_training_challenges.json"
        solutions_path = "/home/claude/arc_data/prize2025/arc-agi_training_solutions.json"
    
    print(f"Loading from: {challenges_path}")
    challenges, solutions = load_tasks(str(challenges_path), str(solutions_path))
    print(f"Loaded {len(challenges)} tasks")
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--next":
            # Find next unsolved task
            for task_id in challenges:
                if task_id not in SOLVED_TASKS:
                    print(f"\nNext unsolved: {task_id}")
                    task = challenges[task_id]
                    visualize_task(task, task_id)
                    
                    # Check simple transforms
                    simple = check_simple_transforms(task)
                    if simple:
                        print(f"\n✓ Simple transform detected: {simple}")
                    else:
                        print(f"\n✗ No simple transform found")
                    
                    # Show analysis
                    analysis = analyze_task(task)
                    print(f"\nAnalysis: {analysis}")
                    break
        
        elif sys.argv[1] == "--task":
            if len(sys.argv) < 3:
                print("Usage: --task TASK_ID")
                return
            task_id = sys.argv[2]
            if task_id in challenges:
                task = challenges[task_id]
                visualize_task(task, task_id)
                
                simple = check_simple_transforms(task)
                if simple:
                    print(f"\n✓ Simple transform: {simple}")
                
                analysis = analyze_task(task)
                print(f"\nAnalysis: {analysis}")
                
                if task_id in solutions:
                    print(f"\nExpected output for test 0:")
                    out = np.array(solutions[task_id][0])
                    colors = ' ▪▫●○◆◇■□★☆'
                    for row in out:
                        print('  ' + ''.join(colors[v] if v < len(colors) else '?' for v in row))
            else:
                print(f"Task {task_id} not found")
        
        else:
            print("Unknown argument")
            print("Usage:")
            print("  python solver_workspace.py           # Run all tests")
            print("  python solver_workspace.py --next    # Show next unsolved")
            print("  python solver_workspace.py --task ID # Analyze specific task")
    
    else:
        # Run all tests
        print(f"\n{'='*60}")
        print("SOLVER STATUS")
        print(f"{'='*60}")
        
        results = run_all_tests(challenges, solutions)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        print(f"\nRegistered solvers: {total}")
        print(f"Passing: {passed}")
        print(f"Total tasks: {len(challenges)}")
        print(f"Progress: {passed}/{len(challenges)} = {100*passed/len(challenges):.1f}%")
        
        if results:
            print(f"\nResults:")
            for task_id, passed in results.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {task_id}")

if __name__ == "__main__":
    main()
