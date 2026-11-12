# SPEC — a skill for causal effect estimation on QRData

Written from the grill-me session (`process/grill-me-transcript.md`), 11 Nov 2026. This file states **what** we build and **why**; `PLAN.md` states **how**.

## Goal

Build one agent skill, `causal-effect`, that helps a coding agent answer QRData's effect-estimation questions. Then measure whether the agent answers more of them correctly with the skill than without it.

## Why this part of QRData

| Part of QRData | Questions | Pilot without a skill | Decision |
|---|---|---|---|
| Statistics (no "Causality" keyword) | 142 | 9 of 10 right | out: almost no room to improve |
| Causal discovery (full graph, pairwise) | 150 + 50 | part of the causal pilot | out: the answer graphs are published, so a skill could help only by holding the answers |
| Effect estimation (the rest of "Causality") | 69 | part of the causal pilot (5 of 10) | **in** |

Effect estimation is a procedure: name the estimand, name the design, choose a method, compute. A skill can teach that procedure without holding any answer.

## What the skill does

The agent follows six steps: (1) name the estimand (ATE, ATT, ATC, or "should we control for X?"), (2) name the design, (3) inspect the CSV, (4) choose the method from the skill's reference and compute it with the skill's script, (5) compare the result with the naive difference in means, (6) round as asked and end with `ANSWER: <value>`.

## What is in the skill, and what is not

| Inside `skills/causal-effect/` (the agent sees it) | Outside the skill (only we see it) |
|---|---|
| `SKILL.md`: trigger + the six steps | `harness/make_tasks.py`: task folders, answer key, dev/test split |
| `references/methods.md`: when to use each method | `harness/run_agent.py`: runs the agent, stores answers |
| `scripts/estimate.py`: computes an estimate | `harness/score.py`: compares answers with the key |
| | `key/`: the answers |

## Success criteria

- The comparison is fair: both arms run the same command and prompt; the only difference is the skill folder.
- No run can read the answer key, and every run is checked for it.
- The result is reported with a sign test fixed in advance (p < 0.05), whether the skill helps or not.

## Constraints

- Two students, one laptop, about 3 weeks for phase 2; a limited API budget.
- Agent: Claude Code with Sonnet, non-interactive (`claude -p`).

## Checked after the session

- grill-me said that with `--setting-sources project` "the baseline should list no skills". Tested on 11 Nov: user-installed plugins are removed, but Claude Code's ~22 built-in skills still load in both arms. The check is therefore: both arms load the same skills except `causal-effect`, and no run calls any other skill.
