"""Re-apply the peek check to stored transcripts, after the check itself changed.

Usage: python recheck_peeks.py <run_name>     e.g. arctic_flow-baseline
Prints each record whose flag changes, then rewrites the record's "peeked" field.
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Read the list from run_agent.py, so both scripts always use the same names.
source = (ROOT / "harness" / "run_agent.py").read_text()
start = source.index("ANSWER_FILES = [") + len("ANSWER_FILES = ")
ANSWER_FILES = ast.literal_eval(source[start:source.index("]", start) + 1])

run = ROOT / "runs" / sys.argv[1]
changed = 0
for path in sorted(run.glob("q*-r*.json")):
    record = json.loads(path.read_text())
    transcript = path.with_suffix(".jsonl").read_text()
    peeked = any(name in transcript for name in ANSWER_FILES)
    if peeked != record["peeked"]:
        print(path.stem, record["peeked"], "->", peeked)
        record["peeked"] = peeked
        path.write_text(json.dumps(record, indent=1))
        changed += 1
flagged = sum(json.loads(p.read_text())["peeked"] for p in run.glob("q*-r*.json"))
print("changed:", changed, "| still flagged:", flagged)
