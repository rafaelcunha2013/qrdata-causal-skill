"""Does a standard discovery method (PC algorithm) reproduce the key? Development questions only.

Usage: python discovery_check.py
For arctic.csv and flow.csv, run PC once (causal-learn, Fisher z test, alpha 0.05) and
answer each question from the graph: no edge -> "no relationship"; X -> Y -> "X causes Y";
undirected edge -> "double sided" if offered. Compared with "always answer no relationship".
"""
import json
import re
from pathlib import Path

import pandas as pd
from causallearn.search.ConstraintBased.PC import pc

ROOT = Path(__file__).resolve().parent.parent
KEY = json.loads((ROOT / "key" / "arctic_flow.json").read_text())
SPLIT = json.loads((ROOT / "key" / "arctic_flow_split.json").read_text())

graphs = {}


def graph_for(csv):
    if csv.name not in graphs:
        data = pd.read_csv(csv)
        result = pc(data.to_numpy(), 0.05, "fisherz", show_progress=False)
        graphs[csv.name] = (list(data.columns), result.G.graph)
    return graphs[csv.name]


def relation(columns, g, x, y):
    i, j = columns.index(x), columns.index(y)
    if g[i, j] == 0 and g[j, i] == 0:
        return "none"
    if g[i, j] == -1 and g[j, i] == 1:
        return "x->y"
    if g[i, j] == 1 and g[j, i] == -1:
        return "y->x"
    return "both"


rows = []
for task in sorted(KEY):
    if SPLIT[task] != "dev":
        continue  # test answers stay closed while we build
    folder = ROOT / "tasks" / task
    csv = next(folder.glob("*.csv"))
    text = (folder / "question.md").read_text()
    options = dict(re.findall(r"^([A-D])\. (.+)$", text, re.M))
    columns, g = graph_for(csv)
    answer, none_option = None, None
    for letter, option in options.items():
        if option.startswith("No causal"):
            none_option = letter
    for letter, option in options.items():
        match = re.match(r"(\S+) causes (\S+)$", option)
        if match and match.group(1) != match.group(2):
            x, y = match.groups()
            if relation(columns, g, x, y) == "x->y":
                answer = letter
    if answer is None:
        pair = [o for o in options.values() if " causes " in o][0].split(" causes ")
        r = relation(columns, g, pair[0], pair[1]) if pair[0] in columns and pair[1] in columns else "none"
        double = [l for l, o in options.items() if "double sided" in o]
        answer = double[0] if r == "both" and double else none_option
    key = KEY[task]["answer"].upper()
    rows.append({"task": task, "file": csv.stem, "side": SPLIT[task], "pc": answer == key,
                 "always_none": none_option == key})

table = pd.DataFrame(rows)
print(table.groupby("file")[["pc", "always_none"]].agg(["sum", "count"]).to_string())
