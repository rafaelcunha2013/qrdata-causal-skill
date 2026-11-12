"""Run the agent once per task and store its answer, transcript, time and cost.

Usage: python run_agent.py <scope> <arm> [repeats] [model] [side]
  e.g. python run_agent.py effect baseline 1
       python run_agent.py effect skill 3
       python run_agent.py effect baseline 1 haiku dev
model: sonnet (default) | haiku | opus ; side: all (default) | dev | test (from key/effect_split.json)
arm: baseline (no skill) | skill (every skill in tasks/.agents/skills/ is copied into the run folder)

Each run happens in a fresh temporary copy of the task folder, outside this repository,
so the agent cannot reach the answer key. Both arms use the same command and prompt.
(The statistics and causal pilots of 11 Nov 2026 used an earlier version: run in place,
--disable-slash-commands, final reply only. Their records are in runs/statistics-baseline
and runs/causal-baseline.)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOPE, ARM = sys.argv[1], sys.argv[2]
REPEATS = int(sys.argv[3]) if len(sys.argv) > 3 else 1
MODEL = sys.argv[4] if len(sys.argv) > 4 else "sonnet"
SIDE = sys.argv[5] if len(sys.argv) > 5 else "all"
TASKS = ROOT / "tasks" if SCOPE == "arctic_flow" else ROOT / f"tasks_{SCOPE}"
RUN = ROOT / "runs" / (f"{SCOPE}-{ARM}" if MODEL == "sonnet" else f"{SCOPE}-{ARM}-{MODEL}")
SPLIT = json.loads((ROOT / "key" / f"{SCOPE}_split.json").read_text()) if SIDE != "all" else {}
RUN.mkdir(parents=True, exist_ok=True)
# The skill lives where Copilot CLI reads skills: .agents/skills/ inside the task folder.
SKILLS = TASKS / ".agents" / "skills"
# Names that only appear if the agent reaches for the answers. "upstream/" with the slash:
# the bare word is ordinary biology ("PLC acts upstream of PIP2") and flagged 27 honest runs.
ANSWER_FILES = ["causal.json", "effect.json", "statistics_full.json", "discovery.json",
                "arctic_flow.json", "QRData.json", "upstream/"]

PROMPT = (
    "Answer the question in question.md, using the data files in this folder. "
    "Python with pandas, scipy and statsmodels is available as `python`. "
    "End your reply with one final line of the form `ANSWER: <value>`."
)
COMMAND = ["claude", "-p", PROMPT, "--model", MODEL,
           "--output-format", "stream-json", "--verbose",
           "--setting-sources", "project", "--strict-mcp-config",
           "--allowedTools", "Bash,Read,Glob,Grep,Skill"]

environment = dict(os.environ)
environment["PATH"] = str(ROOT / ".venv" / "bin") + os.pathsep + environment["PATH"]

for repeat in range(1, REPEATS + 1):
    for task in sorted(TASKS.iterdir()):
        if not task.name.startswith("q"):
            continue  # .agents/ and other non-task entries
        if SIDE != "all" and SPLIT.get(task.name) != SIDE:
            continue
        workdir = Path(tempfile.mkdtemp(prefix="qrdata-")) / task.name
        shutil.copytree(task, workdir)
        if ARM == "skill":
            # Claude Code reads skills from .claude/skills/ (Copilot CLI would read .agents/skills/).
            for skill in SKILLS.iterdir():
                shutil.copytree(skill, workdir / ".claude" / "skills" / skill.name)

        start = time.time()
        result = subprocess.run(COMMAND, cwd=workdir, env=environment,
                                capture_output=True, text=True, timeout=900)
        seconds = round(time.time() - start)
        shutil.rmtree(workdir.parent)

        events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
        init = next((e for e in events if e.get("subtype") == "init"), {})
        final = next((e for e in events if e.get("type") == "result"), {})
        reply = final.get("result", "")
        skills_called = [part["input"].get("skill") for e in events if e.get("type") == "assistant"
                         for part in e["message"]["content"]
                         if part.get("type") == "tool_use" and part.get("name") == "Skill"]

        answer = ""
        for line in reply.splitlines():
            if line.strip().startswith("ANSWER:"):
                answer = line.split("ANSWER:", 1)[1].strip()

        record = {
            "task": task.name, "arm": ARM, "repeat": repeat, "answer": answer,
            "seconds": seconds, "cost_usd": final.get("total_cost_usd"),
            "skills_loaded": init.get("skills", []), "skills_called": skills_called,
            "peeked": any(name in result.stdout for name in ANSWER_FILES),
            "reply": reply,
        }
        json.dump(record, open(RUN / f"{task.name}-r{repeat}.json", "w"), indent=1)
        (RUN / f"{task.name}-r{repeat}.jsonl").write_text(result.stdout)
        print(task.name, f"r{repeat}", seconds, "s", repr(answer), "peeked" if record["peeked"] else "")
