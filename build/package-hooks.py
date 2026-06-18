#!/usr/bin/env python3
"""
package-hooks.py — bundle the investigate-health enforcement hooks into the OpenBioHack plugin.

Copies the hook family + libs + audit-council-completion from the canonical ~/.claude/hooks into
openbiohack/hooks/, STRIPS the machine-specific cwd-guard (public scoping is via the plugin + each
hook's own internal guards, not a hardcoded path), adds an activation hook that sets the
investigation-active marker when /investigate-health is invoked, and writes the plugin hooks/hooks.json
(paths via ${CLAUDE_PLUGIN_ROOT}). Idempotent; re-runnable. Verifies no personal path survives and that
every hook parses.

Run:  python3 build/package-hooks.py
"""
import os, re, json, shutil, subprocess, stat, sys

SRC = os.path.expanduser("~/.claude/hooks")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # openbiohack/
DEST = os.path.join(ROOT, "hooks")
LIBDEST = os.path.join(DEST, "lib")

# (registered event, matcher, script) — mirrors ~/.claude/settings.json exactly.
FAMILY = [
    ("UserPromptSubmit", "",          "investigate-health-orchestrator-context.sh"),
    ("PreToolUse",        ".*",        "investigate-health-corrections-block.sh"),
    ("PreToolUse",        "Bash",      "investigate-health-cleanup-block.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-write-check.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-label-density.sh"),
    ("PreToolUse",        "Write|Edit","investigate-health-read-attestation.sh"),
    ("PostToolUse",       "Read",      "investigate-health-read-log.sh"),
    ("SubagentStart",     None,        "investigate-health-subagent-context.sh"),
]
HELPERS = ["audit-council-completion.sh"]          # called by the orchestrator, not a hook
LIBS    = ["investigate-state.sh", "log-hook-fire.sh", "skill-token-lib.sh"]
ACTIVATE = "investigate-health-activate.sh"        # generated below (PreToolUse Skill -> marker)

GUARD_START = "# --- scope guard (investigate-health"
GUARD_END   = "# --- end scope guard ---"

def strip_cwd_guard(text):
    # Signature-based: catches both the scope-script marker form and any hand-written
    # cwd-guard (both build the __ih_cwd=$(printf ... | python3 ...) + case ... esac block).
    lines = text.splitlines(keepends=True)
    out, i = [], 0
    while i < len(lines):
        if "__ih_cwd=$(printf" in lines[i]:
            if out and "scope guard" in out[-1].lower():
                out.pop()                      # drop the preceding guard comment
            while i < len(lines) and lines[i].strip() != "esac":
                i += 1
            i += 1                              # skip the closing esac
            if i < len(lines) and "end scope guard" in lines[i].lower():
                i += 1                          # skip trailing end-marker if present
            continue
        out.append(lines[i]); i += 1
    return "".join(out)

def make_exec(p):
    os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

os.makedirs(LIBDEST, exist_ok=True)
copied, problems = [], []

def place(name, srcdir=SRC, strip=True):
    src = os.path.join(srcdir, name)
    if not os.path.isfile(src):
        problems.append(f"MISSING source: {name}"); return None
    text = open(src).read()
    if strip:
        text = strip_cwd_guard(text)
    dst = os.path.join(DEST, name)
    open(dst, "w").write(text); make_exec(dst)
    copied.append(name)
    return dst

for _ev, _m, script in FAMILY:
    place(script)
for h in HELPERS:
    place(h)
for lib in LIBS:
    src = os.path.join(SRC, "lib", lib)
    if not os.path.isfile(src):
        problems.append(f"MISSING lib: {lib}"); continue
    shutil.copy2(src, os.path.join(LIBDEST, lib)); copied.append("lib/" + lib)

# --- activation hook (replaces the marker-set that Teo's shared skill-token-issuer did) ---
activate = r'''#!/usr/bin/env bash
# investigate-health-activate.sh — PreToolUse on Skill.
# When /investigate-health is invoked, set the investigation-active marker so
# orchestrator-context injects the register reminder ONLY during a real investigation.
set -eu
INPUT=$(cat)
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh" 2>/dev/null || exit 0
SKILL=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try: print((json.load(sys.stdin).get('tool_input',{}) or {}).get('skill',''))
except Exception: print('')" 2>/dev/null || echo "")
SESSION=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try: print(json.load(sys.stdin).get('session_id','no-session'))
except Exception: print('no-session')" 2>/dev/null || echo "no-session")
[ "$SKILL" = "investigate-health" ] || exit 0
touch "$(investigate_state_dir "$SESSION")/investigation-active" 2>/dev/null || true
exit 0
'''
ap = os.path.join(DEST, ACTIVATE); open(ap, "w").write(activate); make_exec(ap); copied.append(ACTIVATE)

# --- hooks/hooks.json (plugin registration) ---
events = {}
def add(ev, matcher, script):
    grp = {"hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/" + script}]}
    if matcher is not None:
        grp["matcher"] = matcher
    events.setdefault(ev, []).append(grp)

add("PreToolUse", "Skill", ACTIVATE)        # activation first
for ev, m, script in FAMILY:
    add(ev, m, script)
hooks_json = {"hooks": events}
open(os.path.join(DEST, "hooks.json"), "w").write(json.dumps(hooks_json, indent=2) + "\n")
copied.append("hooks.json")

# --- verify ---
print("Copied:", len(copied), "items into", DEST)
leak = subprocess.run(["grep", "-rlE", "/Users/teotrevi", DEST], capture_output=True, text=True).stdout.strip()
print("Personal-path leak after strip:", leak if leak else "NONE")
synfail = []
for f in os.listdir(DEST):
    if f.endswith(".sh"):
        r = subprocess.run(["bash", "-n", os.path.join(DEST, f)], capture_output=True, text=True)
        if r.returncode != 0:
            synfail.append((f, r.stderr.strip()))
print("Syntax check:", "all pass" if not synfail else f"FAILURES: {synfail}")
print("hooks.json valid JSON:", bool(json.load(open(os.path.join(DEST, "hooks.json")))))
if problems: print("PROBLEMS:", problems)
