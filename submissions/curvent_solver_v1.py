# --- ARC Curvent Field Theory Solver ---
# Integrates gradient, curl, and curvature processors for symmetry detection

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from copy import deepcopy

# ============================================
# CURVENT FIELD PROCESSORS
# ============================================

def compute_gradient(grid):
    """∇Φ - Discrete gradient capturing value flow direction"""
    grid = np.array(grid, dtype=float)
    dy = np.diff(grid, axis=0, prepend=grid[:1])
    dx = np.diff(grid, axis=1, prepend=grid[:, :1])
    return dy, dx

def compute_curl(grid):
    """∇×F - Curl captures rotational/swap symmetry

    In 2D discrete fields, curl measures local rotation tendency.
    High curl magnitude at boundaries indicates reflection/swap patterns.
    """
    grid = np.array(grid, dtype=float)
    dy, dx = compute_gradient(grid)

    # Curl in 2D: ∂Fx/∂y - ∂Fy/∂x
    # Using roll to compute cross-derivatives
    curl = np.roll(dx, -1, axis=0) - np.roll(dy, -1, axis=1)
    return curl

def compute_curvature(grid):
    """∇²Φ - Laplacian for detecting stable/anchor regions"""
    grid = np.array(grid, dtype=float)
    laplacian = (
        np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
        np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid
    )
    return laplacian

def compute_symmetry_tensor(grid):
    """Compute symmetry metrics using field operators"""
    grid = np.array(grid, dtype=float)
    curl = compute_curl(grid)

    # Symmetry scores
    h, w = grid.shape

    # Horizontal flip symmetry: compare grid with fliplr
    flip_lr_diff = np.sum(np.abs(grid - np.fliplr(grid)))
    flip_lr_score = 1.0 / (1.0 + flip_lr_diff)

    # Vertical flip symmetry
    flip_ud_diff = np.sum(np.abs(grid - np.flipud(grid)))
    flip_ud_score = 1.0 / (1.0 + flip_ud_diff)

    # 180° rotation symmetry
    rot180_diff = np.sum(np.abs(grid - np.rot90(grid, 2)))
    rot180_score = 1.0 / (1.0 + rot180_diff)

    # 90° rotation symmetry (only for square grids)
    if h == w:
        rot90_diff = np.sum(np.abs(grid - np.rot90(grid, 1)))
        rot90_score = 1.0 / (1.0 + rot90_diff)
    else:
        rot90_score = 0.0

    # Curl asymmetry - high values indicate transformation potential
    curl_magnitude = np.mean(np.abs(curl))

    return {
        'flip_lr': flip_lr_score,
        'flip_ud': flip_ud_score,
        'rot90': rot90_score,
        'rot180': rot180_score,
        'curl_magnitude': curl_magnitude
    }

# ============================================
# TRANSFORMATION DETECTION
# ============================================

def detect_transformation(input_grid, output_grid):
    """Use Curvent field analysis to detect transformation type"""
    inp = np.array(input_grid)
    out = np.array(output_grid)

    # Direct transformations
    if np.array_equal(out, np.fliplr(inp)):
        return ('flip_lr', None)

    if np.array_equal(out, np.flipud(inp)):
        return ('flip_ud', None)

    if np.array_equal(out, np.rot90(inp, 1)):
        return ('rot90', 1)

    if np.array_equal(out, np.rot90(inp, 2)):
        return ('rot180', None)

    if np.array_equal(out, np.rot90(inp, 3)):
        return ('rot270', None)

    if np.array_equal(out, np.transpose(inp)):
        return ('transpose', None)

    # Value mapping detection
    value_map = detect_value_mapping(inp, out)
    if value_map:
        return ('value_map', value_map)

    # Positional shift detection
    shift = detect_shift(inp, out)
    if shift != (0, 0):
        return ('shift', shift)

    # Scale detection
    scale = detect_scale(inp, out)
    if scale:
        return ('scale', scale)

    # Block swap detection using curl
    swap = detect_block_swap_curl(inp, out)
    if swap:
        return ('block_swap', swap)

    return ('unknown', None)

