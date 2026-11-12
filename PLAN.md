# PLAN — a skill for causal effect estimation on QRData

Pair: Student A, Student B · Repository: *(URL added when the private repository is created)*
Process: grill-me session → `process/grill-me-transcript.md` → `SPEC.md` (what and why) → this plan (how).

## 1 · Benchmark

**Worked example: q325** (a development question; see Scope).

- **What the agent receives:** `question.md` and `ihdp_4.csv` (747 children; `treatment`, outcome `y`, covariates `x1`–`x25`). The question: "What is the Average treatment effect on the treated of the dataset? Please round to the nearest hundredth."
- **Correct answer:** 4.00.
- **How the benchmark checks it:** QRData's `eval.py` takes the first number in the answer and accepts it if it lies within 3% of the key, so here between 3.88 and 4.12. Multiple-choice answers are accepted if they start with the key's text.
- *First candidate was q317. After the split it fell on the test side, so we replaced it: we may not study test questions while we build.*

**Pilot run** (Claude Code, Sonnet, no skill, 11 Nov; full results in `runs/effect-baseline/`):

| Run | Questions | Right |
|---|---|---|
| Statistics pilot | 10 | 9 |
| Causal pilot | 10 | 5 |
| **Effect estimation, first run, one repeat** | **69** | **39 (57%)** — dev 17 of 31, test 22 of 38 |

On q325 the agent answered 4.14 (wrong: 3.5% off). Its reply also gives the plain regression (4.18) and the difference in means (4.23). All three miss the key, so choosing the method decides the score.

**Validity — what could make a high score misleading:**

- **Lenient scoring:** only the first number counts, within 3%; a multiple-choice answer only has to start with the key.
- **Chance:** 5 of the 69 questions are multiple choice (yes/no), right half the time by guessing; for the 64 numerical ones, chance is near zero.
- **Training data:** QRData and its sources (textbooks, the IHDP and Jobs datasets) are public, so the model may have seen the answers.
- **Doubtful keys:** on q370 the key is 0.10 and the agent answered 9.75 with a regression-discontinuity fit. B checks q370 and one more; we always score with the official key.

## 2 · Scope

- **Subset:** the 69 effect-estimation questions (QRData questions with the keyword "Causality" that are not causal discovery). Sources: IHDP 30, *Causal Inference for the Brave and True* 24, Jobs 10, *Quantitative Social Science* 5. 64 numerical, 5 multiple choice.
- **Rationale:**
  - Statistics was left out: 9 of 10 right in the pilot leaves almost no room for a skill.
  - Causal discovery (150 + 50) was left out: its answer graphs are published, so a skill could help there only by containing the answers.
  - Effect estimation is a procedure a skill can teach without holding answers.
- **Runtime:** median 12 s per task (max 63 s); one pass over the 69 takes 15 min and costs $4.25. The final measurement (38 test questions × 2 arms × 3 repeats = 228 runs) takes about 46 min and $14.

## 3 · Skill design

- **Procedure** (`SKILL.md`):
  1. Name the estimand: ATE, ATT, ATC, or "should we control for X?".
  2. Name the design: randomized, observational with confounders, instrumental variables, difference-in-differences, regression discontinuity, or synthetic control.
  3. Inspect the CSV: treatment, outcome and covariate columns.
  4. Choose the method in `references/methods.md` and run `scripts/estimate.py`. If no method fits, regress the outcome on treatment and all covariates.
  5. Compare the estimate with the naive difference in means (sign and size).
  6. Round as the question asks; end with `ANSWER: <value>`.
- **Trigger** (the `description` line): "Use when a question asks for a treatment effect (ATE, ATT, ATC) or whether to control for a variable, using CSV data."
- **Structure:**

  ```
  skills/causal-effect/
    SKILL.md                trigger + the six steps
    references/methods.md   one section per method the dev questions need: when to use it, a snippet
    scripts/estimate.py     --csv --treatment --outcome --method [--covariates]
                            prints the estimate and the naive difference in means
  ```

  `estimate.py` starts with two methods, `diff_means` and `regression`; others are added only if dev questions need them. The method names in `methods.md` match its `--method` values.
- **Multiple skills:** one skill.
- **Outside the skill** (the agent never sees it): `harness/make_tasks.py`, `harness/run_agent.py`, `harness/score.py`, `key/`.

## 4 · Evaluation

- **Comparison:** both arms run the identical command and prompt:

  ```
  claude -p "<prompt>" --model sonnet --output-format stream-json --verbose
         --setting-sources project --strict-mcp-config --allowedTools Bash,Read,Glob,Grep,Skill
  ```

  The prompt never mentions the skill. The only difference: in the skill arm, `run_agent.py` copies `skills/causal-effect/` into the task's `.claude/skills/`.
- **Skill check:** `--setting-sources project` removes our user-installed skills, but Claude Code's 22 built-in skills still load in both arms (tested 11 Nov). Each record stores the skills loaded and the skills called. A run is valid if its loaded skills equal the baseline's plus `causal-effect` (skill arm only) and it calls no skill other than `causal-effect`.
- **Development and test split:** by data file, within each source, seed 2026 (`key/effect_split.json`): 31 dev and 38 test questions. We build the skill on dev questions only; test questions run only for the final measurement. *Limitation:* IHDP asks the same three questions on 10 files, so a dev IHDP question already teaches the method a test IHDP question needs.
- **Metrics** (test set, per arm): accuracy averaged over 3 repeats; for each question, how many of its 3 repeats were right; median time and cost per task.
- **Decision rule, fixed now:** per question, *win* = the skill arm got more of its 3 repeats right, *loss* = fewer, *tie* = equal. Sign test on wins and losses, `scipy.stats.binomtest(wins, wins + losses, 0.5)`, threshold p < 0.05. If it is not reached, we write "not enough evidence that the skill helps on this test set" and still report wins, losses and ties. No repeats or questions are added after seeing the result. *Limitation:* with 38 test questions, a difference of one or two questions is noise; at least 6 questions must change, all wins, to reach p < 0.05.
- **Answer isolation:** each run happens in a fresh temporary copy of the task folder, outside the repository. The full transcript is saved, and the harness flags any run whose transcript names an answer file (`causal.json`, `effect.json`, `QRData.json`, `upstream`); we check flagged runs by hand. A run that peeked or called another skill is invalid and rerun; we report how many. First run: 0 of 69 flagged.

## 5 · Tools and teamwork

- **Agent and model:** Claude Code with Sonnet, non-interactive. The harness already runs it; changing agents would mean redoing the pilot.
- **Batch execution:** `run_agent.py <scope> <arm> <repeats>`, one run after another on one laptop. One record per run, `runs/<scope>-<arm>/<task>-r<k>.json` (answer, seconds, cost, skills loaded and called, peek flag), plus the transcript `.jsonl`.
- **Version control:** one private repository. `.gitignore` excludes `.venv/` and `upstream/data/`; the README says how to unzip `data.zip`. `runs/` is committed as evidence. One branch per person, merged into `main` after the other has read it.
- **Division of work:**
  - A: harness, split, runs, scoring, `estimate.py` and its tests, the q370 write-up.
  - B: `SKILL.md`, `methods.md`, the q370 check.
  - Before the pitch, each explains their part to the other (10 min each).
