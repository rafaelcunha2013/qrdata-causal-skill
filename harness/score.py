"""Score one run against the answer key, the way QRData's eval.py does.

Usage: python score.py <scope> <run_name>
Numerical: the first number in the answer must lie within 3% of the key.
Multiple choice: the answer must start with the key's text (case ignored).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
key = json.load(open(ROOT / "key" / f"{sys.argv[1]}.json"))
RUN = ROOT / "runs" / f"{sys.argv[1]}-{sys.argv[2]}"


def to_number(text):
    match = re.search(r"-?\d+\.?\d*%?", text)
    if match is None:
        return None
    found = match.group()
    if found.endswith("%"):
        return float(found[:-1]) / 100
    return float(found)


def is_correct(answer, expected, question_type):
    answer, expected = answer.lower(), expected.lower()
    if question_type == "numerical":
        got, want = to_number(answer), to_number(expected)
        if got is None:
            return False
        return abs(got - want) < abs(want) * 0.03
    return answer.startswith(expected)


split_file = ROOT / "key" / f"{sys.argv[1]}_split.json"
split = json.load(open(split_file)) if split_file.exists() else {}

correct = 0
scored = 0
per_side = {}
for task, entry in sorted(key.items()):
    # Records are named <task>.json (pilots of 11 Nov) or <task>-r<repeat>.json.
    paths = sorted(RUN.glob(f"{task}-r*.json")) or [RUN / f"{task}.json"]
    paths = [path for path in paths if path.exists()]  # a dev-only run has no test records
    for path in paths:
        record = json.load(open(path))
        if record.get("peeked"):
            print(f"{path.stem}  INVALID (transcript names an answer file)")
            continue
        ok = is_correct(record["answer"], entry["answer"], entry["question_type"])
        correct += ok
        scored += 1
        side = split.get(task, "all")
        right, total = per_side.get(side, (0, 0))
        per_side[side] = (right + ok, total + 1)
        cost = record.get("cost_usd")
        cost_text = f"  ${cost:.3f}" if cost is not None else ""
        print(f"{path.stem}  {side:4}  {'right' if ok else 'WRONG'}  got {record['answer']!r}  key {entry['answer']!r}  {record['seconds']} s{cost_text}")
for side, (right, total) in sorted(per_side.items()):
    print(f"{side}: {right} of {total}")
print(f"correct: {correct} of {scored}")
