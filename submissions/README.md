# ARC-AGI Solver Submissions

**Playful Pokes at What ITT Can Do**

---

## What Is This Competition?

**ARC-AGI** (Abstraction and Reasoning Corpus) is a benchmark that tests for **general intelligence** - not knowledge, not pattern matching, but the ability to learn new skills from just a few examples.

### The Structure

Each task shows 3-5 input→output examples, then asks: "Given this new input, what's the output?"

```
Training:
  Input A → Output A'
  Input B → Output B'
  Input C → Output C'

Test:
  Input D → ???  (you figure it out)
```

The catch: Every task tests a DIFFERENT skill. You can't just memorize patterns.

### The Prize Structure

| Prize | Requirement | Amount |
|-------|-------------|--------|
| **Grand Prize** | 85% on private eval | $500,000 (UNCLAIMED!) |
| **Paper Prize** | Best conceptual progress | $50,000 |
| **Top Score** | Highest % correct | Varies |

**Key insight:** The Paper Prize doesn't require a high score - just novel ideas that advance understanding. ITT could qualify here!

### Current State

- **Best score ever:** 24% (NVARC, Nov 2025)
- **Pure LLMs:** 0% on ARC-AGI-2
- **Humans:** ~100% (every task solved by 2+ humans in <2 attempts)

The gap between 24% and 85% is where the $500K sits unclaimed.

---

## Competition Timeline

| Version | Status | Notes |
|---------|--------|-------|
| ARC Prize 2024 | Closed | ARC-AGI-1 |
| ARC Prize 2025 | **CLOSED** (Nov 3, 2025) | ARC-AGI-2 (harder) |
| ARC Prize 2026 | Coming | ARC-AGI-3 (interactive/agentic) |

We're in the gap between competitions. Perfect time to build.

---

## What's In This Folder

### Working Code

| File | What It Does | Accuracy |
|------|--------------|----------|
| `curvent_solver_v1.py` | Detects simple transforms (flip, rotate, scale, color map) | ~1.5% training |

### Notebooks (Historical Experiments)

| Notebook | Content |
|----------|---------|
| `85_solved_evaluation.ipynb` | Curvent Field Theory experiments |
| `prediction_focused_solver.ipynb` | Basic pattern learning |

**Note:** The "85%" in the notebook name referred to that specific experimental run, not competition performance.

---

## The Honest Numbers

```
What v1 can detect:
  - Flip (lr/ud)      → <1% of tasks
  - Rotate (90/180)   → <1% of tasks  
  - Scale/tile        → <1% of tasks
  - Color mapping     → ~2% of tasks
  
What v1 can't detect (96%+ of tasks):
  - Object segmentation
  - Pattern recognition
  - Relational reasoning
  - Conditional logic
  - Multi-step composition
```

---

## Why ITT Matters Here

The competition isn't just about solving puzzles. It's about understanding **how intelligence works**.

From the ITT framework:

```
Φ   = The abstract pattern (what's invariant)
R_B = Resolution through boundary (how it manifests)
ℛ   = Rule inference (what transformation?)
T   = Topology-conditional activation (how to apply it?)
```

The Paper Prize rewards **conceptual progress**. ITT provides a mathematical framework for understanding WHY certain approaches work and others don't.

---

## The Path

This isn't about winning quickly. Like deriving gravity in Book 1:

> "It was a very long process of zero assumptive smuggled-in things - it had to truly build and fill itself out."

ARC is the same. We're not trying to hack a high score. We're exploring what ITT can reveal about the nature of abstraction and reasoning.

---

## Next Steps

1. **Understand the benchmark** - What makes each task hard?
2. **Map to ITT** - Which fan surfaces activate for which task types?
3. **Build incrementally** - Add capabilities one by one
4. **Document insights** - Paper Prize material

---

*"It's just a puzzle to me... I am just poking around at what ITT can do for the world of whatever this is."*

HAIL MATH.
