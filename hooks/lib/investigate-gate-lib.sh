#!/usr/bin/env bash
# investigate-gate-lib.sh — L1 single rule-source loader.
#
# A per-file JSON manifest (references/gates/<file>.rules.json) declares WHICH named checks
# apply to a gated artifact. The proven regex/python implementations stay in write-check and
# are switched on/off + parameterised by the manifest, so one source drives hook + writer
# digest + auditor template without rewriting battle-tested regex.
#
# Backward-compatible + fail-closed:
#   - No manifest for a basename  -> gate_rules_path echoes empty -> caller runs the hardcoded
#     check (no regression).
#   - Manifest present but unreadable/corrupt -> gate_enabled returns 0 (ENABLED) so a broken
#     manifest can never silently DISABLE enforcement.
#   - A check not declared in a present manifest -> treated as ENABLED (fail-closed).

IH_GATE_SKILL_DIR="${IH_GATE_SKILL_DIR:-$HOME/.claude/skills/investigate-health}"

gate_rules_path() {            # gate_rules_path <basename> -> path or empty
    local base="$1" f
    case "$base" in
        constraints-*|shape-profile-*|mechanism-map-*|convergence-*) f=phaseB ;;
        working-hypothesis.md|step5-cross-check.md|hypothesis-set.md|step6-prioritize.md) f=synthesis ;;
        *) f="${base%.md}" ;;
    esac
    local p="$IH_GATE_SKILL_DIR/references/gates/$f.rules.json"
    [ -f "$p" ] && printf '%s' "$p"
}

gate_enabled() {               # gate_enabled <rules.json> <check> ; exit 0 if enabled
    python3 - "$1" "$2" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)                      # fail-closed: unreadable manifest => run the check
chk = d.get("checks", {})
node = chk.get(sys.argv[2])
if node is None:
    sys.exit(0)                      # check not declared => fail-closed (enabled)
sys.exit(0 if node.get("enabled") else 1)
PY
}

gate_param() {                 # gate_param <rules.json> <check> <key> -> stdout (empty on miss)
    python3 - "$1" "$2" "$3" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
v = d.get("checks", {}).get(sys.argv[2], {}).get(sys.argv[3], "")
if isinstance(v, (list, dict)):
    import json as _j; sys.stdout.write(_j.dumps(v))
else:
    sys.stdout.write("" if v is None else str(v))
PY
}
