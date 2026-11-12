# SPEC — a skill for causal discovery on QRData

Written from the grill-me session (`process/grill-me-transcript.md`), 11 Nov 2026, and revised on 12 Nov after the scope check (version 3; v1 and v2 beside this file). This file states **what** we build and **why**; `PLAN.md` states **how**.

## Goal

Build one agent skill, `causal-discovery`, that helps a coding agent answer QRData's causal-discovery questions on real data: "which cause-and-effect relationship between these two variables is more likely?". Then measure whether the agent answers more of them correctly with the skill than without it.

## Why this part of QRData

We ran the agent without a skill on the development half of each candidate part, and counted the wrong answers a skill could fix.

| Part of QRData | Questions | Right without a skill | Wrong answers a skill could fix | Decision |
|---|---|---|---|---|
| Statistics | 142 | 75 of 83 (dev) | few: almost all right | out |
| Effect estimation | 69 | 17 of 31 (dev) | 1 of 14 | out: the failures come from the key, not the method |
| Discovery, simulated data (Neuropathic) | 100 | 46 of 50 (dev) | — | out: almost all right |
| **Discovery, real data (arctic.csv, flow.csv)** | **100** | **20 of 50 (dev)** | **23 of 30** | **in** |

On the real-data questions the agent claims a causal link where the key says there is none: in 23 of its 30 wrong development answers. It answers from domain knowledge and correlation instead of testing the data. Testing the data is a procedure a skill can teach, with a script that runs the test.

## What the skill does

The agent follows six steps: (1) read the two variables and the options; (2) check both variables are columns of the CSV; (3) run the skill's script, which runs the PC algorithm on all columns and reports whether the two variables are linked and in which direction; (4) map the result to an option: no link → "no causal relationship", a directed link → that direction, an undirected link → "double sided" if offered; (5) do not answer from domain knowledge or correlation alone; (6) end with `ANSWER: <letter>`.

## What is in the skill, and what is not

| Inside `tasks/.agents/skills/causal-discovery/` (the agent sees it) | Outside the skill (only we see it) |
|---|---|
| `SKILL.md`: trigger + the six steps | `harness/make_tasks.py`: task folders, answer key, dev/test split |
| `references/reading-the-graph.md`: how the script's output maps to the options | `harness/run_agent.py`: runs the agent, stores answers |
| `scripts/discover.py`: runs the PC algorithm on a CSV | `harness/score.py`: compares answers with the key |
| | `key/`: the answers |

The skill names no variable of the two datasets and no link between them: development and test questions come from the same two datasets, so a skill that held links seen on development questions would hold answers to test questions.

## Success criteria

- The comparison is fair: both runs use the same command and prompt; the only difference is the skill folder.
- No run can read the answer key, and every run is checked for it.
- The result is reported with a sign test fixed in advance (p < 0.05), whether the skill helps or not, next to two reference scores: answering "no causal relationship" every time, and the PC algorithm alone.

## Constraints

- Two students, one laptop, about 3 weeks for phase 2; a limited API budget.
- Agent: Claude Code with Sonnet, non-interactive (`claude -p`).
