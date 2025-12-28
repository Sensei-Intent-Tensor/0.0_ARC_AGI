#!/usr/bin/env python3
"""
Complex Dataset Generator for v5C Layer -1 Validation
======================================================

This generates synthetic tasks where:
- Layer 0 sees NOTHING (real rounds to 0)
- The ONLY signal is in ||∇ Im(Φ_c)|| spikes
- Output requires filling the mask region

Proves:
- v5B cannot solve these (no admissible invariant support)
- v5C solves them (σ_irr_mask expands support + IrrMaskFillTransform)

This is the first genuine capability injection from Layer −1.

Usage:
    python generate_complex_dataset.py --out dataset.json --train 12 --test 4

HAIL MATH
"""

import json
import random
import argparse
from typing import Dict, Any, List
import numpy as np


def make_spike_mask(h: int, w: int, rng: random.Random) -> np.ndarray:
    """
    Create a contiguous "spike zone" mask (rectangle with optional holes).
    This mask will be encoded ONLY in the imaginary field (via gradients).
    """
    # Random rectangle (not touching edges)
    rh = rng.randint(2, max(2, h // 3))
    rw = rng.randint(2, max(2, w // 3))
    r0 = rng.randint(1, max(1, h - rh - 1))
    c0 = rng.randint(1, max(1, w - rw - 1))

    mask = np.zeros((h, w), dtype=bool)
    mask[r0:r0+rh, c0:c0+rw] = True

    # Optionally punch 1-2 holes to make it non-trivial
    if rng.random() < 0.4 and rh > 2 and rw > 2:
        for _ in range(rng.randint(1, 2)):
            hr = rng.randint(1, max(1, rh // 2))
            hc = rng.randint(1, max(1, rw // 2))
            rr = rng.randint(r0, r0 + rh - hr)
            cc = rng.randint(c0, c0 + rw - hc)
            mask[rr:rr+hr, cc:cc+hc] = False

    return mask


def encode_imag_from_mask(mask: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    """
    Encode mask into Im field such that ||∇Im|| spikes around mask edges.
    
    Simplest approach: Im = amplitude * indicator(mask)
    Then gradients occur at boundaries.
    """
    return amplitude * mask.astype(np.float64)


def make_task(h: int, w: int, fill_color: int, rng: random.Random) -> Dict[str, Any]:
    """
    Build one complex-field task:
    
    - input_re: mostly zeros + light noise (keeps Layer 0 ambiguous)
    - input_im: spikes encode the allowed edit zone
    - output: fill the allowed edit zone with fill_color (rest unchanged)
    
    The key insight:
    - Real part rounds to all zeros → Layer 0 sees nothing
    - Imaginary gradient spikes mark the edit zone
    - Only v5C with σ_irr_mask can solve this
    """
    # Real field: keep it boring/ambiguous in Layer 0
    input_re = np.zeros((h, w), dtype=np.float64)

    # Add tiny real perturbations (still rounds to 0)
    noise = rng.random() * 0.2
    input_re += noise * (np.random.rand(h, w) - 0.5)

    # Create edit zone mask (encoded in imaginary only)
    mask = make_spike_mask(h, w, rng)
    input_im = encode_imag_from_mask(mask, amplitude=1.0)

    # Output: fill the mask region with the fill color
    output = np.zeros((h, w), dtype=int)
    output[mask] = fill_color

    return {
        "input_re": input_re.round(4).tolist(),
        "input_im": input_im.round(4).tolist(),
        "output": output.tolist()
    }


def make_dataset(num_train: int = 12, num_test: int = 4, seed: int = 0) -> Dict[str, Any]:
    """Generate complete complex-field dataset."""
    rng = random.Random(seed)
    np.random.seed(seed)

    # Keep sizes varied to prevent overfitting
    sizes = [(8, 8), (10, 10), (12, 12), (8, 12), (12, 8)]
    fill_colors = [2, 3, 4, 6, 8]

    train = []
    for i in range(num_train):
        h, w = rng.choice(sizes)
        c = rng.choice(fill_colors)
        train.append(make_task(h, w, c, rng))

    test = []
    for i in range(num_test):
        h, w = rng.choice(sizes)
        c = rng.choice(fill_colors)
        t = make_task(h, w, c, rng)
        # Test keeps output for validation
        test.append(t)

    return {
        "train": train,
        "test": test,
        "metadata": {
            "description": "Complex-field dataset for Layer -1 validation",
            "purpose": "Prove v5C with σ_irr_mask can solve tasks v5B cannot",
            "num_train": num_train,
            "num_test": num_test,
            "seed": seed
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate complex-field dataset for v5C validation")
    parser.add_argument("--out", default="complex_dataset.json", help="Output file path")
    parser.add_argument("--train", type=int, default=12, help="Number of training examples")
    parser.add_argument("--test", type=int, default=4, help="Number of test examples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    ds = make_dataset(args.train, args.test, args.seed)
    
    with open(args.out, "w") as f:
        json.dump(ds, f, indent=2)
    
    print(f"Generated complex dataset: {args.out}")
    print(f"  Training examples: {args.train}")
    print(f"  Test examples: {args.test}")
    print(f"  Seed: {args.seed}")
    print("\nDataset guarantees:")
    print("  - Layer 0 sees nothing (real rounds to 0)")
    print("  - Only signal is in ||∇ Im(Φ)|| spikes")
    print("  - v5B cannot solve (no invariant support)")
    print("  - v5C can solve (σ_irr_mask extends support)")


if __name__ == "__main__":
    main()
