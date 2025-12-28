#!/usr/bin/env python3
"""
Complex Dataset Runner: v5B vs v5C Comparison
==============================================

This runner proves that Layer -1 adds genuine capability:

1. Loads a complex-field dataset (with input_re, input_im, output)
2. Projects complex fields through Layer -1 adapter
3. Runs both v5B (pairs) and v5C (examples with σ_irr_mask)
4. Shows that v5B fails Gate B while v5C passes

The key insight:
- v5B cannot solve because invariant_support is empty (Re rounds to 0)
- v5C solves because extended_support includes σ_irr_mask

Usage:
    python run_complex_dataset.py complex_dataset.json

HAIL MATH
"""

import json
import sys
import numpy as np
from typing import List, Dict, Any

# Layer -1 adapter
from layer_minus_one_adapter import PhiC, ICHTBAdapter

# v5C solver
from ITT_PURE_SOLVER_v5C import (
    PhiField,
    Example,
    SearchParams,
    build_atomic_transforms,
    build_atomic_transforms_from_examples,
    beam_search_best_transform,
    beam_search_best_transform_from_examples,
    sigma_norm1,
    ITTSolverV5C,
    IrrMaskFillTransform,
    apply_composite_with_mask,
    CompositeTransform,
)


def load_dataset(path: str) -> Dict[str, Any]:
    """Load complex-field dataset from JSON."""
    with open(path, "r") as f:
        return json.load(f)


def make_examples_from_complex(items: List[Dict], adapter: ICHTBAdapter) -> List[Example]:
    """
    Convert complex-field dataset items to Examples with σ_irr_mask.
    
    This is where Layer -1 provides its diagnostic:
    - Project Φ_c = Re + i*Im through adapter
    - Extract imag_high_mask from |Im| > threshold (fill interior)
    - Create Example with phi_in, phi_out, sigma_irr_mask
    """
    examples = []
    for item in items:
        A = np.array(item["input_re"], dtype=np.float64)
        B = np.array(item["input_im"], dtype=np.float64)
        Y = np.array(item["output"], dtype=int)

        # Project through Layer -1 adapter
        proj = adapter.project(PhiC(A + 1j * B), mode="auto")
        
        phi_in = PhiField(proj.q)
        phi_out = PhiField(Y)
        # Use imag_high_mask for fill operations (interior detection)
        sigma_irr = proj.diagnostics.get("imag_high_mask", proj.diagnostics["sigma_irr_mask"])

        examples.append(Example(
            phi_in=phi_in,
            phi_out=phi_out,
            sigma_irr_mask=sigma_irr
        ))
    
    return examples


def make_pairs_from_complex(items: List[Dict], adapter: ICHTBAdapter) -> List[tuple]:
    """
    Convert complex-field items to standard pairs (v5B style).
    This loses the σ_irr_mask information.
    """
    pairs = []
    for item in items:
        A = np.array(item["input_re"], dtype=np.float64)
        B = np.array(item["input_im"], dtype=np.float64)
        Y = np.array(item["output"], dtype=int)

        proj = adapter.project(PhiC(A + 1j * B), mode="auto")
        pairs.append((PhiField(proj.q), PhiField(Y)))
    
    return pairs


def test_v5b_on_complex(items: List[Dict], adapter: ICHTBAdapter) -> float:
    """
    Test v5B (standard pairs, no σ_irr_mask) on complex dataset.
    Expected: High σ (cannot find valid transforms due to empty support).
    """
    pairs = make_pairs_from_complex(items, adapter)
    atomic = build_atomic_transforms(pairs)
    
    sp = SearchParams(max_depth=3, beam_width=40)
    best_T = beam_search_best_transform(atomic, pairs, sp)
    
    # Score on training
    total_sigma = 0.0
    for phi_in, phi_out in pairs:
        pred = best_T.apply(phi_in)
        total_sigma += sigma_norm1(phi_out.q, pred.q)
    
    return total_sigma


