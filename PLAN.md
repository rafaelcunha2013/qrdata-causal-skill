# PLAN — a skill for causal effect estimation on QRData

Pair: Student A, Student B · Repository: *(URL added when the private repository is created)* · Version 2, 12 Nov 2026 (v1 beside it)
Process: grill-me session → `process/grill-me-transcript.md` → `SPEC.md` (what and why) → this plan (how). Sections 1–5 answer the brief's five cards. Sections 6–10 turn the plan into work we can start on Monday.

## 1 · Benchmark

**Worked example: q325** (a development question; see Scope).

- **What the agent receives:** `question.md` and `ihdp_4.csv` (747 children; `treatment`, outcome `y`, covariates `x1`–`x25`). The question: "What is the Average treatment effect on the treated of the dataset? Please round to the nearest hundredth."
- **Correct answer:** 4.00.
- **How the benchmark checks it:** QRData's `eval.py` takes the first number in the answer and accepts it if it lies strictly within 3% of the key, so here between 3.88 and 4.12 (both excluded). Multiple-choice answers are accepted if they start with the key's text. Our `score.py` does the same: `tests/test_score.py` checks it against `eval.py` on 11 edge cases and the 69 first-run answers, with 0 disagreements.
- *First candidate was q317. After the split it fell on the test side, so we replaced it: we may not study test questions while we build.*

**Pilot runs** (Claude Code, no skill, 11–12 Nov; records in `runs/`):

| Run | Model | Questions | Right |
|---|---|---|---|
| Statistics pilot | Sonnet | 10 | 9 |
| Causal pilot | Sonnet | 10 | 5 |
| Effect estimation, one repeat | Sonnet | 69 | 39 (57%): dev 17 of 31, test 22 of 38 |
| Effect estimation, dev only, one repeat | Haiku | 31 | 14 (45%) |

On q325 the agent answered 4.14 (wrong: 3.5% off). Its reply also gives the plain regression (4.18) and the difference in means (4.23). All three miss the key.

**What the key is.** Before designing the skill we asked which standard estimator reproduces the key (`analysis/estimator_check.py`, development questions only, IHDP and Jobs, 20 questions):

| Estimator | Within 3% of the key |
|---|---|
| Difference in means | 2 of 20 |
| Inverse propensity weighting | 7 of 20 |
| Regression with treatment and covariates | 8 of 20 |
| Separate regressions per group (T-learner) | 10 of 20 |
| *The agent without a skill (Sonnet, first run)* | *10 of 20* |

No estimator reproduces the key reliably. The five development ATT keys on IHDP are all exactly 4.00, while the estimators on the same files spread from 3.8 to 4.9. Our hypothesis: the IHDP key is the effect that was set when the IHDP outcomes were simulated, not a number computed from the file. If so, on IHDP a correct method lands inside the 3% band only by luck. (Task T4 checks how QRData made its keys.)

**Validity: what could make a high score misleading:**

- **Lenient scoring:** only the first number counts, within 3%; a multiple-choice answer only has to start with the key.
- **Chance:** 5 of the 69 questions are yes/no, right half the time by guessing. For the 64 numerical ones chance is near zero, but on IHDP (30 questions) a sound method is right only about half the time (table above).
- **Training data:** QRData and its sources (textbooks, the IHDP and Jobs datasets) are public, so the model may have seen the answers.
- **Doubtful keys:**
  - q370 (key 0.10): the agent's regression discontinuity gives 9.75 more deaths at 21.
  - q402 (key 255051): the question asks for the effect on *log* net wealth, rounded to an integer. The key is the effect in pounds: exp(13.188) − exp(12.538) ≈ 255,000.
  - We always score with the official key, and report a second score without the doubtful questions (rule in section 4).

## 2 · Scope

- **Subset:** the 69 effect-estimation questions (QRData questions with the keyword "Causality" that are not causal discovery). Sources: IHDP 30, *Causal Inference for the Brave and True* 24, Jobs 10, *Quantitative Social Science* 5. 64 numerical, 5 multiple choice.
- **Rationale:**
  - Statistics was left out: 9 of 10 right in the pilot leaves almost no room for a skill.
  - Causal discovery (150 + 50) was left out: its answer graphs are published, so a skill could help there only by containing the answers.
  - Effect estimation is a procedure a skill can teach without holding answers.
