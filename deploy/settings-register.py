#!/usr/bin/env python3
"""Register the lock-anchors + activate hooks in ~/.claude/settings.json.

Paired artifact: deploy/settings-unregister.py removes exactly what this adds.
Idempotent — entries already present are left alone. Apply AFTER `deploy.sh`
has materialized the hook files (a registration pointing at a missing file is
a dangling reference; deploy.sh flags those).

Run it yourself:  python3 deploy/settings-register.py
"""
import json
import os
import shutil
import sys
import time

SETTINGS = os.environ.get("DEPLOY_SETTINGS", os.path.expanduser("~/.claude/settings.json"))

ENTRIES = [
    # (event, matcher, command) — matcher None means no matcher key.
    ("PostToolUse", "Write", "~/.claude/hooks/investigate-health-lock-anchors.sh"),
    ("PreToolUse", "Skill", "~/.claude/hooks/investigate-health-activate.sh"),
]


def main() -> int:
    with open(SETTINGS) as f:
        settings = json.load(f)
    hooks = settings.setdefault("hooks", {})

    changed = []
    for event, matcher, command in ENTRIES:
        if not os.path.isfile(os.path.expanduser(command)):
            print(f"WARNING: {command} does not exist — the hook will be INERT "
                  f"until deploy.sh materializes it. Registering anyway.")
        groups = hooks.setdefault(event, [])
        already = any(
            h.get("command") == command
            for g in groups
            for h in (g.get("hooks") or [])
        )
        if already:
            print(f"already registered: {event}[{matcher}] {command}")
            continue
        group = {"hooks": [{"type": "command", "command": command}]}
        if matcher is not None:
            group["matcher"] = matcher
        groups.append(group)
        changed.append(f"{event}[{matcher}] {command}")

    if not changed:
        print("nothing to do.")
        return 0

    backup = f"{SETTINGS}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(SETTINGS, backup)
    tmp = SETTINGS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    json.load(open(tmp))  # sanity: parseable before replacing
    os.replace(tmp, SETTINGS)
    print(f"backup: {backup}")
    for c in changed:
        print(f"registered: {c}")
    print("Restart or start a fresh Claude Code session to pick up the change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
