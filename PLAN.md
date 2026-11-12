# PLAN — a skill for causal discovery on QRData

Pair: Student A, Student B · Repository: *(URL added when the private repository is created)* · Version 3, 12 Nov 2026 (v1 and v2 beside it)
Process: grill-me session → `process/grill-me-transcript.md` → `SPEC.md` (what and why) → this plan (how). Sections 1–5 answer the brief's five cards. Sections 6–10 turn the plan into work we can start on Monday.

## 1 · Benchmark

**Worked example: q213** (a development question; see Scope).

- **What the agent receives:** `question.md` and `arctic.csv` (468 rows, 12 climate variables of the Arctic, such as wind, longwave flux and sea ice). The question: "Which cause-and-effect relationship is more likely? A. Residual_u10m causes Residual_longwave · B. Residual_longwave causes Residual_u10m · C. The causal relation is double sided · D. No causal relationship exists."
- **Correct answer:** D.
- **How the benchmark checks it:** QRData's `eval.py` accepts a multiple-choice answer if it starts with the key's letter (case ignored). Our `score.py` does the same: `tests/test_score.py` checks it against `eval.py`, with 0 disagreements.

**Pilot run** (Claude Code, Sonnet, no skill, 11–12 Nov; records in `runs/`). On q213 the agent answered **A**, wrong. Its reply: it answered "from physical reasoning, not from a causal-discovery test", after finding a weak correlation (0.12) between the two variables. It never tested whether the link survives once the other variables are taken into account.

**What a high score could hide (validity):**

- **Chance:** guessing gives 25% on arctic (4 options) and 33% on flow (3 options).
- **One answer dominates:** "no causal relationship" is the key on 38 of the 50 development questions. A skill that only said "answer no relationship" would score well without teaching any method. So we report two reference scores next to ours: answering "no causal relationship" every time (38 of 50 on dev) and the PC algorithm alone (33 of 50 on dev; `analysis/discovery_check.py`).
- **Training data:** `flow.csv` is a well-known protein-signalling dataset. In 46 of its 50 runs on it, the agent's reply refers to the known signalling network or its source, so it may answer from memory, not from the data.
- **Same graph on both sides:** all questions about one dataset share one answer graph, so the skill may not name any variable or link (section 3).
- **A broken question:** q262 asks whether `p44/42` causes `p44/42` (the same variable twice). We keep it and score it with the official key, and report it.

## 2 · Scope

**How we chose:** we ran the agent without a skill on the development half of each part of QRData and counted the wrong answers a skill could fix. A part only qualifies if the agent fails there often, for reasons a skill can address.

| Part | Questions | Right without a skill | Wrong answers a skill could fix | Decision |
|---|---|---|---|---|
| Statistics | 142 | 75 of 83 (dev) | few | out |
| Effect estimation | 69 | 17 of 31 (dev) | 1 of 14 | out |
| Discovery, simulated data | 100 | 46 of 50 (dev) | — | out |
| **Discovery, real data** | **100** | **20 of 50 (dev)** | **23 of 30** | **in** |

- **Subset:** the 100 causal-discovery questions on real data: 50 on `arctic.csv` (Arctic sea ice), 50 on `flow.csv` (protein signalling). All multiple choice.
- **Our first choice was effect estimation.** Its failures turned out to come from the answer key (estimates near the key but outside its 3% band, doubtful keys), not from a method a skill could teach: only 1 of 14 was fixable. So we widened the scope. *(Analysis: `analysis/estimator_check.py`; plan v2.)*
- **Runtime:** median 10 s per task (max 16 s), about $0.05 per task with Sonnet. One pass over the 100 takes 17 min and $5.10. Budget in section 10.

## 3 · Skill design

**Derived from the failures.** Of the 30 wrong development answers, 23 claim a causal link where the key says none. The replies show why: the agent reasons from domain knowledge ("wind changes moisture and heat transport…") and from correlation, and never tests whether a link survives once the other variables are taken into account. That test is what causal-discovery algorithms do.

- **Procedure** (`SKILL.md`):
  1. Read the two variables and the options.
  2. Check that both variables are columns of the CSV.
  3. Run `scripts/discover.py`: it runs the PC algorithm on all columns and reports whether the two variables are linked, in which direction, and which test removed the link if there is none.
  4. Map the result to an option (`references/reading-the-graph.md`): no link → "no causal relationship"; a directed link → that direction; an undirected link → "double sided" if offered.
  5. Do not answer from domain knowledge or from a correlation alone.
  6. End with `ANSWER: <letter>`.