- **Reported per source**, because the sources behave differently: on IHDP the ceiling is set by the key (section 1); the textbook questions fail for reasons a skill can address (section 3).
- **Runtime:** Sonnet median 12 s per task, one pass over the 69 in 15 min for $4.25; Haiku median 21 s, about $0.005 per task. Budget in section 10.

## 3 · Skill design

**Derived from the failures, not from the topic.** We classified every wrong development answer of both dev pilots (Sonnet 14 of 31 wrong, Haiku 17 of 31):

| Cause | Sonnet | Haiku | Can a skill fix it? |
|---|---|---|---|
| Estimator noise against a simulated key (IHDP) | 7 | 6 | Hardly: the best fixed estimator scores the same as the agent |
| Method choice on observational data (Jobs, binary outcome) | 3 | 4 | Partly: the agent switches method between questions; a fixed rule makes it consistent |
| The question fixes the model, the agent chose another | 1 | 2 | **Yes:** read the model off the question |
| Answer format | 0 | 2 | **Yes:** keep the question's unit; always end with the `ANSWER:` line |
| A library is missing | 1 | 1 | No: a harness fix for both arms (T3) |
| Doubtful key | 2 | 2 | No, and it must not try |

Examples. q400 says "message and age as predictors… if the voter's age was 25": Sonnet computed the interaction model (0.066) and then reported the model without it. On q362 Haiku computed 8.53% and answered `8.53`, which the scorer reads as 8.53, not 0.0853. On q332 Haiku's estimate was inside the band, but its reply had no `ANSWER:` line.

So the skill teaches three things: **read the specification off the question**, **answer in the question's format**, and **use one estimator rule consistently**.

- **Procedure** (`SKILL.md`):
  1. Write down what the question fixes: the estimand (ATE, ATT, ATC, "should we control for X?"), the model terms it names, the conditions it sets (an age, a subgroup, a time window), the scale and rounding of the answer.
  2. Name the design: randomized, observational with confounders, instrumental variables, difference-in-differences, regression discontinuity, or synthetic control.
  3. Inspect the CSV: treatment, outcome and covariate columns; binary or continuous outcome.
  4. If the question fixes the model, fit exactly that model. Otherwise choose the method from `references/methods.md` and compute it with `scripts/estimate.py`.
  5. Compare with the naive difference in means (sign and size), and check the answer against step 1: estimand, condition, scale.
  6. Round as asked and keep the question's unit (a percentage keeps its `%`); end with `ANSWER: <value>`.
- **Trigger** (the `description` line): "Use when a question asks for a treatment effect (ATE, ATT, ATC) or whether to control for a variable, using CSV data."
- **Structure:**

  ```
  skills/causal-effect/
    SKILL.md                trigger + the six steps
    references/methods.md   one section per design: when it applies, the default estimator, a snippet
    scripts/estimate.py     --csv --treatment --outcome --estimand --method [--covariates]
                            prints the estimate and the naive difference in means
  ```

  `estimate.py` starts with `diff_means`, `regression`, `t_learner` and `ipw` (the four checked above). The method names in `methods.md` match its `--method` values.
- **Multiple skills:** one skill.
- **Outside the skill** (the agent never sees it): `harness/`, `analysis/`, `tests/`, `key/`.

## 4 · Evaluation

- **Comparison:** both arms run the identical command and prompt:

  ```
  claude -p "<prompt>" --model <model> --output-format stream-json --verbose
         --setting-sources project --strict-mcp-config --allowedTools Bash,Read,Glob,Grep,Skill
  ```

  The prompt never mentions the skill. The only difference: in the skill arm, `run_agent.py` copies `skills/causal-effect/` into the task's `.claude/skills/`. Both arms get the same Python environment (with scikit-learn after T3).
