# grill-me session — QRData example (SIMULATED)

Simulated for the BPP tutorial on 11 Nov 2026. The interviewer is a coding agent (Claude Code, Opus) following Matt Pocock's grill-me and grilling skills as written. It has read access to the project brief and this folder. The student pair is played by a second agent (Sonnet) given a first-year persona. Both sides are verbatim.

## Pair

> /grill-me We are a pair of first-year students in a Python course. Our final project: build an agent skill that helps a coding agent answer the questions of a benchmark, then measure whether the agent does better with our skill than without it. Phase 1 is a plan, PLAN.md, due Sunday. Our benchmark is QRData (causal and statistical questions on CSV data). Help us work out the plan.

## Agent — round 1

❓ **Q1** - **Which part of QRData?**: In your pilot the agent got 9 of 10 statistics questions right, but only 5 of 10 causal ones (it missed q234, q236, q242, q358 and q370). A skill can only show its value on questions the agent gets wrong without it. With 9 of 10 already right, statistics leaves almost no room to improve. Your options:
- (a) causal questions only: the 269 questions with the keyword "Causality"
- (b) statistics questions only: the other 142
- (c) both

You will narrow the subset further in a later round.

➡️ Yes: (a) causal only. Your pilot already gives the reason you will write in PLAN.md: that is where the agent fails.

---

❓ **Q2** - **Agent and model**: Your pilot ran Claude Code non-interactively (`claude -p`) with the Sonnet model. Both arms of the comparison must use the same agent and model. You could switch to another agent, for example GitHub Copilot CLI (the brief links to it), but then you would have to rebuild and rerun the pilot.

➡️ Yes: keep Claude Code with Sonnet in both arms. Your harness already runs it, and one task took 6–18 seconds in the pilot.

---

❓ **Q3** - **Answer isolation**: `run_agent.py` starts the agent inside `tasks_causal/qNNN/`, but it allows the Bash tool. That means nothing stops the agent from reading `../../key/causal.json` or `upstream/QRData.json`, which contain every answer. Also, you save only the agent's final reply, so you cannot check afterwards which files it opened.

➡️ Yes: before each task, copy only that task's folder (`question.md` and its CSV files) to a fresh temporary folder outside your repository, and run the agent there. Save the full transcript of each run, not just the final reply. After each run, search the transcripts for `key`, `QRData` and `upstream`.

---

❓ **Q4** - **Validity: what could make a high score misleading?**: Here is what I found in your files:
- **Guessing scores points.** Of the causal multiple-choice answers, 75 are "C". Every yes/no question is right half the time by chance.
- **Scoring is lenient.** `eval.py` takes the *first* number in the answer and accepts it if it is within 3% of the key. For multiple choice, it only checks that the answer *starts with* the key's text.
- **The answers may already be known.** QRData is public, and so are its sources: the textbooks and the published causal graphs for the arctic and flow-cytometry data. So the model may have seen them during training.
- **Some keys look doubtful.** For q370 the key is 0.10, but a standard regression-discontinuity fit on those data gives 9.75, which is what your agent answered.

➡️ Yes: put these four points in PLAN.md under Validity. Also report the score from pure guessing next to your measured scores, so a reader can see how much above chance the agent is.

## Pair — answers to round 1

Q1: A: Okay, causal only. B: Fine with it, since that is where the pilot showed the agent failing (5 of 10). Quick question though: the 269 causal questions, do we have to run all of them? With about 10 seconds each, A thinks it is fine, but B is worried about API cost if we run both arms several times.

Q2: A: Keep Claude Code with Sonnet, the harness already works and we don't have time to rebuild the pilot. B: Agreed. Can we run the agent more than once per question? We only have one laptop between us, so we can't run two things in parallel.

Q3: A: Makes sense, copying only the task folder is easy, that is just shutil.copytree in a loop and we can do that. B: I don't fully get why we search the transcripts for "key", "QRData" and "upstream", is that only to see if the agent peeked? If it did peek, what do we do with that run, throw it away?

Q4: B: The guessing point makes sense, I know about chance level from statistics. A: We will put all four in PLAN.md. One thing we don't understand: "regression-discontinuity", we haven't heard of it, so we can't judge ourselves whether the key for q370 is wrong. Do we have to check the doubtful keys ourselves, or just mention them as a risk? We only have about 3 weeks and other courses, so we would prefer just mentioning them and maybe checking one or two.

## Agent — round 2

