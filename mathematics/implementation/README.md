# Implementation: From Theory to Code

**Code-Ready Specifications for the ITT-ARC Solver**

---

## The Algorithm

```
For each ARC task:
  1. DETECT: Compute fan activations from training pairs
  2. ANALYZE: Evaluate bridge tensors for composite operations
  3. SYNTHESIZE: Generate minimal program from active fans
  4. EXECUTE: Apply program to test inputs
  5. VERIFY: Check against any known constraints
```

---

## Step 1: Fan Detection

### Input Processing

```python
import numpy as np
from scipy import ndimage

def preprocess_grid(grid):
    """Convert ARC grid to scalar field."""
    return np.array(grid, dtype=np.float32)

def compute_delta_phi(phi_in, phi_out):
    """Compute the transformation field."""
    # Handle size differences
    h_out, w_out = phi_out.shape
    h_in, w_in = phi_in.shape
    
    if (h_out, w_out) != (h_in, w_in):
        # Size change detected - this is information
        return phi_out, {'scale': (h_out/h_in, w_out/w_in)}
    
    return phi_out - phi_in, {}
```

### Fan Activation Computation

```python
def compute_all_fan_activations(phi_in, phi_out):
    """Compute activation levels for all six fans."""
    
    delta, metadata = compute_delta_phi(phi_in, phi_out)
    
    activations = {}
    
    # Δ₁: Gradient (translation)
    grad_y, grad_x = np.gradient(delta)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    activations['D1'] = {
        'value': np.mean(grad_mag),
        'direction': (np.mean(grad_x), np.mean(grad_y)),
        'threshold': 0.1
    }
    
    # Δ₂: Curl (rotation)
    curl = np.gradient(grad_x, axis=0) - np.gradient(grad_y, axis=1)
    activations['D2'] = {
        'value': np.mean(np.abs(curl)),
        'sign': np.sign(np.mean(curl)),
        'threshold': 0.05
    }
    
    # Δ₃: Positive Laplacian (expansion)
    laplacian = ndimage.laplace(delta.astype(float))
    activations['D3'] = {
        'value': np.mean(np.maximum(laplacian, 0)),
        'regions': laplacian > 0,
        'threshold': 0.1
    }
    
    # Δ₄: Negative Laplacian (compression)
    activations['D4'] = {
        'value': np.mean(np.maximum(-laplacian, 0)),
        'regions': laplacian < 0,
        'threshold': 0.1
    }
    
    # Δ₅: Temporal (needs multiple pairs - placeholder)
    activations['D5'] = {
        'value': 0.0,
        'threshold': 0.1
    }
    
    # Δ₆: Scalar root (identity preservation)
    unchanged = np.sum(phi_in == phi_out)
    activations['D6'] = {
        'value': unchanged / phi_in.size,
        'mask': phi_in == phi_out,
        'threshold': 0.3
    }
    
    # Add scale metadata
    if 'scale' in metadata:
        activations['scale_factor'] = metadata['scale']
        activations['D3']['value'] = max(metadata['scale']) - 1
    
    return activations
```

### Active Fan Identification

```python
def identify_active_fans(activations):
    """Determine which fans are active (above threshold)."""
    active = []
    
    for fan in ['D1', 'D2', 'D3', 'D4', 'D5', 'D6']:
        if activations[fan]['value'] > activations[fan]['threshold']:
            active.append(fan)
    
    return active
```

---

## Step 2: Bridge Tensor Analysis

```python
def compute_bridge_tensors(phi_in, phi_out, active_fans, activations):
    """Compute interaction tensors between active fans."""
    
    bridges = {}
    
    for i, fan_i in enumerate(active_fans):
        for j, fan_j in enumerate(active_fans):
            if i >= j:
                continue
            
            key = f"B_{fan_i}_{fan_j}"
            
            # Get fan-specific fields
            field_i = get_fan_field(phi_in, phi_out, fan_i, activations)
            field_j = get_fan_field(phi_in, phi_out, fan_j, activations)
            
            # Compute correlation
            if field_i.shape == field_j.shape:
                corr = np.corrcoef(field_i.flatten(), field_j.flatten())[0, 1]
            else:
                corr = 0.0
            
            bridges[key] = {
                'correlation': corr,
                'order': infer_fan_order(phi_in, phi_out, fan_i, fan_j)
            }
    
    return bridges

def get_fan_field(phi_in, phi_out, fan, activations):
    """Extract the field associated with a specific fan."""
    delta = phi_out - phi_in
    
    if fan == 'D1':
        grad_y, grad_x = np.gradient(delta)
        return np.sqrt(grad_x**2 + grad_y**2)
    elif fan == 'D2':
        grad_y, grad_x = np.gradient(delta)
        return np.gradient(grad_x, axis=0) - np.gradient(grad_y, axis=1)
    elif fan == 'D3':
        return np.maximum(ndimage.laplace(delta.astype(float)), 0)
    elif fan == 'D4':
        return np.maximum(-ndimage.laplace(delta.astype(float)), 0)
    elif fan == 'D6':
        return (phi_in == phi_out).astype(float)
    else:
        return delta
```

