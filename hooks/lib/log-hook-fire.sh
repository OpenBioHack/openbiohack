#!/usr/bin/env bash
# Lightweight JSONL logger for phase3a hooks. One line per fire.
# Args: $1=hook_name $2=matched_pattern $3=tool_call_summary $4=decision
set -eu

LOG_DIR="${HOME}/.claude/logs"
mkdir -p "$LOG_DIR" 2>/dev/null || true
LOG_FILE="$LOG_DIR/hooks-phase3a-$(date +%Y-%m-%d).jsonl"

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 -c "
import json, sys
print(json.dumps({
    'ts': sys.argv[1],
    'hook': sys.argv[2],
    'matched_pattern': sys.argv[3],
    'tool_call_summary': sys.argv[4][:500],
    'decision': sys.argv[5],
}))
" "$TS" "${1:-unknown}" "${2:-}" "${3:-}" "${4:-allow}" >> "$LOG_FILE" 2>/dev/null || true
exit 0