❓ **Q1** - **Which causal questions, and how many?**: You don't have to run all 269; the brief allows a subset. The 269 causal questions are of three kinds:
- **Full-graph causal discovery:** 150 multiple-choice questions on only three datasets (arctic, flow cytometry, neuropathic pain). Example: "which causes which?" (q236).
- **Pairwise causal discovery:** 50 multiple-choice questions, all on neuropathic-pain data.
- **Effect estimation:** 69 questions (64 numerical, 5 multiple-choice). They ask for a treatment effect (ATE/ATT/ATC), what to control for, matching, difference-in-differences and similar. Examples: q317, q358, q366, q370.

The two discovery kinds have fixed answer graphs that are published. A skill that helps on them risks simply containing those graphs, which would put the answers inside your skill. Effect estimation is a procedure: choose a method, then compute. That is something a skill can teach without holding any answer.

On cost: at about 10 s per task, 269 tasks take about 45 minutes for one pass of one arm. 69 tasks take about 12 minutes.

➡️ Yes: use only the 69 effect-estimation questions. You can run them several times in both arms. In PLAN.md, say that you left out discovery because a skill could only help there by holding the published graphs.

---

❓ **Q2** - **Record time and cost for every run**: Yes, you can run each question more than once. On one laptop, you run them one after another. We fix the number of repeats next round, once the size is settled. Right now you cannot tell what a run costs: `run_agent.py` saves only the reply and the seconds. Claude Code's JSON output also reports the cost of each call (`total_cost_usd`).

➡️ Yes: also save `total_cost_usd` and the repeat number in each record, under a file name such as `runs/<arm>/q317-r1.json`. Your first pass then tells you exactly what one repeat costs, and you can cap the number of repeats to fit your budget.

---

❓ **Q3** - **What to do with a run that peeked**: Yes, the search is only there to catch peeking. A run that read the key measures nothing about your skill. Counting it as right would inflate the score, and counting it as wrong would punish the agent for a leak in your setup.

➡️ Yes: if a run peeked, mark it invalid, fix the leak, and rerun that task. In your results, report how many runs you had to throw away (hopefully zero).

---

❓ **Q4** - **Doubtful keys in scoring**: Mentioning them as a risk and checking one or two is enough. Regression discontinuity is a method for estimating an effect when a cut-off decides who gets treated. Here the cut-off is age 21, the legal drinking age. You don't need to master it to flag the key. The open question is how you score a question whose key you believe is wrong.

➡️ Yes: always score with the official key, exactly as `eval.py` does, so your numbers are comparable to the benchmark. In PLAN.md, list the one or two keys you checked (q370 first) and say what you found. Do not change any key.

## Pair — answers to round 2

Q1: A: 69 questions is doable, and about 12 minutes per pass fits our budget. B: Fine with it, the argument about the published graphs makes sense to us. We didn't know the discovery answers are public. But the pilot's failures (q234, q236, q242) were mostly discovery questions, right? Then our skill won't fix the questions where we saw the agent fail. Is that okay for the project? Also, only 5 of the 69 are multiple-choice, so the guessing baseline will be mostly about numbers, not chance. Do we still report a guessing score?

Q2: A: Yes, saving total_cost_usd and the repeat number is easy, we'll write one JSON file per run in runs/<arm>/. B: Good, we have a limited API budget, so a first pass to measure the cost is what we need. One constraint: we only have one laptop, so both arms will take double the time. We'd like to start with a small number of repeats, like 3, and see.

Q3: A: Okay: peeked run = invalid, fix the leak, rerun. We'll report the count of discarded runs. B: Makes sense, otherwise the score would be wrong in either direction. A question: what if the agent only mentions the word "key" in its own answer, for example "key variable"? Then the search for "key" would flag a run that did not peek. Should we check these by hand?

Q4: B: Mentioning doubtful keys as a risk and scoring with the official key is fine with us, then our numbers match the benchmark. A: We'll check q370 and maybe one more, and write down what we found. We only understood the regression discontinuity idea after your explanation (cut-off at age 21), so B will check the q370 fit and A will write it up, so that the work is split fairly.

## Agent — round 3

❓ **Q1** - **Worked example, and a new baseline on your 69**: Yes, it is fine that your skill won't touch the discovery failures. You are assessed on planning, building and measuring, not on the score. But your old pilot contains only 4 of the 69 questions: q317 and q366 were right, q358 and q370 were wrong. So you don't yet know how often the agent fails on your subset.

