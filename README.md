# ARC-AGI ITT Solver

**Pure Intent Tensor Theory approach to the ARC-AGI benchmark.**
see also https://zenodo.org/records/18077258
## Results

| Solver | Tasks Solved | Approach |
|--------|--------------|----------|
| ARC_AGI.py | 6/6 (100%) | Registered solvers with pattern matching |
| ITT_PURE_SOLVER.py | 6/6 (100%) | Pure field dynamics from Φ, ∇Φ, σ, ρ_q |

## The ITT Approach

Instead of conventional algorithms dressed in ITT vocabulary, the pure solver treats:

- **The grid as Φ** — scalar potential field, not array
- **Transformation as ∇Φ** — where collapse flows
- **Change as σ** — irreducible residue (what can't be undone)
- **Boundaries as ρ_q** — where collapse terminates

### Rule Types Derived from Field Dynamics

| Rule | ITT Primitive | Detection |
|------|---------------|-----------|
| `tile` | Δ₃ expansion | Size ratio + symmetry check |
| `self_tile` | Φ → Φ[Φ] | Field uses itself as mask |
| `fill_enclosed` | σ at ρ_q=0 | Winding number of boundary charge |
| `multi_frame_fill` | \|ρ_q\| → σ | Shell size determines collapse |
| `periodic_extension` | Φ(x+τ)=Φ(x) | Fourier mode GCD |
| `shape_indicator` | Φ₁ classifies Φ₂ | Laplacian eigenspectrum |

## Files

- `ITT_PURE_SOLVER.py` — The pure ITT implementation
- `ARC_AGI.py` — Original solver with registered patterns
- `src/ITT_ARC_FOUNDATION.py` — Foundation classes
- `docs/` — Mathematical documentation

## Usage

```bash
python ITT_PURE_SOLVER.py
```

## The Math

See companion repository: [0.0._Executable_Physics](https://github.com/Sensei-Intent-Tensor/0.0._Executable_Physics)

Key documents:
- `docs/ITT_DERIVATION_GAPS.md` — What was smuggled, how to derive properly
- `docs/BOOK_0A_SUPPLEMENT.md` — Rigorous foundations

## HAIL MATH