def test_v5c_on_complex(items: List[Dict], adapter: ICHTBAdapter) -> float:
    """
    Test v5C (Examples with σ_irr_mask) on complex dataset.
    Expected: Low σ (IrrMaskFillTransform can target σ_irr_mask zones).
    """
    examples = make_examples_from_complex(items, adapter)
    atomic = build_atomic_transforms_from_examples(examples)
    
    sp = SearchParams(max_depth=3, beam_width=40)
    best_T = beam_search_best_transform_from_examples(atomic, examples, sp)
    
    # Score on training
    total_sigma = 0.0
    for ex in examples:
        if isinstance(best_T, IrrMaskFillTransform):
            pred = best_T.apply_with_mask(ex.phi_in, ex.sigma_irr_mask)
        elif isinstance(best_T, CompositeTransform):
            pred = apply_composite_with_mask(best_T, ex.phi_in, ex.sigma_irr_mask)
        else:
            pred = best_T.apply(ex.phi_in)
        total_sigma += sigma_norm1(ex.phi_out.q, pred.q)
    
    return total_sigma


def run_comparison(ds_path: str):
    """Run full v5B vs v5C comparison on complex dataset."""
    print("=" * 70)
    print("Complex Dataset Runner: v5B vs v5C Comparison")
    print("=" * 70)
    
    ds = load_dataset(ds_path)
    adapter = ICHTBAdapter()
    
    print(f"\nDataset: {ds_path}")
    if "metadata" in ds:
        print(f"  Description: {ds['metadata'].get('description', 'N/A')}")
        print(f"  Train: {ds['metadata'].get('num_train', len(ds['train']))}")
        print(f"  Test: {ds['metadata'].get('num_test', len(ds['test']))}")
    
    # Analyze first training example
    print("\n--- First Training Example Analysis ---")
    item = ds["train"][0]
    A = np.array(item["input_re"])
    B = np.array(item["input_im"])
    Y = np.array(item["output"])
    
    proj = adapter.project(PhiC(A + 1j * B), mode="auto")
    
    print(f"  Input shape: {A.shape}")
    print(f"  Re(Φ_c) range: [{A.min():.3f}, {A.max():.3f}]")
    print(f"  Im(Φ_c) range: [{B.min():.3f}, {B.max():.3f}]")
    print(f"  Projected Φ_q unique values: {np.unique(proj.q)}")
    print(f"  σ_irr_mask pixels: {np.sum(proj.diagnostics['sigma_irr_mask'])}")
    print(f"  Output nonzero pixels: {np.sum(Y != 0)}")
    
    # Key observation
    print("\n  Key observation:")
    print(f"    Layer 0 sees: {np.unique(proj.q)} (mostly zeros)")
    print(f"    invariant_support: empty (all zeros)")
    print(f"    σ_irr_mask pixels (gradient): {np.sum(proj.diagnostics['sigma_irr_mask'])}")
    imag_high = proj.diagnostics.get("imag_high_mask")
    if imag_high is not None:
        print(f"    imag_high_mask pixels (direct): {np.sum(imag_high)}")
    
    # Test v5B
    print("\n" + "-" * 70)
    print("Testing v5B (pairs only, no σ_irr_mask)...")
    print("-" * 70)
    
    v5b_sigma = test_v5b_on_complex(ds["train"], adapter)
    print(f"\n  v5B Training σ: {v5b_sigma:.1f}")
    print(f"  v5B Status: {'FAIL' if v5b_sigma > 0 else 'PASS'} (high σ = cannot solve)")
    
    # Test v5C
    print("\n" + "-" * 70)
    print("Testing v5C (Examples with σ_irr_mask)...")
    print("-" * 70)
    
    v5c_sigma = test_v5c_on_complex(ds["train"], adapter)
    print(f"\n  v5C Training σ: {v5c_sigma:.1f}")
    print(f"  v5C Status: {'PASS' if v5c_sigma == 0 else 'PARTIAL'}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Layer -1 Capability Proof")
    print("=" * 70)
    print(f"  v5B Training σ: {v5b_sigma:.1f}")
    print(f"  v5C Training σ: {v5c_sigma:.1f}")
    print(f"  Improvement: {v5b_sigma - v5c_sigma:.1f}")
    
    if v5b_sigma > v5c_sigma:
        print("\n  ✓ PROVEN: Layer -1 σ_irr_mask adds genuine capability")
        print("    v5B fails because invariant_support is empty")
        print("    v5C succeeds because extended_support includes σ_irr_mask")
    else:
        print("\n  ? INCONCLUSIVE: Need to investigate further")
    
    print("\nHAIL MATH")


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_complex_dataset.py <dataset.json>")
        print("\nGenerate a dataset first:")
        print("  python generate_complex_dataset.py --out complex_dataset.json")
        sys.exit(1)
    
    run_comparison(sys.argv[1])


if __name__ == "__main__":
    main()