q317 makes a good worked example:
- **What the agent receives:** `ihdp_1.csv` and the question "What is the Average treatment effect on the control?"
- **The key:** 4.06
- **The agent's answer:** 4.09. That counts as right, because it is within the 3% tolerance.
- **The lesson:** the agent also computed a plain regression, which gives 3.90. That is 3.9% off, so it would have been scored wrong. The choice of method decides the score.

About B's question on "key variable": search for the file names `causal.json`, `QRData.json` and `upstream`, not the word "key". If a run still gets flagged, check it by hand.

➡️ Yes: use q317 as the worked example. Before Sunday, run one baseline pass over all 69 questions (about 12 minutes) and report that pass as your pilot. It tells you how much room there is, and what one pass costs.

---

❓ **Q2** - **Development / test split**: The 69 questions come from four sources:
- **IHDP:** 30 questions = 10 files × the same 3 questions (ATE, ATT, ATC)
- **Jobs:** 10 questions, 10 files
- *Causal Inference for the Brave and True*: 24 questions, mixed methods
- *Quantitative Social Science*: 5 questions

Questions on the same file must stay on the same side of the split. Otherwise you tune your skill on a dataset you later test on. Note also that IHDP questions are near-copies of each other across files, so a dev IHDP question already teaches the method that a test IHDP question needs. Say that in PLAN.md as a limitation.

➡️ Yes: split by data file, about half of each source on each side, drawn with a fixed seed: about 34 dev and 35 test. Build the skill using only the dev questions. Run the test questions only for the final measurement.

---

❓ **Q3** - **Skill procedure (added value)**: Without your skill, the agent picks a method ad hoc, as in q317 (where it tried three) and q358 (where it controlled for a variable it should not have). Your skill would give it a fixed procedure:
1. Name the **estimand**: ATE, ATT, ATC, or a "should we control for X?" question.
2. Name the **design**: randomized experiment, observational data with confounders, instrumental variables, difference-in-differences, regression discontinuity, or synthetic control.
3. Inspect the CSV: find the treatment, outcome and covariate columns.
4. Look up the method for that estimand and design in a reference table, then compute it with pandas or statsmodels.
5. Sanity-check the result: compare its sign and size with the naive difference in means.
6. Round as the question asks and end with `ANSWER: <value>`.

➡️ Yes: plan this six-step procedure. Each method in the reference table is named after its textbook, so the skill teaches methods and never contains answers.

---

❓ **Q4** - **Metrics and repeats**: Starting with 3 repeats is fine: 35 test questions × 2 arms × 3 repeats is about 35 minutes on one laptop. B is right that a guessing score means little here: with 64 numerical questions, chance is close to zero.

➡️ Yes: report these for each arm on the test set:
- accuracy, averaged over the 3 repeats
- for each question, how many of its 3 repeats were right, so you can list the questions where the skill made a difference
- median time and cost per task

Drop the guessing baseline. Mention chance level in one sentence for the 5 multiple-choice questions.

## Pair — answers to round 3

Q1: A: Okay, q317 as the worked example. It's useful that the same question can be right or wrong depending on the method, it shows why the skill matters. A will run the baseline pass over all 69 and write the harness change (search for causal.json, QRData.json, upstream). B: We understand "key variable" is no longer a problem. Constraint: we have the pass of about 12 minutes only if the laptop is free, and B has an exam on Thursday, so we'll run it on Friday at the latest, before the Sunday deadline. Is it okay if the baseline in PLAN.md is labelled as a first run of one repeat?

Q2: B: We understand why the split is by file. Question: "about half of each source on each side" for Quantitative Social Science that has only 5 questions, how do we split them? If those 5 are on 2 or 3 files, we'd have maybe 1 or 2 files each side, is that fine? A: The fixed seed is easy (random.seed with a number we write in PLAN.md). We'll write the IHDP near-copy limitation in PLAN.md.

Q3: A: The six steps are clear and we can write them as a SKILL.md. B: Two terms we don't know well: "instrumental variables" and "synthetic control", we haven't heard of them in our stats course. We know difference in means and regression, but not matching or difference-in-differences well either. Do we have to put every method in the reference table, or only those used in the dev questions? We'd prefer the second, because we don't have time to learn six methods in 3 weeks. Also, "reference table" for each method: is that just a short paragraph and a code snippet with statsmodels?

Q4: A: Accepted: accuracy averaged over 3 repeats, per-question count out of 3, and median time and cost. B: Okay to drop the guessing baseline for numbers, and write one sentence on chance for the 5 multiple-choice questions. We'd like to double check one thing: with only 35 test questions, a difference of one or two questions is probably noise. Can we say that in the limitations, and should we say how big a difference we'd consider real?