- **Skill check:** `--setting-sources project` removes our user-installed skills, but Claude Code's 22 built-in skills still load in both arms (tested 11 Nov). Each record stores the skills loaded and the skills called. A run is valid if its loaded skills equal the baseline's plus `causal-effect` (skill arm only) and it calls no other skill. We also report how often the skill arm called `causal-effect` at all.
- **Development and test split:** by data file, within each source, seed 2026 (`key/effect_split.json`): 31 dev and 38 test questions. We build the skill on dev questions only; test questions run once, for the final measurement, and nobody reads their transcripts before then. *Limitation:* IHDP asks the same three questions on 10 files, so a dev IHDP question already teaches the method a test IHDP question needs.
- **Metrics** (test set, per arm, also per source): accuracy averaged over 3 repeats; for each question, how many of its 3 repeats were right; median time and cost per task; how often the skill was called.
- **Decision rule, fixed now:** per question, *win* = the skill arm got more of its 3 repeats right, *loss* = fewer, *tie* = equal. Sign test on wins and losses, `scipy.stats.binomtest(wins, wins + losses, 0.5)`, threshold p < 0.05. If it is not reached, we write "not enough evidence that the skill helps on this test set" and still report wins, losses and ties. No repeats or questions are added after seeing the result.
- **Second score, fixed now:** the same rule without the questions listed as doubtful in `DECISIONS.md` *before* the test run. The official-key score stays the headline.
- **Power:** with 38 test questions, at least 6 questions must change, all wins, to reach p < 0.05. Even with Haiku the failure table predicts a modest effect (section 3), so "not enough evidence" is a possible result, and an honest one.
- **Answer isolation:** each run happens in a fresh temporary copy of the task folder, outside the repository. The full transcript is saved, and the harness flags any run whose transcript names an answer file (`causal.json`, `effect.json`, `QRData.json`, `upstream`); we check flagged runs by hand. A run that peeked or called another skill is invalid and rerun; we report how many. First run: 0 of 69 flagged.

## 5 · Tools and teamwork

- **Agent and model:** Claude Code with **Haiku**, non-interactive. Decided from the two dev pilots: Haiku leaves 4 failures the skill can fix against Sonnet's 1, and one run costs about $0.005 against $0.06. Its runs are slower (median 21 s against 12 s). Changing agents would mean redoing the pilots.
- **Batch execution:** `run_agent.py <scope> <arm> <repeats> <model> <side>`, one run after another on one laptop. One record per run, `runs/<scope>-<arm>[-<model>]/<task>-r<k>.json` (answer, seconds, cost, skills loaded and called, peek flag), plus the transcript `.jsonl`.
- **Version control (GitHub):**
  - One private repository; `main` holds only work the partner has read.
  - Each task in section 6 is a GitHub issue with its owner and its "done when" (`/to-tickets` can create them; by hand is fine).
  - One branch per issue (`t7-estimate`), one pull request per branch, "Closes #7" in its description. The partner reads it and approves; then it is merged. Reading each other's pull requests is how each of us can answer any defence question.
  - Commit messages say what changed and why. `DECISIONS.md` entries name the commit or pull request where the decision happened.
  - `.gitignore` excludes `.venv/` and `upstream/data/`; `runs/` is committed after each measurement; the frozen skill gets the tag `skill-final`.
- **Division of work:**
  - A: harness, environment, runs, scoring, `estimate.py` and its tests, analysis.
  - B: key checks, failure analysis, `SKILL.md`, `methods.md`, README and `DECISIONS.md`.
  - Both: each iteration of the development loop; the slides.

## 6 · Tasks