def detect_value_mapping(inp, out):
    """Detect color/value replacement patterns"""
    if inp.shape != out.shape:
        return None

    mapping = {}
    for i in range(inp.shape[0]):
        for j in range(inp.shape[1]):
            iv, ov = inp[i, j], out[i, j]
            if iv in mapping:
                if mapping[iv] != ov:
                    return None  # Inconsistent mapping
            else:
                mapping[iv] = ov

    # Check if it's a non-trivial mapping
    if all(k == v for k, v in mapping.items()):
        return None

    return mapping

def detect_shift(inp, out):
    """Detect if output is shifted version of input"""
    if inp.shape != out.shape:
        return (0, 0)

    # Try all possible shifts
    h, w = inp.shape
    for dy in range(-h+1, h):
        for dx in range(-w+1, w):
            shifted = np.roll(np.roll(inp, dy, axis=0), dx, axis=1)
            if np.array_equal(shifted, out):
                return (dy, dx)

    return (0, 0)

def detect_scale(inp, out):
    """Detect scaling transformations"""
    ih, iw = inp.shape
    oh, ow = out.shape

    if oh % ih == 0 and ow % iw == 0:
        sy, sx = oh // ih, ow // iw
        # Verify by tiling
        tiled = np.repeat(np.repeat(inp, sy, axis=0), sx, axis=1)
        if np.array_equal(tiled, out):
            return (sy, sx)

    return None

def detect_block_swap_curl(inp, out):
    """Use curl field to detect block swap patterns

    Key insight: When blocks swap, the curl field shows
    opposite-sign vorticity at the swap boundaries.
    """
    curl_in = compute_curl(inp)
    curl_out = compute_curl(out)

    # If curl patterns are mirror-inverted, blocks swapped
    curl_diff = curl_in + np.fliplr(curl_out)
    if np.sum(np.abs(curl_diff)) < 0.1 * np.sum(np.abs(curl_in) + np.abs(curl_out)):
        return 'horizontal_swap'

    curl_diff = curl_in + np.flipud(curl_out)
    if np.sum(np.abs(curl_diff)) < 0.1 * np.sum(np.abs(curl_in) + np.abs(curl_out)):
        return 'vertical_swap'

    return None

# ============================================
# TRANSFORMATION APPLICATION
# ============================================

def apply_transformation(grid, transform_type, param):
    """Apply detected transformation to a grid"""
    grid = np.array(grid)

    if transform_type == 'flip_lr':
        return np.fliplr(grid)

    elif transform_type == 'flip_ud':
        return np.flipud(grid)

    elif transform_type == 'rot90':
        return np.rot90(grid, 1)

    elif transform_type == 'rot180':
        return np.rot90(grid, 2)

    elif transform_type == 'rot270':
        return np.rot90(grid, 3)

    elif transform_type == 'transpose':
        return np.transpose(grid)

    elif transform_type == 'value_map':
        result = grid.copy()
        for old_val, new_val in param.items():
            result[grid == old_val] = new_val
        return result

    elif transform_type == 'shift':
        dy, dx = param
        return np.roll(np.roll(grid, dy, axis=0), dx, axis=1)

    elif transform_type == 'scale':
        sy, sx = param
        return np.repeat(np.repeat(grid, sy, axis=0), sx, axis=1)

    elif transform_type == 'block_swap':
        if param == 'horizontal_swap':
            return np.fliplr(grid)
        elif param == 'vertical_swap':
            return np.flipud(grid)

    # Unknown - return as-is
    return grid

# ============================================
# MAIN SOLVER
# ============================================

def solve_arc_curvent(task):
    """Solve ARC task using Curvent Field Theory"""
    train_pairs = task['train']
    test_inputs = [np.array(t['input']) for t in task['test']]

    # Analyze all training pairs to find consistent transformation
    detected_transforms = []

    for pair in train_pairs:
        inp = np.array(pair['input'])
        out = np.array(pair['output'])

        transform = detect_transformation(inp, out)
        detected_transforms.append(transform)

        # Debug output
        print(f"  Training pair: {inp.shape} → {out.shape}")
        print(f"    Detected: {transform[0]}, param: {transform[1]}")

        # Show symmetry tensor
        sym = compute_symmetry_tensor(inp)
        print(f"    Symmetry: flip_lr={sym['flip_lr']:.3f}, flip_ud={sym['flip_ud']:.3f}")

    # Find consensus transformation
    transform_types = [t[0] for t in detected_transforms]
    if len(set(transform_types)) == 1:
        # All pairs agree on transformation type
        final_transform = detected_transforms[0]
        print(f"\n✓ Consensus transformation: {final_transform[0]}")
    else:
        # Take most common or first valid
        from collections import Counter
        most_common = Counter(transform_types).most_common(1)[0][0]
        for t in detected_transforms:
            if t[0] == most_common:
                final_transform = t
                break
        print(f"\n⚠ Mixed transforms, using: {final_transform[0]}")

    # Apply to test inputs
    predictions = []
    for test_grid in test_inputs:
        pred = apply_transformation(test_grid, final_transform[0], final_transform[1])
        predictions.append(pred.tolist())

    return predictions

