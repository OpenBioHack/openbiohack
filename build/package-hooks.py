#!/usr/bin/env python3
"""
package-hooks.py — verify the canonical investigate-health hooks and (re)generate hooks.json.

Since the git-native restructure (2026-07-07), openbiohack/hooks/ IS the canonical source of
truth: the hooks are edited here, the private install is materialized FROM here by deploy.sh,
and the public plugin ships this directory as-is. This script therefore no longer copies
anything from ~/.claude/hooks — it verifies the canonical tree (no personal path, no
machine-specific cwd-guard, every hook parses, every registered file exists) and regenerates
the plugin hooks/hooks.json (paths via ${CLAUDE_PLUGIN_ROOT}). Idempotent; re-runnable.

Run:  python3 build/package-hooks.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # openbiohack/
DEST = os.path.join(ROOT, "hooks")

# (registered event, matcher, script) — mirrors the private ~/.claude/settings.json set.
FAMILY = [
    ("PreToolUse",        "Skill",     "investigate-health-activate.sh"),
    ("UserPromptSubmit",  "",          "investigate-health-orchestrator-context.sh"),
    ("PreToolUse",        ".*",        "investigate-health-corrections-block.sh"),
    ("PreToolUse",        "Bash",      "investigate-health-cleanup-block.sh"),
    ("PreToolUse",        "Bash|Edit|Write", "investigate-health-faithful-strip.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-write-check.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-label-density.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-read-attestation.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-extraction-check.sh"),
    ("PostToolUse",       "Read",      "investigate-health-read-log.sh"),
    ("PostToolUse",       "Write",     "investigate-health-lock-anchors.sh"),
    ("SubagentStart",     None,        "investigate-health-subagent-context.sh"),
]
HELPERS = [  # invoked by the orchestrator / the skill, not registered as hooks
    "audit-council-completion.sh",
    "council-fence-check.sh",
    "council-finding.sh",
    "council-offer-complete.sh",
    "council-readproof.sh",
]

problems: list[str] = []

# --- verify every referenced file exists ------------------------------------
for _ev, _m, script in FAMILY:
    if not os.path.isfile(os.path.join(DEST, script)):
        problems.append(f"MISSING registered hook: {script}")
for h in HELPERS:
    if not os.path.isfile(os.path.join(DEST, h)):
        problems.append(f"MISSING helper: {h}")
if not os.path.isdir(os.path.join(DEST, "lib")):
    problems.append("MISSING hooks/lib/")

# --- hooks/hooks.json (plugin registration) ---------------------------------
events: dict[str, list[dict[str, object]]] = {}
def add(ev: str, matcher: str | None, script: str) -> None:
    grp: dict[str, object] = {
        "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/" + script}]
    }
    if matcher is not None:
        grp["matcher"] = matcher
    events.setdefault(ev, []).append(grp)

for ev, m, script in FAMILY:
    add(ev, m, script)
hooks_json = {"hooks": events}
with open(os.path.join(DEST, "hooks.json"), "w") as f:
    f.write(json.dumps(hooks_json, indent=2) + "\n")

# --- verify the canonical tree ----------------------------------------------
# Scan only git-shippable source files. __pycache__/*.pyc are build artifacts:
# gitignored, never committed, and never deployed (deploy.sh and the public
# plugin both ship via `git archive`, which includes only tracked files). A
# .pyc embeds its source's absolute path in co_filename, so scanning it yields
# a false "personal path" leak for a file that never leaves this machine.
def scan_files() -> list[str]:
    found = []
    for root, dirs, files in os.walk(DEST):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            if name.endswith(".pyc"):
                continue
            found.append(os.path.join(root, name))
    return found

def grep_files(pattern: str, files: list[str]) -> str:
    if not files:
        return ""
    return subprocess.run(
        ["grep", "-lE", pattern, *files], capture_output=True, text=True
    ).stdout.strip()

shippable = scan_files()
leak = grep_files("/Users/[username]", shippable)
print("Personal-path leak:", leak if leak else "NONE")
guard = grep_files(r"__ih_cwd=\$\(printf", shippable)
print("Hardcoded cwd-guard signature:", guard if guard else "NONE")
if leak:
    problems.append(f"personal path present: {leak}")
if guard:
    problems.append(f"cwd-guard present: {guard}")

synfail = []
for f in sorted(os.listdir(DEST)):
    if f.endswith(".sh"):
        r = subprocess.run(["bash", "-n", os.path.join(DEST, f)], capture_output=True, text=True)
        if r.returncode != 0:
            synfail.append((f, r.stderr.strip()))
for f in sorted(os.listdir(os.path.join(DEST, "lib"))):
    p = os.path.join(DEST, "lib", f)
    if f.endswith(".sh"):
        r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
        if r.returncode != 0:
            synfail.append((f"lib/{f}", r.stderr.strip()))
    elif f.endswith(".py"):
        r = subprocess.run([sys.executable, "-m", "py_compile", p], capture_output=True, text=True)
        if r.returncode != 0:
            synfail.append((f"lib/{f}", r.stderr.strip()))
print("Syntax check:", "all pass" if not synfail else f"FAILURES: {synfail}")
if synfail:
    problems.append(f"syntax failures: {[n for n, _ in synfail]}")

print("hooks.json valid JSON:", bool(json.load(open(os.path.join(DEST, "hooks.json")))))
if problems:
    print("PROBLEMS:", problems)
    sys.exit(1)
print("OK: canonical hooks verified; hooks.json regenerated.")
