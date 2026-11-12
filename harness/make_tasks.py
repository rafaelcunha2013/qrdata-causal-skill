"""Build a task folder (what the agent sees) and its answer key (what it never sees).

Usage: python make_tasks.py <scope>
  statistics:      pilot, 10 of the questions WITHOUT the keyword "Causality"
  causal:          pilot, 10 of the questions WITH the keyword "Causality"
  effect:          all 69 causal questions that are NOT causal discovery
  statistics_full: all 142 questions without "Causality"
  discovery:       all 200 causal-discovery questions (full graph 150, pairwise 50)
  arctic_flow:     the 100 discovery questions on real data: arctic.csv (sea ice) and flow.csv (proteins)
Full scopes also write key/<scope>_split.json: each data file goes to dev or test,
per source, seed 2026, so no data file is on both sides. arctic_flow has one file per
source, so it splits by QUESTION within each file instead (half dev, half test).
"""
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = ROOT / "upstream"
SCOPE = sys.argv[1]
# The chosen scope lives in tasks/ (the task folder of PHASE 2); pilots keep tasks_<scope>/.
TASKS = ROOT / "tasks" if SCOPE == "arctic_flow" else ROOT / f"tasks_{SCOPE}"
KEY = ROOT / "key" / f"{SCOPE}.json"
PILOT_SIZE = {  # (numerical, multiple choice), roughly the scope's own mix
    "statistics": (7, 3),
    "causal": (3, 7),
}

questions = json.load(open(UPSTREAM / "QRData.json"))
for number, question in enumerate(questions):
    question["id"] = f"q{number:03d}"

DISCOVERY = {"Full graph causal discovery", "Pairwise causal discovery"}
FULL = {"effect", "statistics_full", "discovery", "arctic_flow"}
if SCOPE == "effect":
    in_scope = [q for q in questions if "Causality" in q["meta_data"]["keywords"]
                and not DISCOVERY & set(q["meta_data"]["keywords"])]
elif SCOPE == "discovery":
    in_scope = [q for q in questions if DISCOVERY & set(q["meta_data"]["keywords"])]
elif SCOPE == "arctic_flow":
    in_scope = [q for q in questions if DISCOVERY & set(q["meta_data"]["keywords"])
                and q["data_files"][0] in ("arctic.csv", "flow.csv")]
elif SCOPE == "statistics_full":
    in_scope = [q for q in questions if "Causality" not in q["meta_data"]["keywords"]]
else:
    causal = SCOPE == "causal"
    in_scope = [q for q in questions if ("Causality" in q["meta_data"]["keywords"]) == causal]
numerical = [q for q in in_scope if q["meta_data"]["question_type"] == "numerical"]
multiple_choice = [q for q in in_scope if q["meta_data"]["question_type"] == "multiple_choice"]

rng = random.Random(0)
if SCOPE in FULL:
    pilot = in_scope
else:
    how_many_numerical, how_many_choice = PILOT_SIZE[SCOPE]
    pilot = rng.sample(numerical, how_many_numerical) + rng.sample(multiple_choice, how_many_choice)

key = {}
for question in pilot:
    folder = TASKS / question["id"]
    folder.mkdir(parents=True, exist_ok=True)
    text = question["data_description"] + "\n\n" + question["question"] + "\n"
    if question["meta_data"].get("multiple_choices"):
        text += "\nOptions:\n" + "\n".join(question["meta_data"]["multiple_choices"]) + "\n"
    (folder / "question.md").write_text(text)
    for name in question["data_files"]:
        shutil.copy(UPSTREAM / "data" / "data" / name, folder / name)
    key[question["id"]] = {
        "answer": question["answer"],
        "question_type": question["meta_data"]["question_type"],
    }

KEY.parent.mkdir(exist_ok=True)
json.dump(key, open(KEY, "w"), indent=1)

if SCOPE in FULL:
    # Split by DATA FILE, per source, so no file is on both sides. Seed 2026.
    split_rng = random.Random(2026)
    sources = {}
    for question in pilot:
        source = question["meta_data"]["reference"].split(" dataset")[0][:25]
        sources.setdefault(source, set()).add(tuple(question["data_files"]))
    side = {}
    if SCOPE == "arctic_flow":
        split = {}
        for name in ("arctic.csv", "flow.csv"):
            ids = sorted(q["id"] for q in pilot if q["data_files"][0] == name)
            split_rng.shuffle(ids)
            for position, task in enumerate(ids):
                split[task] = "dev" if position < len(ids) / 2 else "test"
        sources = {}
    for source in sorted(sources):
        files = sorted(sources[source])
        split_rng.shuffle(files)
        for position, files_of_task in enumerate(files):
            side[files_of_task] = "dev" if position < len(files) / 2 else "test"
    if SCOPE != "arctic_flow":
        split = {q["id"]: side[tuple(q["data_files"])] for q in pilot}
    json.dump(split, open(ROOT / "key" / f"{SCOPE}_split.json", "w"), indent=1)
    print("dev", list(split.values()).count("dev"), "test", list(split.values()).count("test"))
print(f"{len(pilot)} tasks written to {TASKS}; key in {KEY}")