## Agent — round 4

❓ **Q1** - **The no-skill arm: what exactly differs between the arms?**: Yes, it's fine to label the Friday baseline in PLAN.md as "first run, one repeat". Now the comparison itself. Your harness passes `--disable-slash-commands`, which switches all skills off. So the skill arm cannot use that flag. If the two arms differ in that flag, you are comparing more than your skill. Without the flag, other skills installed on your laptop could also load, in either arm.

➡️ Yes: run both arms with the identical command and the identical prompt (the prompt never mentions the skill). The only difference is that, in the skill arm, the harness copies your skill folder into `.claude/skills/` inside the temporary task folder. Then check the transcripts: in the skill arm, the agent actually loaded your skill; in both arms, no other skill was loaded. In each skill-arm record, also store whether your skill was used.

---

❓ **Q2** - **Trigger and folder structure**: The trigger is the `description` line at the top of `SKILL.md`. It is the only part the agent reads before deciding whether to load the skill. On the methods: you only need the ones your dev questions use. Instrumental variables and synthetic control are each used by only 2–3 of the 69 questions, so they may not appear in your dev set at all. Each method entry is what you guessed: a short paragraph saying when to use the method, plus a statsmodels snippet.

```
causal-effect/
  SKILL.md              description (trigger) + the six steps
  references/methods.md one section per method from the dev questions
```

The harness (`make_tasks.py`, `run_agent.py`, `score.py`) stays outside the skill folder; the agent never sees it.

➡️ Yes: use the description "Use when a question asks for a treatment effect (ATE, ATT, ATC) or whether to control for a variable, using CSV data." Use this two-file structure with no scripts, and add a script only if your dev runs show the agent miscoding the same method again and again. In step 4, add a fallback for when no method in the table fits: "regression of the outcome on treatment and all covariates".

---

❓ **Q3** - **When is a difference real?**: You're right: with 35 test questions, one or two questions is noise. On Quantitative Social Science: `social.csv` (3 questions) goes on one side, and `women.csv` and `MPs.csv` (1 each) on the other. That's fine.

For a test, compare the two arms question by question. A question is a *win* if the skill arm got more of its 3 repeats right, a *loss* if it got fewer, and a *tie* if equal. Ignore the ties, and run a sign test: `scipy.stats.binomtest(wins, wins + losses, 0.5)`. For example, if 10 questions changed, you need at least 9 wins for p < 0.05; 8 of 10 is not enough.

➡️ Yes: in PLAN.md, state this test and the threshold p < 0.05 now, before you see any results. Put the "one or two questions is noise" point under limitations.

---

❓ **Q4** - **Repository and division of work**: Your folder is not a git repository yet, and `upstream/` holds 319 MB of unzipped data. That is too large to commit comfortably.

➡️ Yes:
- **Repository:** one private repository. Add `.venv/` and `upstream/data/` to `.gitignore`, and write in the README how to unzip `data.zip`. Commit the `runs/` JSON files, since they are your evidence. Each piece of work goes on its own branch and is merged into `main` after the other person has read it.
- **Division:** A owns the harness and the measurement (split, runs, scoring). B owns the skill (`SKILL.md`, `methods.md`). As you agreed, B checks q370 and A writes it up. Since the defence questions go to individual students, each of you explains the other's part to them once before the pitch.

## Pair — answers to round 4

Q1: A: Okay, same command and same prompt in both arms, and the harness only copies the skill folder into .claude/skills/ in the task folder. We'll drop --disable-slash-commands. B: We don't fully understand how we check that "no other skill was loaded" in the transcripts. What do we search for, the skill name in the transcript? Also, A's laptop probably has other skills installed (from other courses), so if they load in both arms, is it enough to report that and discard those runs, or do we need a clean setup? We would prefer not to reinstall anything.

Q2: A: Description line and the two-file structure (SKILL.md + references/methods.md) are fine, the fallback regression is easy to add. But push-back: in tutorial the lecturer said the course expects at least one Python script inside the skill folder that SKILL.md tells the agent to run while solving a task. So "no scripts" does not work for us. We'd rather plan one small script now, not wait until the dev runs show miscoding. B suggests a script that takes the CSV, the treatment column, the outcome column and the method, and prints the estimate (and the naive difference in means for the step 5 sanity check). A: it can live in causal-effect/scripts/ and SKILL.md step 4 and 5 say to run it. The runner, scorer and analysis stay outside, as you said. Is that a good use of a script? We worry it is a lot for B alone in 3 weeks, so we'd start with the difference in means and a regression with covariates, and add other methods only if the dev questions need them.

