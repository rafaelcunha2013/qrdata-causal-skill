# A skill for causal discovery on QRData — worked example

A worked example for the final project of *Basics of Programming in Python* (Leiden University, 2026–27). It shows **phase 1, define and plan**, on a benchmark that is *not* one of the project benchmarks: [QRData](https://github.com/xxxiaol/QRData), statistical and causal questions on CSV files.

**Status: end of phase 1.** The plan is written, and the agent has been run without a skill to choose the scope. The skill itself is not built yet; that is phase 2.

## Read in this order

1. `process/grill-me-transcript.md`: the grill-me session that started the plan. It is *simulated*: one agent asked, a second agent played the student pair.
2. `SPEC.md`: what we build and why.
3. `PLAN.md`: how. Sections 1–5 answer the brief's five cards; sections 6–10 (tasks, development loop, milestones, risks, budget) go beyond them.
4. The git history: `git log --stat` shows how the plan changed and why. Earlier versions of `SPEC.md` and `PLAN.md` are in the first commits.

## Layout

```
README.md · SPEC.md · PLAN.md
process/                  the grill-me transcript
tasks/                    what the agent sees: one folder per task (rebuilt by make_tasks.py)
  .agents/skills/causal-discovery/   the skill (phase 2)
  q213/                   the worked example: question.md + arctic.csv
key/                      the answers and the development/test split: outside tasks/, the agent never opens it
harness/                  our own Python: make_tasks.py, run_agent.py, score.py, recheck_peeks.py
analysis/                 estimator_check.py, discovery_check.py (development questions only)
tests/                    test_score.py: our scorer against QRData's eval.py
runs/                     one record per run (answer, time, cost, skills seen and called) + full transcript
```

## Setup

Needs Python 3.11 or later, [uv](https://docs.astral.sh/uv/), and [Claude Code](https://code.claude.com) for running the agent.

```bash
uv venv .venv
uv pip install --python .venv/bin/python pandas scipy statsmodels causal-learn
mkdir -p upstream && cd upstream
curl -LO https://raw.githubusercontent.com/xxxiaol/QRData/main/benchmark/QRData.json
curl -LO https://raw.githubusercontent.com/xxxiaol/QRData/main/benchmark/data.zip
curl -LO https://raw.githubusercontent.com/xxxiaol/QRData/main/benchmark/eval.py
unzip -q data.zip -d data && cd ..
.venv/bin/python harness/make_tasks.py arctic_flow
```

`make_tasks.py arctic_flow` writes the 100 task folders to `tasks/` and the answers to `key/arctic_flow.json`. Other scopes (`statistics`, `causal`, `effect`, `statistics_full`, `discovery`) write to `tasks_<scope>/`; they were used to choose the scope.

## Run and score

```bash
.venv/bin/python harness/run_agent.py arctic_flow baseline 1 sonnet dev   # the agent without the skill, development questions
.venv/bin/python harness/score.py arctic_flow baseline                    # right answers per side
.venv/bin/python tests/test_score.py                                      # our scorer vs eval.py
.venv/bin/python analysis/discovery_check.py                              # reference scores on development questions
```

## Results so far (Claude Code, Sonnet, no skill, one repeat)

| Part of QRData | Development questions right | Decision |
|---|---|---|
| Statistics | 75 of 83 | out: almost no room for a skill |
| Effect estimation | 17 of 31 | out: the failures come from the key |
| Discovery, simulated data | 46 of 50 | out: almost no room for a skill |
| **Discovery, real data** (`arctic.csv`, `flow.csv`) | **20 of 50** | **the scope** |

On the same 50 development questions: answering "no causal relationship" every time gets 38 right, and the PC algorithm alone gets 33. Score files: `runs/*-score.txt`.

## Licence and data

Our own code and text are under the MIT licence (`LICENSE`). The QRData material described below keeps its own licence.

QRData is by X. Liu, Z. Wu, X. Wu, P. Lu, K.-W. Chang and Y. Feng, *Are LLMs Capable of Data-based Statistical and Causal Reasoning? Benchmarking Advanced Quantitative Reasoning with Data*, Findings of ACL 2024. It is licensed [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). This repository includes, from QRData: the task folder `tasks/q213/` (one question and `arctic.csv`), the answer keys in `key/`, and the agent transcripts in `runs/`, which quote questions and data. They are used here non-commercially, with this attribution. Everything else is downloaded by the setup steps.
