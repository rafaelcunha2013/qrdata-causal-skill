"""Check that our scorer agrees with QRData's eval.py.

Usage: python tests/test_score.py
1. Hand-made cases at the edges of the rule (3% band, percentages, multiple choice).
2. Every record of the first effect-estimation run, scored by both.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.argv = ["score.py", "effect", "baseline"]  # score.py reads these when imported
sys.path.insert(0, str(ROOT / "harness"))

import io
import contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from score import is_correct

# eval.py runs its own scoring when executed, so take only its functions.
source = (ROOT / "upstream" / "eval.py").read_text().split("data = json.load")[0]
upstream = {}
exec(source, upstream)


def upstream_correct(answer, expected, question_type):
    item = {"pred": answer, "answer": expected, "meta_data": {"question_type": question_type}}
    return upstream["calc_acc"]([item]) == 1.0


CASES = [
    ("4.12", "4.00", "numerical"),      # inside the band
    ("4.13", "4.00", "numerical"),      # just outside
    ("3.88", "4.00", "numerical"),      # 3.0% below: the band is open, so wrong
    ("-7.36", "-7.36", "numerical"),    # negative key
    ("8.53%", "8.53%", "numerical"),    # percentages on both sides
    ("0.0853", "8.53%", "numerical"),   # key in percent, answer as a fraction
    ("about 4.1 points", "4.00", "numerical"),
    ("no number", "4.00", "numerical"),
    ("Yes, it does", "yes", "multiple_choice"),
    ("B", "B", "multiple_choice"),
    ("not B", "B", "multiple_choice"),
]

disagree = []
for answer, expected, kind in CASES:
    if is_correct(answer, expected, kind) != upstream_correct(answer, expected, kind):
        disagree.append((answer, expected))

key = json.loads((ROOT / "key" / "effect.json").read_text())
records = sorted((ROOT / "runs" / "effect-baseline").glob("q*-r*.json"))
for path in records:
    record = json.loads(path.read_text())
    entry = key[record["task"]]
    ours = is_correct(record["answer"], entry["answer"], entry["question_type"])
    theirs = upstream_correct(record["answer"], entry["answer"], entry["question_type"])
    if ours != theirs:
        disagree.append((path.stem, record["answer"], entry["answer"]))

print(f"hand cases: {len(CASES)}, run records: {len(records)}, disagreements: {len(disagree)}")
for row in disagree:
    print("  ", row)
sys.exit(1 if disagree else 0)