Q3: B: Understood, we like that the sign test is fixed before we see results. Question: if only, say, 6 questions change, we can never reach p < 0.05 (needs 6 of 6 wins). Is that okay, and do we just report it as "not enough evidence"? A: We'll write the test and the threshold in PLAN.md now, and the limitation about 35 questions being noisy. We'll put the Quantitative Social Science split (social.csv on one side, women.csv and MPs.csv on the other) in the plan too.

Q4: A: One private repository, .gitignore for .venv/ and upstream/data/, commit runs/ is okay, and the README explains how to unzip data.zip. A owns the harness, B owns the skill. B: Pushing back a little on one thing: with the script now in the skill, B's part is bigger than A's. Can A write the script's tests or take the script, and B keep SKILL.md and methods.md plus the q370 check? We'd like the work split fairly. We also have never used branches and merging, so we'd like to keep it simple: a branch per person, and merge after the other has read it. Is it okay to explain each other's part before the pitch by a 10 minute talk each?

## Agent — round 5

❓ **Q1** - **Keeping other skills out without reinstalling**: You don't need a clean laptop. Your other courses' skills and plugins are switched on in A's user settings (`~/.claude/`). Claude Code has a flag, `--setting-sources project`, that loads only the settings of the folder the agent runs in, so those user settings stay off.

To check it, save transcripts with `--output-format stream-json`. Then:
- **What the session had:** the first message of each transcript (`"type": "system"`, `"subtype": "init"`) lists the skills and plugins the session loaded.
- **What the agent used:** every time the agent uses a skill, the transcript has a tool call with `"name": "Skill"` and the skill's name. Search for `"name": "Skill"` (with the quotation marks).

➡️ Yes: add `--setting-sources project` to the command in both arms. Before the full run, run one task in each arm and read its init message: the baseline should list no skills, and the skill arm only `causal-effect`. During the real runs, the harness marks any run that used a skill other than `causal-effect` as invalid, the same way as a peeked run, and you report how many there were.

---

❓ **Q2** - **The script, and who owns it**: Your push-back is right; plan the script now. B's design is a good use of a script: one fixed computation the agent would otherwise rewrite, and possibly get wrong, in every task.

`causal-effect/scripts/estimate.py --csv <file> --treatment <col> --outcome <col> --method <name> [--covariates ...]`

It prints the estimate and the naive difference in means. Start with two methods (`diff_means`, `regression`) and add others only if the dev questions need them. Steps 4 and 5 in `SKILL.md` tell the agent to run it. Explaining each other's part in a 10-minute talk each before the pitch is fine.