# ============================================
# VISUALIZATION
# ============================================

def plot_grids(input_grid, pred_grid, title_prefix=""):
    """Display input and predicted output side by side"""
    fig, axs = plt.subplots(1, 2, figsize=(8, 4))
    cmap = plt.colormaps.get_cmap('tab10')

    axs[0].imshow(input_grid, cmap=cmap, vmin=0, vmax=9)
    axs[0].set_title(f"{title_prefix}Test Input")
    axs[0].axis('off')

    axs[1].imshow(pred_grid, cmap=cmap, vmin=0, vmax=9)
    axs[1].set_title(f"{title_prefix}Predicted Output")
    axs[1].axis('off')

    plt.tight_layout()
    plt.show()

def plot_curvent_analysis(grid, title="Curvent Analysis"):
    """Visualize the Curvent field components"""
    grid = np.array(grid, dtype=float)

    dy, dx = compute_gradient(grid)
    curl = compute_curl(grid)
    curv = compute_curvature(grid)

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Original
    cmap = plt.colormaps.get_cmap('tab10')
    axs[0, 0].imshow(grid, cmap=cmap, vmin=0, vmax=9)
    axs[0, 0].set_title('Original Grid')
    axs[0, 0].axis('off')

    # Gradient magnitude
    grad_mag = np.sqrt(dy**2 + dx**2)
    axs[0, 1].imshow(grad_mag, cmap='viridis')
    axs[0, 1].set_title('|∇Φ| Gradient Magnitude')
    axs[0, 1].axis('off')

    # Curl
    axs[1, 0].imshow(curl, cmap='RdBu', vmin=-np.max(np.abs(curl)), vmax=np.max(np.abs(curl)))
    axs[1, 0].set_title('∇×F Curl (Rotation Field)')
    axs[1, 0].axis('off')

    # Curvature
    axs[1, 1].imshow(curv, cmap='RdBu', vmin=-np.max(np.abs(curv)), vmax=np.max(np.abs(curv)))
    axs[1, 1].set_title('∇²Φ Curvature (Laplacian)')
    axs[1, 1].axis('off')

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

# ============================================
# TEST CASES
# ============================================

if __name__ == "__main__":
    # Test: Horizontal swap (your failing case)
    test_swap = {
        "train": [
            {"input": [[1, 0, 2], [1, 0, 2], [0, 0, 0]],
             "output": [[2, 0, 1], [2, 0, 1], [0, 0, 0]]},
            {"input": [[3, 0, 4], [3, 0, 4], [0, 0, 0]],
             "output": [[4, 0, 3], [4, 0, 3], [0, 0, 0]]}
        ],
        "test": [{"input": [[5, 0, 6], [5, 0, 6], [0, 0, 0]]}]
    }

    print("=" * 50)
    print("TEST: Horizontal Swap Detection")
    print("=" * 50)

    predictions = solve_arc_curvent(test_swap)

    print("\n📊 Results:")
    for i, (test, pred) in enumerate(zip(test_swap['test'], predictions)):
        print(f"\nTest {i+1}:")
        print(f"  Input:    {test['input']}")
        print(f"  Predicted: {pred}")
        print(f"  Expected:  [[6, 0, 5], [6, 0, 5], [0, 0, 0]]")

        plot_grids(np.array(test['input']), np.array(pred))

    # Visualize Curvent fields
    print("\n" + "=" * 50)
    print("CURVENT FIELD ANALYSIS")
    print("=" * 50)
    plot_curvent_analysis(test_swap['train'][0]['input'], "Input Field Analysis")
