# ARC-AGI: The Complete Picture

**Everything You Need to Play NOW**

---

## What ARC-AGI Actually Is

It's a **benchmark** created by François Chollet (creator of Keras) to measure **general intelligence** - not knowledge, not memorization, but the ability to **learn new skills from minimal examples**.

The philosophy: "We can declare the arrival of AGI when we build an artificial system that matches the learning efficiency of humans."

---

## The Three Versions

| Version | Type | Tasks | Best AI Score | Human Score |
|---------|------|-------|---------------|-------------|
| **ARC-AGI-1** | Static puzzles | 800 (400 train + 400 eval) | ~50% | ~85% |
| **ARC-AGI-2** | Static puzzles (harder) | 1120 (1000 train + 120 eval) | ~24% | ~66% |
| **ARC-AGI-3** | Interactive games | ~100 environments | In development | TBD |

---

## THE REPOSITORIES (Clone These to Play NOW)

### ARC-AGI-1 (Original)
```bash
git clone https://github.com/fchollet/ARC-AGI.git
cd ARC-AGI

# Structure:
# data/training/     → 400 tasks to practice on
# data/evaluation/   → 400 tasks to test on
# apps/testing_interface.html → Browser UI to solve manually
```
**Play it:** Open `apps/testing_interface.html` in Chrome, load any JSON from `data/`

### ARC-AGI-2 (Current Competition Version)
```bash
git clone https://github.com/arcprize/ARC-AGI-2.git
cd ARC-AGI-2

# Structure:
# data/training/     → 1000 tasks (includes ARC-AGI-1 + new)
# data/evaluation/   → 120 tasks (harder than v1)
```
**Play it:** Use the testing interface from ARC-AGI-1, or go to https://arcprize.org/play

### ARC-AGI-3 (Interactive - In Development)
```bash
git clone https://github.com/arcprize/ARC-AGI-3-Agents.git
cd ARC-AGI-3-Agents
uv sync  # Install dependencies

# Get API key from: https://three.arcprize.org
# Add to .env file

# Run an agent:
uv run main.py --agent=random --game=ls20
```
**This is different:** Instead of static puzzles, you build **agents** that play interactive games.

---

## Task Counts Summary

```
ARC-AGI-1:
  Training:    400 tasks (public, use to learn/train)
  Evaluation:  400 tasks (public, use to test)
  
ARC-AGI-2:
  Training:   1000 tasks (public, includes v1 + new)
  Evaluation:  120 tasks (public, harder)
  Semi-private: ??? (for commercial models)
  Private:     ??? (for competition final scoring)

ARC-AGI-3:
  Public games:    3 (ls20, ft09, vc33)
  Private games:   ~3 more (hidden)
  Future:         ~100 total planned
```

---

## How to Actually Play RIGHT NOW

### Option 1: Browser Interface (Easiest)
Go to: https://arcprize.org/play

This loads tasks from ARC-AGI-2. You can solve them manually to understand what the puzzles look like.

### Option 2: Local Testing Interface
```bash
git clone https://github.com/fchollet/ARC-AGI.git
cd ARC-AGI
# Open apps/testing_interface.html in Chrome
# Load any .json file from data/training/ or data/evaluation/
```

### Option 3: Write Code That Solves Them
```python
import json

# Load a task
with open('data/training/0a938d79.json') as f:
    task = json.load(f)

# task['train'] = list of {input, output} pairs (the examples)
# task['test'] = list of {input} (what you need to solve)

# Your job: figure out the rule from train, apply to test
```

### Option 4: Build an Agent (ARC-AGI-3)
```bash
git clone https://github.com/arcprize/ARC-AGI-3-Agents.git
cd ARC-AGI-3-Agents
uv sync
# Get API key from https://three.arcprize.org
# Edit .env
uv run main.py --agent=random --game=ls20
```

---

## The Competition vs The Benchmark

**BENCHMARK** = The puzzles themselves. Always available. Clone and solve anytime.

**COMPETITION** = Specific events with prizes and deadlines.

| Competition | Dataset | Status | Prize |
|-------------|---------|--------|-------|
| ARC Prize 2024 | ARC-AGI-1 | CLOSED | $1M |
| ARC Prize 2025 | ARC-AGI-2 | CLOSED (Nov 3, 2025) | $1M |
| ARC Prize 2026 | ARC-AGI-3? | Coming 2026 | TBD |

**You can work on the puzzles anytime.** The competition just adds deadlines and prizes.

---

## 2026 Competition: What We Know

- **ARC-AGI-3** is interactive (games, not static puzzles)
- **Format:** Build agents that explore, learn, and act
- **Test:** Percept → Plan → Action → Feedback loop
- **Skills tested:** Exploration, memory, goal acquisition, alignment
- **Games:** ~100 environments (only 6 public so far)