➡️ Yes: A takes the script and its tests, since A already writes the Python harness. B keeps `SKILL.md`, `methods.md` (whose method names must match the script's `--method` values) and the q370 check. One branch per person, merged into `main` after the other has read it.

---

❓ **Q3** - **When too few questions change**: Yes, that is fine, and it is an honest result. With 6 changed questions, even 6 of 6 wins gives p ≈ 0.03, so 6 is the smallest number that can reach significance, and only with no losses at all.

➡️ Yes: if the test does not reach p < 0.05, you write "not enough evidence that the skill helps on this test set", and still report the wins, losses and ties. Do not add more repeats or questions after you have seen the result in order to reach significance.

## Pair — answers to round 5

Q1: A: Accepted, we add --setting-sources project and --output-format stream-json to both arms. We'll run one task per arm first and read the init message, baseline should list no skills and the skill arm only causal-effect. Runs that used another skill are marked invalid like peeked runs, and we report the count. B: Good, this means we don't have to touch A's installed skills.

Q2: A: Okay, I take estimate.py and its tests, starting with diff_means and regression, with the arguments you listed. B: I keep SKILL.md and methods.md, and I'll make sure the method names match the script's --method values. I also keep the q370 check. Branch per person, merged after the other has read it. Fine with this split, it feels fair now.

Q3: Accepted. If p is not below 0.05 we write "not enough evidence that the skill helps on this test set" and report wins, losses and ties. We won't add repeats or questions after seeing the result, and we'll write that rule in PLAN.md.

## Agent — shared understanding (frontier empty)

The frontier is empty. Here is what you agreed, organised by the five points of PLAN.md.

**1 · Benchmark**
- **Worked example: q317.** The agent receives `ihdp_1.csv` and the question "What is the Average treatment effect on the control? Round to the nearest hundredth." The key is 4.06. The benchmark takes the first number in the answer and accepts it if it is within 3% of the key. The agent answered 4.09, which counts as right. The plain regression it also tried gives 3.90, which would have been wrong. The choice of method decides the score.
- **Pilot:** one baseline pass over all 69 questions, one repeat, run by Friday. Label it "first run, one repeat".
- **Validity:**
  - guessing (chance level, in one sentence, for the 5 multiple-choice questions)
  - lenient scoring (first number within 3%; multiple choice only checks how the answer starts)
  - the benchmark and its sources are public, so the model may have seen the answers in training
  - doubtful keys: B checks q370 (key 0.10; a regression-discontinuity fit gives 9.75) and maybe one more, and A writes it up. You always score with the official key.

**2 · Scope**
- **Subset:** the 69 effect-estimation questions among QRData's causal questions: IHDP 30, Jobs 10, *Brave and True* 24, *Quantitative Social Science* 5.
- **Rationale:** statistics is near ceiling (9 of 10 in the pilot). Causal discovery is left out because a skill could only help there by containing the published answer graphs.
- **Runtime:** about 10 s per task, so about 12 minutes per pass.

**3 · Skill design**
- **One skill, `causal-effect`.** It gives the agent a fixed procedure instead of picking a method ad hoc:
  1. name the estimand
  2. name the design
  3. inspect the CSV
  4. pick the method from `methods.md` and run `estimate.py`; fall back to regression on all covariates if no method fits
  5. sanity-check against the naive difference in means
  6. round as asked and end with `ANSWER:`
- **Trigger:** the description "Use when a question asks for a treatment effect (ATE, ATT, ATC) or whether to control for a variable, using CSV data."
- **Structure:**
  - `SKILL.md`: the trigger and the six steps
  - `references/methods.md`: when to use each method, plus a snippet; only methods your dev questions use, with names matching the script's `--method` values
  - `scripts/estimate.py`: `--csv --treatment --outcome --method [--covariates]`; prints the estimate and the naive difference; starts with `diff_means` and `regression`

  The harness stays outside the skill.

**4 · Evaluation**
- **Comparison:** both arms use the identical command (Claude Code, Sonnet, `--setting-sources project`, `--output-format stream-json`, without `--disable-slash-commands`) and the identical prompt. The only difference: the skill arm has the skill copied into `.claude/skills/` of the task folder. Check one task per arm first: the baseline's init message should list no skills, and the skill arm's only `causal-effect`.
- **Split:** by data file, about half of each source on each side, with a fixed seed written in PLAN.md: about 34 dev and 35 test. `social.csv` goes on one side; `women.csv` and `MPs.csv` on the other. You build on dev only. Limitation: IHDP questions are near-copies across files.
- **Metrics:** for each arm on the test set:
  - accuracy, averaged over 3 repeats
  - for each question, how many of its 3 repeats were right
  - median time and cost per task (`total_cost_usd`)

  A sign test over wins and losses (`binomtest`), with the threshold p < 0.05 stated in advance. If it isn't reached, you write "not enough evidence…" and still report wins, losses and ties. You add no repeats or questions after seeing the result. Limitation: one or two questions is noise.
- **Answer isolation:** each run happens in a temporary copy of the task folder, outside the repository. You save full transcripts and search them for `causal.json`, `QRData.json` and `upstream`, and check any hit by hand. A run that peeked, or that used another skill, is marked invalid and rerun, and you report the count.

**5 · Tools and teamwork**
- **Agent and model:** Claude Code with Sonnet, the setup your harness already runs.
- **Batch execution:** runs go one after another on one laptop. You write one JSON file per run, `runs/<arm>/qNNN-rK.json`, holding the answer, seconds, cost, repeat number, whether the skill was used, and the validity flags.
- **Version control:** one private repository. `.gitignore` excludes `.venv/` and `upstream/data/`, the README explains how to unzip `data.zip`, and `runs/` is committed. Each person works on their own branch, which is merged into `main` after the other has read it.
- **Division of work:**
  - A: harness, split, runs, scoring, `estimate.py` and its tests, and the q370 write-up
  - B: `SKILL.md`, `methods.md` and the q370 check

  Before the pitch, each of you gives the other a 10-minute explanation of your part.

Does this match what you both have in mind? Please confirm, or tell me what to correct, before you write PLAN.md.
