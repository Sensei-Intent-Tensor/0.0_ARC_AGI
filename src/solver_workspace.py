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
    
Current Progress: 6/1000 = 0.6%
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

# =============================================================================
# SOLVED TASKS REGISTRY
# =============================================================================

SOLVED_TASKS: Dict[str, Callable] = {}

def register_solver(task_id: str):
    """Decorator to register a solver for a specific task."""
    def decorator(func: Callable):
        SOLVED_TASKS[task_id] = func
        return func
    return decorator

# =============================================================================
# SOLVED TASK 1: 00576224
# Pattern: Vertical reflection tiling
# ITT: Δ₂ (curl/reflection) + Δ₃ (expansion)
# =============================================================================
@register_solver("00576224")
def solve_00576224(task: Dict) -> List[List[List[int]]]:
    """
    Task: 00576224
    
    Pattern: 
      - Stack vertically: [input, flip_lr(input), input]
      - Tile 3x horizontally
    
    Input (2x2) → Output (6x6)
    """
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        flipped = np.fliplr(inp)
        stacked = np.vstack([inp, flipped, inp])
        result = np.tile(stacked, (1, 3))
        predictions.append(result.tolist())
    return predictions

# =============================================================================
# SOLVED TASK 2: 007bbfb7
# Pattern: Self-similar tiling (fractal-like)
# ITT: Recursive self-reference - input IS the tiling map
# =============================================================================
@register_solver("007bbfb7")
def solve_007bbfb7(task: Dict) -> List[List[List[int]]]:
    """
    Task: 007bbfb7
    
    Pattern: For each non-zero cell (i,j) in input, place input at tile (i,j)
    
    Input (NxN) → Output (N²xN²)
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

# =============================================================================
# SOLVED TASK 3: 009d5c81
# Pattern: Shape-to-color indicator mapping
# ITT: Small shape ENCODES the target color (glyph → scalar)
# =============================================================================
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
        
        output_color = SHAPE_009d5c81.get(shape, 0)
        
        result = np.zeros_like(inp)
        result[inp == 8] = output_color
        
        predictions.append(result.tolist())
    return predictions

# =============================================================================
# SOLVED TASK 4: 00d62c1b
# Pattern: Fill enclosed regions
# ITT: Boundary detection + interior flood fill
# =============================================================================
@register_solver("00d62c1b")
def solve_00d62c1b(task: Dict) -> List[List[List[int]]]:
    """
    Task: 00d62c1b
    
    Pattern:
      - Color 3 forms boundaries
      - Empty regions (0) that don't touch grid edge get filled with color 4
    """
    from scipy.ndimage import label
    
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        result = inp.copy()
        
        zeros = (inp == 0).astype(int)
        labeled, _ = label(zeros)
        
        h, w = inp.shape
        border_labels = set()
        
        for j in range(w):
            if labeled[0, j] > 0: border_labels.add(labeled[0, j])
            if labeled[h-1, j] > 0: border_labels.add(labeled[h-1, j])
        for i in range(h):
            if labeled[i, 0] > 0: border_labels.add(labeled[i, 0])
            if labeled[i, w-1] > 0: border_labels.add(labeled[i, w-1])
        
        for i in range(h):
            for j in range(w):
                if labeled[i, j] > 0 and labeled[i, j] not in border_labels:
                    result[i, j] = 4
        
        predictions.append(result.tolist())
    return predictions

# =============================================================================
# SOLVED TASK 5: 00dbd492
# Pattern: Size-based color fill for enclosed regions
# ITT: σ magnitude (region size) → ρ_q (boundary color)
# =============================================================================
@register_solver("00dbd492")
def solve_00dbd492(task: Dict) -> List[List[List[int]]]:
    """
    Task: 00dbd492
    
    Pattern:
      - Find enclosed regions (don't touch border)
      - Assign color based on region SIZE:
        * size ≤ 12  → color 8
        * 12 < size ≤ 30 → color 4
        * size > 30 → color 3
    """
    from scipy.ndimage import label
    
    def size_to_color(size):
        if size <= 12:
            return 8
        elif size <= 30:
            return 4
        else:
            return 3
    
    predictions = []
    for test in task['test']:
        inp = np.array(test['input'])
        result = inp.copy()
        
        zeros = (inp == 0).astype(int)
        labeled, num = label(zeros)
        
        h, w = inp.shape
        border_labels = set()
        for j in range(w):
            if labeled[0, j] > 0: border_labels.add(labeled[0, j])
            if labeled[h-1, j] > 0: border_labels.add(labeled[h-1, j])
        for i in range(h):
            if labeled[i, 0] > 0: border_labels.add(labeled[i, 0])
            if labeled[i, w-1] > 0: border_labels.add(labeled[i, w-1])
        
        for lab in range(1, num+1):
            if lab not in border_labels:
                mask = labeled == lab
                size = np.sum(mask)
                result[mask] = size_to_color(size)
        
        predictions.append(result.tolist())
    return predictions

# =============================================================================
# SOLVED TASK 6: 017c7c7b
# Pattern: Extend periodic pattern to 9 rows, recolor
# ITT: Period detection + σ-continuation
# =============================================================================
@register_solver("017c7c7b")
def solve_017c7c7b(task: Dict) -> List[List[List[int]]]:
    """
    Task: 017c7c7b
    
    Pattern:
      - Find smallest period in input rows
      - Extend to 9 rows using that period
      - Change color 1 → 2
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
        
        analysis['color_counts'].append({
            'input_colors': len(np.unique(inp)),
            'output_colors': len(np.unique(out))
        })
    
    return analysis

def check_simple_transforms(task: Dict) -> Optional[str]:
    """Check if task is solved by simple geometric transform."""
    transforms = {
        'flip_horizontal': lambda x: np.fliplr(x),
        'flip_vertical': lambda x: np.flipud(x),
        'rotate_90': lambda x: np.rot90(x, 1),
        'rotate_180': lambda x: np.rot90(x, 2),
        'rotate_270': lambda x: np.rot90(x, 3),
        'transpose': lambda x: np.transpose(x),
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
    colors = ' ▪▫●○◆◇■□★☆'
    
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
    challenges_path = "/home/claude/arc_data/prize2025/arc-agi_training_challenges.json"
    solutions_path = "/home/claude/arc_data/prize2025/arc-agi_training_solutions.json"
    
    print(f"Loading from: {challenges_path}")
    challenges, solutions = load_tasks(challenges_path, solutions_path)
    print(f"Loaded {len(challenges)} tasks")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--next":
            for task_id in challenges:
                if task_id not in SOLVED_TASKS:
                    print(f"\nNext unsolved: {task_id}")
                    task = challenges[task_id]
                    visualize_task(task, task_id)
                    
                    simple = check_simple_transforms(task)
                    if simple:
                        print(f"\n✓ Simple transform detected: {simple}")
                    else:
                        print(f"\n✗ No simple transform found")
                    
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
            for task_id, success in sorted(results.items()):
                status = "✓" if success else "✗"
                print(f"  {status} {task_id}")

if __name__ == "__main__":
    main()