**The puzzles from ARC-AGI-1 and ARC-AGI-2 will likely NOT be in ARC-AGI-3.** It's a fundamentally different paradigm.

---

## How Scoring Works

### ARC-AGI-1 and ARC-AGI-2 (Static)
```
Score = (correct tasks) / (total tasks) × 100%

"Correct" means:
- EVERY cell matches expected output
- EXACT dimensions
- You get 2-3 attempts per task
```

### ARC-AGI-3 (Interactive)
```
Score = based on game completion / level achievement
(Details still being developed)
```

---

## What You Can Do Right Now

### Level 1: Understand the puzzles
```bash
# Clone both repos
git clone https://github.com/fchollet/ARC-AGI.git
git clone https://github.com/arcprize/ARC-AGI-2.git

# Look at tasks manually using the testing interface
# Or: https://arcprize.org/play
```

### Level 2: Write a solver
```python
# In your repo: 0.0_ARC_AGI
# Create a solver that:
# 1. Loads tasks from data/
# 2. Analyzes input→output patterns
# 3. Applies detected rule to test input
# 4. Compares prediction to expected output
# 5. Calculates accuracy %
```

### Level 3: Run against full evaluation set
```python
# Load all 400 (v1) or 120 (v2) evaluation tasks
# Run your solver
# Report: X% correct
```

### Level 4: Build an ARC-AGI-3 agent
```bash
git clone https://github.com/arcprize/ARC-AGI-3-Agents.git
# Create your own agent in agents/
# Test against the 3 public games
```

---

## File Structure Reference

### ARC-AGI-1 (github.com/fchollet/ARC-AGI)
```
ARC-AGI/
├── apps/
│   └── testing_interface.html   ← Browser UI
├── data/
│   ├── training/                ← 400 tasks (practice)
│   │   ├── 0a938d79.json
│   │   ├── 0b148d64.json
│   │   └── ...
│   └── evaluation/              ← 400 tasks (test)
│       ├── 0520fde7.json
│       └── ...
├── LICENSE
└── README.md
```

### ARC-AGI-2 (github.com/arcprize/ARC-AGI-2)
```
ARC-AGI-2/
├── data/
│   ├── training/                ← 1000 tasks
│   └── evaluation/              ← 120 tasks
├── LICENSE
├── changelog.md
└── readme.md
```

### ARC-AGI-3-Agents (github.com/arcprize/ARC-AGI-3-Agents)
```
ARC-AGI-3-Agents/
├── agents/
│   ├── __init__.py
│   ├── random_agent.py          ← Example agent
│   └── ...
├── main.py                      ← Entry point
├── .env-example                 ← API key config
└── ...
```

---

## The ITT Approach

You're not just trying to "solve puzzles." You're exploring what ITT can reveal about the **nature of abstraction and reasoning**.

Each task is a **boundary resolution problem**:
- Input = R_B₁[Φ] (constraint resolved through boundary B₁)
- Output = R_B₂[Φ] (same constraint, different boundary)
- Task = infer Φ and B₂

The fans (Δ₁-Δ₆) detect which operations activated:
- ∇Φ → translation
- ∇×F → rotation
- ∇²Φ → scaling
- etc.

This is what makes ITT's approach potentially valuable for the **Paper Prize** - not just solving puzzles, but explaining WHY solutions work.

---

## Quick Start Checklist

- [ ] Clone ARC-AGI-1: `git clone https://github.com/fchollet/ARC-AGI.git`
- [ ] Clone ARC-AGI-2: `git clone https://github.com/arcprize/ARC-AGI-2.git`
- [ ] Try solving manually: Open `apps/testing_interface.html`
- [ ] Or use: https://arcprize.org/play
- [ ] Look at task JSON structure
- [ ] Write simple solver (detect flips, rotates)
- [ ] Run against training set
- [ ] Expand solver capabilities
- [ ] Document what you learn (for Paper Prize potential)

---

## Links

| Resource | URL |
|----------|-----|
| ARC Prize Main Site | https://arcprize.org |
| Play Online | https://arcprize.org/play |
| Guide | https://arcprize.org/guide |
| ARC-AGI-1 Repo | https://github.com/fchollet/ARC-AGI |
| ARC-AGI-2 Repo | https://github.com/arcprize/ARC-AGI-2 |
| ARC-AGI-3 Agents | https://github.com/arcprize/ARC-AGI-3-Agents |
| ARC-AGI-3 Info | https://arcprize.org/arc-agi/3/ |
| Original Paper | https://arxiv.org/abs/1911.01547 |

---

*"It's just a puzzle to me... I am just poking around at what ITT can do."*

That's the right approach. The puzzles are always there. Play when you want. Learn what you can.

HAIL MATH.
