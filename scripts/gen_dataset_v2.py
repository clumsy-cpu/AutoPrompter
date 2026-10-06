"""Build a bigger grounded Q&A set for continuous-learning-v2 (train/val/test via split_dataset.py).

Asks Opus (claude_cli) for Q&A pairs, one call per file group, and keeps a pair only if its answer
is verbatim in its source file, absent from SKILL.md, has letters, 4+ chars, max 3 words, no '='.

Usage: python3 gen_dataset_v2.py OUT_DIR [PER_GROUP]
Writes OUT_DIR/raw_<group>.txt (cached: re-runs skip groups already fetched) and OUT_DIR/grounded.json.
"""
import json
import os
import re
import sys
from collections import Counter

SKILL = os.path.expanduser("~/skills/continuous-learning-v2")
sys.path.insert(0, os.path.expanduser("~/AutoPrompter/src"))
from config_manager import ClaudeCLIConfig
from claude_cli_client import ClaudeCLIClient

GROUPS = {
    "agents": ["agents/observer.md", "agents/observer-loop.sh", "agents/session-guardian.sh",
               "agents/start-observer.sh"],
    "hooks_scripts": ["hooks/observe.sh", "scripts/detect-project.sh", "scripts/migrate-homunculus.sh",
                      "scripts/lib/homunculus-dir.sh", "config.json"],
    "cli": ["scripts/instinct-cli.py"],
}
out_dir = sys.argv[1]
per_group = int(sys.argv[2]) if len(sys.argv) > 2 else 45
os.makedirs(out_dir, exist_ok=True)

norm = lambda s: re.sub(r"\s+", " ", s.lower()).strip()
read = lambda f: open(os.path.join(SKILL, f), encoding="utf-8", errors="replace").read()
skill_md = norm(read("SKILL.md"))

PROMPT = """You are building a test set for the "continuous-learning-v2" skill. Below are some of its implementation files.

Write {n} question/answer pairs about concrete details found in these files: default values, thresholds, file and directory names, environment variables, CLI subcommands and flags, function names, hook or agent behavior, exact conditions in the code. Spread the questions across ALL files shown, and make every pair ask about a different fact.

Rules for every pair:
- "question": self-contained, one sentence, answerable only by someone who has read the implementation. Never put the answer in the question.
- "answer": a SHORT snippet (1 to 3 words, an identifier, a file name, a flag or a word) copied VERBATIM from the source file, so that a case-insensitive text search of that file finds it. It must contain letters and must not contain "=". Do not paraphrase.
- "source": the file path exactly as in the FILE header.
- Avoid facts that are likely to be in a general description of the skill, such as the idea of instincts or confidence scoring. Prefer implementation specifics.

Output ONLY a JSON array of objects with keys question, answer, source. No prose.

{bundle}
"""

client = ClaudeCLIClient(ClaudeCLIConfig(model="opus", timeout=900))
items = []
for group, files in GROUPS.items():
    cache = os.path.join(out_dir, f"raw_{group}.txt")
    if not os.path.exists(cache):
        bundle = "\n\n".join(f"=== FILE: {f} ===\n{read(f)}" for f in files)
        print(f"asking opus for {per_group} pairs on {group} ({len(bundle)} chars)", flush=True)
        resp = client.query(PROMPT.format(n=per_group, bundle=bundle),
                            system_message="You write precise test sets. Output only JSON.")
        if not resp.success:
            sys.exit(f"opus failed on {group}: {resp.error}")
        open(cache, "w").write(resp.content)
    raw = open(cache).read()
    got = json.loads(raw[raw.index("["): raw.rindex("]") + 1])
    print(f"{group}: {len(got)} pairs")
    items += [dict(it, group=group) for it in got]

texts = {f: read(f) for fs in GROUPS.values() for f in fs}
kept, seen_a, seen_q, drops = [], set(), set(), Counter()
for it in items:
    q, a, src = it.get("question", "").strip(), it.get("answer", "").strip(), it.get("source", "")
    if src not in texts or not q or not a:
        reason = "bad fields/source"
    elif len(a.split()) > 3 or len(norm(a)) < 4 or not re.search("[a-z]", norm(a)) or "=" in a:
        reason = "weak label"
    elif norm(a) not in norm(texts[src]):
        reason = "not verbatim in source"
    elif norm(a) in skill_md:
        reason = "in SKILL.md"
    elif norm(a) in norm(q):
        reason = "answer in question"
    elif norm(a) in seen_a or norm(q) in seen_q:
        reason = "duplicate"
    else:
        reason = None
    if reason:
        drops[reason] += 1
        continue
    seen_a.add(norm(a))
    seen_q.add(norm(q))
    kept.append({"input": q, "expected_output": a, "metadata": {"source": src}})

json.dump(kept, open(os.path.join(out_dir, "grounded.json"), "w"), indent=2)
print(f"kept {len(kept)} of {len(items)}; dropped {dict(drops)}")
print("sources:", dict(Counter(e["metadata"]["source"] for e in kept)))