- **Trigger** (the `description` line): "Use when a question asks which cause-and-effect relationship between two variables is more likely, given a CSV file."
- **Structure:**

  ```
  tasks/.agents/skills/causal-discovery/
    SKILL.md                         trigger + the six steps
    references/reading-the-graph.md  how the script's output maps to the options; what the test assumes
    scripts/discover.py              --csv --x --y [--alpha 0.05]
                                     prints: linked or not, direction, the test that removed the link
  ```

- **What the skill may not contain:** any variable name of `arctic.csv` or `flow.csv`, or any link between them. Development and test questions share the same two answer graphs, so a link written into the skill would be an answer to a test question. A test (T8) searches the skill folder for every column name of both datasets.
- **Multiple skills:** one skill.
- **Outside the skill** (the agent never sees it): `harness/`, `analysis/`, `tests/`, `key/`.

## 4 · Evaluation

- **Comparison:** both runs use the identical command and prompt:

  ```
  claude -p "<prompt>" --model sonnet --output-format stream-json --verbose
         --setting-sources project --strict-mcp-config --allowedTools Bash,Read,Glob,Grep,Skill
  ```

  The prompt never mentions the skill. The skill lives in the task folder, at `tasks/.agents/skills/causal-discovery/`. Each run gets a fresh copy of one task; the only difference is that in the run with the skill, `run_agent.py` also copies the skill in. (Claude Code reads skills from `.claude/skills/`, so that is where the copy goes; Copilot CLI would read `.agents/skills/` directly.)
- **Skill check:** `--setting-sources project` removes our own installed skills, but Claude Code's 22 built-in skills still load in both runs (tested 11 Nov). Each record stores the skills the agent could see and the skills it called. A run is valid if it sees the same skills as the run without ours, plus `causal-discovery`, and calls no other skill. We also report how often the agent called `causal-discovery` at all.
- **Development and test split:** by question, within each dataset, seed 2026 (`key/arctic_flow_split.json`): 25 development and 25 test questions per dataset. *Why by question:* each dataset is a single file, so a split by file would put a whole dataset on one side. We build the skill on development questions only; test questions run once, for the final measurement, and nobody reads their transcripts before then.
- **Metrics** (test set, per arm, also per dataset): accuracy averaged over 3 repeats; for each question, how many of its 3 repeats were right; how often the skill was called; median time and cost per task. Next to them, the two reference scores on the test set: "no causal relationship" every time, and the PC algorithm alone.
- **Decision rule, fixed now:** per question, *win* = the run with the skill got more of its 3 repeats right, *loss* = fewer, *tie* = equal. Sign test on wins and losses, `scipy.stats.binomtest(wins, wins + losses, 0.5)`, threshold p < 0.05. If it is not reached, we write "not enough evidence that the skill helps on this test set" and still report wins, losses and ties. No repeats or questions are added after seeing the result.
- **Power:** if the agent with the skill matched the PC algorithm on dev, it would win about 13 of 50 questions. With 50 test questions, 6 wins and no losses already give p < 0.05.
- **Answer isolation:** each run happens in a fresh temporary copy of the task folder, outside the repository. The full transcript is saved, and the harness flags any run whose transcript names an answer file or the folder `upstream/`. We check flagged runs by hand. A run that read the key or called another skill is invalid and rerun; we report how many.
  - *A check that needed checking:* the first version searched for the bare word `upstream` and flagged 27 runs. All 27 were biology ("PLCγ acts upstream of PIP2"). The check now looks for `upstream/`; `harness/recheck_peeks.py` re-applied it to the stored transcripts: 0 of 100 flagged.

## 5 · Tools and teamwork

