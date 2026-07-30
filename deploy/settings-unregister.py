#!/usr/bin/env python3
"""Un-register the lock-anchors + activate hooks from ~/.claude/settings.json.

Paired artifact of deploy/settings-register.py — removes exactly what it adds.
Apply BEFORE rolling back (deploy.sh <tag>) below the tag that introduced
lock-anchors/activate, so no settings entry dangles on a missing file.

Run it yourself:  python3 deploy/settings-unregister.py
"""
import json
import os
import shutil
import sys
import time

SETTINGS = os.environ.get("DEPLOY_SETTINGS", os.path.expanduser("~/.claude/settings.json"))

COMMANDS = {
    "~/.claude/hooks/investigate-health-lock-anchors.sh",
    "~/.claude/hooks/investigate-health-activate.sh",
}


def main() -> int:
    with open(SETTINGS) as f:
        settings = json.load(f)
    hooks = settings.get("hooks") or {}

    removed = []
    for event, groups in list(hooks.items()):
        kept_groups = []
        for g in groups or []:
            entries = g.get("hooks") or []
            kept = [h for h in entries if h.get("command") not in COMMANDS]
            removed += [h["command"] for h in entries if h.get("command") in COMMANDS]
            if kept:
                g["hooks"] = kept
                kept_groups.append(g)
            # a group whose only hooks were ours is dropped entirely
        hooks[event] = kept_groups

    if not removed:
        print("nothing to do — neither hook is registered.")
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
    for c in removed:
        print(f"un-registered: {c}")
    print("Restart or start a fresh Claude Code session to pick up the change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