---

## Step 3: Program Synthesis

```python
def synthesize_program(active_fans, bridges, activations):
    """Generate executable program from fan analysis."""
    
    program = []
    
    # Sort fans by dependency order using bridges
    ordered_fans = topological_sort_fans(active_fans, bridges)
    
    for fan in ordered_fans:
        op = fan_to_operation(fan, activations)
        if op:
            program.append(op)
    
    return program

def fan_to_operation(fan, activations):
    """Convert fan activation to primitive operation."""
    
    if fan == 'D1':
        dx, dy = activations['D1']['direction']
        if abs(dx) > 0.5 or abs(dy) > 0.5:
            return ('translate', int(round(dx)), int(round(dy)))
    
    elif fan == 'D2':
        if activations['D2']['sign'] > 0:
            return ('rotate', 90)
        elif activations['D2']['sign'] < 0:
            return ('rotate', -90)
        # Could also be reflection
        return ('reflect', 'detect_axis')
    
    elif fan == 'D3':
        if 'scale_factor' in activations:
            sy, sx = activations['scale_factor']
            return ('scale', int(round(sy)), int(round(sx)))
        return ('expand', 'detect_pattern')
    
    elif fan == 'D4':
        return ('crop', 'detect_region')
    
    elif fan == 'D6':
        # Check for color mapping
        return ('preserve', activations['D6']['mask'])
    
    return None
```

---

## Step 4: Program Execution

```python
def execute_program(phi_in, program):
    """Apply synthesized program to input."""
    
    result = phi_in.copy()
    
    for op in program:
        if op[0] == 'translate':
            _, dx, dy = op
            result = np.roll(np.roll(result, dy, axis=0), dx, axis=1)
        
        elif op[0] == 'rotate':
            _, angle = op
            k = angle // 90
            result = np.rot90(result, k)
        
        elif op[0] == 'reflect':
            _, axis = op
            if axis == 'x':
                result = np.flipud(result)
            elif axis == 'y':
                result = np.fliplr(result)
        
        elif op[0] == 'scale':
            _, sy, sx = op
            result = np.repeat(np.repeat(result, sy, axis=0), sx, axis=1)
        
        elif op[0] == 'tile':
            _, ty, tx = op
            result = np.tile(result, (ty, tx))
        
        elif op[0] == 'crop':
            _, region = op
            y1, y2, x1, x2 = region
            result = result[y1:y2, x1:x2]
    
    return result.astype(int)
```

---

## Complete Pipeline

```python
def solve_arc_task(task):
    """Complete ITT-based ARC solver."""
    
    train_pairs = task['train']
    test_inputs = [t['input'] for t in task['test']]
    
    # Analyze all training pairs
    all_activations = []
    for pair in train_pairs:
        phi_in = preprocess_grid(pair['input'])
        phi_out = preprocess_grid(pair['output'])
        activations = compute_all_fan_activations(phi_in, phi_out)
        all_activations.append(activations)
    
    # Find consensus active fans
    active_fans = find_consensus_fans(all_activations)
    
    # Compute bridge tensors
    bridges = compute_bridge_tensors(
        preprocess_grid(train_pairs[0]['input']),
        preprocess_grid(train_pairs[0]['output']),
        active_fans,
        all_activations[0]
    )
    
    # Synthesize program
    program = synthesize_program(active_fans, bridges, all_activations[0])
    
    # Execute on test inputs
    results = []
    for test_input in test_inputs:
        phi_test = preprocess_grid(test_input)
        result = execute_program(phi_test, program)
        results.append(result.tolist())
    
    return results
```

---

## Verification

```python
def verify_program(program, train_pairs):
    """Verify synthesized program against training data."""
    
    for pair in train_pairs:
        phi_in = preprocess_grid(pair['input'])
        phi_out = preprocess_grid(pair['output'])
        
        predicted = execute_program(phi_in, program)
        
        if not np.array_equal(predicted, phi_out):
            return False, f"Mismatch: {predicted.shape} vs {phi_out.shape}"
    
    return True, "All training pairs verified"
```

---

## Files in This Folder

- [fan_detection.md](./fan_detection.md) — Detailed detection algorithms
- [program_synthesis.md](./program_synthesis.md) — DSL and synthesis strategies

---

## Performance Targets

| Component | Complexity | Target |
|-----------|------------|--------|
| Fan detection | O(n²) per grid | < 10ms |
| Bridge analysis | O(k² · n²) | < 50ms |
| Program synthesis | O(k!) worst | < 100ms |
| Execution | O(n²) | < 5ms |
| **Total** | | < 200ms per task |

Where n = grid size, k = active fan count.

---

*"This is not heuristics. This is field calculus."*