- **Agent and model:** Claude Code with Sonnet, non-interactive. The harness already runs it; changing agents would mean redoing the pilots.
- **Batch execution:** `run_agent.py <scope> <arm> <repeats> <model> <side>`, one run after another on one laptop. One record per run, `runs/<scope>-<arm>/<task>-r<k>.json` (answer, seconds, cost, skills seen and called, peek flag), plus the full transcript `.jsonl`.
- **Version control (GitHub):**
  - One private repository; `main` holds only work the partner has read.
  - Each task in section 6 is a GitHub issue with its owner and its "done when" (Pocock's `/to-tickets` can create them; by hand is fine).
  - One branch per issue (`t7-discover`), one pull request per branch, "Closes #7" in its description. The partner reads it and approves; then it is merged. Reading each other's pull requests is how each of us can answer any defence question.
  - Commit messages say what changed and why. `DECISIONS.md` entries name the commit or pull request where the decision happened.
  - `.gitignore` excludes `.venv/` and `upstream/data/`; `runs/` is committed after each measurement; the frozen skill gets the tag `skill-final`.
- **Division of work:**
  - A: harness, runs, scoring, `discover.py` and its tests, analysis.
  - B: failure analysis, `SKILL.md`, `reading-the-graph.md`, the variable-name test, README and `DECISIONS.md`.
  - Both: each round of the development loop; the slides.

## 6 · Tasks

| # | Task | Owner | Done when | After |
|---|---|---|---|---|
| T1 | Repository, `.gitignore`, README setup steps | A | B clones it, follows the README and gets the 100 task folders | — |
| T2 | Scorer agrees with `eval.py` | A | `tests/test_score.py`: 0 disagreements ✔ (12 Nov) | — |
| T3 | Peek check looks for paths, not words | A | `recheck_peeks.py`: 0 of 100 flagged, each change explained ✔ (12 Nov) | — |
| T4 | `make_tasks.py` stops appending the letter-only "Options: a b c d" block to multiple-choice questions | A | Task files show the options once; README notes it | T1 |
| T5 | Runner resumes a stopped run and records the model ID; development baseline, 3 repeats | A | 150 valid records; right count per question | T4 |
| T6 | Failure table for the development baseline | B | Every wrong run has one cause, with a quote from its reply | T5 |
| T7 | `discover.py` with tests | A | On synthetic data from a known graph (X → Y → Z, W unlinked), it reports X–Y linked, X–Z not linked, W unlinked | T1 |
| T8 | `SKILL.md`, `reading-the-graph.md`, and the variable-name test | B | The test finds no column name of either dataset in the skill folder | T6, T7 |
| T9 | Trigger check | B | The agent with the skill calls `causal-discovery` in at least 4 of 5 development questions | T8 |
| T10 | Development loop (section 7) | A + B | Skill frozen, tag `skill-final` | T9 |
| T11 | Test measurement: 50 questions × 2 arms × 3 repeats | A | 300 records; invalid runs rerun and counted | T10 |
| T12 | Analysis with pandas: results table, chart, sign test, reference scores | A | `analysis/results.py` writes the table and chart the README shows | T11 |
| T13 | README, `DECISIONS.md` (4–6 entries), defence slides | B (+ A) | The partner has read and approved each | T12 |
| T14 | Explain your part to the other, 10 min each | A + B | Each answers three questions about the other's part | T13 |

## 7 · Development loop

1. Change one thing in the skill, on its own branch.
2. Run the agent with the skill on the 50 development questions, 3 repeats (about 26 min and $8).
3. Compare, question by question, with the development baseline: wins, losses, ties. Read the transcripts of every loss.
4. Keep the change if wins exceed losses; otherwise undo it. A change that alters the design gets a `DECISIONS.md` entry.

Stop on Fri 27 Nov or after two rounds in a row without a gain; at most four rounds. Test questions and their transcripts stay closed throughout.

## 8 · Milestones

| Date | Milestone |
|---|---|
| Sun 15 Nov | `PLAN.md` and repository URL handed in (T1–T3) |
| Thu 19 Nov | Pitch |
| Sun 22 Nov | Development baseline, failure table, tested `discover.py` (T4–T7) |
| Fri 27 Nov | Skill frozen (T8–T10) |
| Tue 1 Dec | Test measurement done (T11) |
| Fri 4 Dec | Analysis, README, `DECISIONS.md`, slides drafted (T12, T13) |
| Sun 6 Dec | Hand in (Saturday is buffer) |
| Mon 7 Dec | Rehearsal and T14; defence Wed 9 Dec |

## 9 · Risks

| Risk | Early sign | Response |
|---|---|---|
| The agent never calls the skill | T9 below 4 of 5 | Rewrite the `description` line; report the call rate either way |
| The skill helps only by saying "answer no relationship" | Dev gains match the "always no relationship" score, not the PC score | Report it as such; the skill must state a test, not a default answer |
| The agent answers from memory (flow) | Replies name "the known network" | Report the flow and arctic results separately |
| Overfitting to dev | Gains on dev with nothing on test | At most four rounds; one change at a time; no variable names in the skill |
| Budget runs out | Spend passes $50 before T11 | Stop the loop; the test measurement has priority |
| One of us is away | A task blocks the other's | Issues and branches keep work visible; the README lets either run anything |
| The model changes during the project | The model ID in the records differs | Rerun the baseline with the new model |

## 10 · Budget (Sonnet: median 10 s and about $0.05 per run)

| Item | Runs | Time | Cost |
|---|---|---|---|
| Development baseline, 3 repeats | 150 | 26 min | ≈ $8 |
| Development loop, up to 4 rounds | 600 | 1 h 45 min | ≈ $31 |
| Test measurement | 300 | 52 min | ≈ $15 |
| Reruns and margin (20%) | | 35 min | ≈ $11 |
| **Total from now** | | **≈ 3.5 h** | **≈ $65** |