| # | Task | Owner | Done when | After |
|---|---|---|---|---|
| T1 | Repository, `.gitignore`, README setup steps | A | B clones it, follows the README and gets 69 task folders | — |
| T2 | Scorer agrees with `eval.py` | A | `tests/test_score.py`: 0 disagreements ✔ (12 Nov) | — |
| T3 | Add scikit-learn to the environment and the prompt | A | q371 runs without "not installed", both arms | T1 |
| T4 | Check how QRData made its keys (paper, repository) and the doubtful keys q370, q402 | B | One `DECISIONS.md` entry each, with the evidence | — |
| T5 | Runner resumes a stopped run and records the model ID; dev baseline, 3 repeats | A | 93 valid records; right count per question | T3 |
| T6 | Failure table for the dev baseline | B | Every wrong run has one cause from section 3, or a new one | T5 |
| T7 | `estimate.py` with tests | A | On synthetic data with a known effect, each method recovers it within 0.05 | T1 |
| T8 | `SKILL.md` and `methods.md` v0 | B | Method names match `estimate.py`; no question-specific content | T6, T7 |
| T9 | Trigger check | B | The skill arm calls `causal-effect` in at least 4 of 5 dev questions | T8 |
| T10 | Development loop (section 7) | A + B | Skill frozen, tag `skill-final` | T9 |
| T11 | Test measurement: 38 questions × 2 arms × 3 repeats | A | 228 records, invalid runs rerun and counted | T10 |
| T12 | Analysis with pandas: results table, chart, sign test, per source | A | `analysis/results.py` writes the table and chart the README shows | T11 |
| T13 | README, `DECISIONS.md` (4–6 entries), defence slides | B (+ A) | The partner has read and approved each | T12 |
| T14 | Explain your part to the other, 10 min each | A + B | Each answers three questions about the other's part | T13 |

## 7 · Development loop

1. Change one thing in the skill, on its own branch.
2. Run the skill arm on the 31 dev questions, 3 repeats (about 35 min with Haiku).
3. Compare per question with the dev baseline: wins, losses, ties. Read the transcripts of every loss.
4. Keep the change if wins exceed losses; otherwise revert. A change that alters the design gets a `DECISIONS.md` entry.

Stop at the freeze date or after two iterations in a row without a gain; at most four iterations. Test questions and their transcripts stay closed throughout.

## 8 · Milestones

| Date | Milestone |
|---|---|
| Sun 15 Nov | `PLAN.md` and repository URL handed in (T1, T2) |
| Thu 19 Nov | Pitch |
| Sun 22 Nov | Dev baseline, failure table, tested `estimate.py` (T3–T7) |
| Fri 27 Nov | Skill frozen (T8–T10) |
| Tue 1 Dec | Test measurement done (T11) |
| Fri 4 Dec | Analysis, README, `DECISIONS.md`, slides drafted (T12, T13) |
| Sun 6 Dec | Hand in (Saturday is buffer) |
| Mon 7 Dec | Rehearsal and T14; defence Wed 9 Dec |

## 9 · Risks

| Risk | Sign | Response |
|---|---|---|
| The agent never calls the skill | T9 below 4 of 5 | Rewrite the `description` line; report the call rate either way |
| No room for the skill | The 3-repeat dev baseline fails mostly on IHDP noise and doubtful keys | Report a null result; the failure table explains it |
| The IHDP key is not computable from the file | T4 confirms it | Report IHDP separately; do not tune the skill to it |
| Overfitting to dev | Gains on dev questions that share a file with nothing on test | At most four iterations; one change at a time |
| Time runs out | The loop is not frozen by Fri 27 Nov | Stop the loop; the test measurement has priority |
| One of us is away | A task blocks the other's | Issues and branches keep work visible; the README lets either run anything |
| The model changes during the project | The model ID in the records differs | Rerun the baseline with the new model |

## 10 · Budget (Haiku: median 21 s and about $0.005 per run)

| Item | Runs | Time | Cost |
|---|---|---|---|
| Pilots so far (Sonnet and Haiku) | 151 | 36 min | ≈ $6.4 |
| Dev baseline, 3 repeats | 93 | 35 min | ≈ $0.5 |
| Development loop, up to 4 iterations | 372 | 2 h 10 min | ≈ $2 |
| Test measurement | 228 | 1 h 20 min | ≈ $1.2 |
| Reruns and margin (20%) | | 50 min | ≈ $0.8 |
| **Total from now** | | **≈ 5 h** | **≈ $4.5** |

Time, not money, is the limit: the runs go one after another on one laptop, so the loop's dev runs are planned for evenings.
