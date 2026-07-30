#!/usr/bin/env bash
# council-fence-check.sh — SP2 banner-survival lint.
# Before dispatching an investigate-offer / investigate-audit-* agent whose prompt embeds a
# worked example (s<N>.md), assert the IH-EXAMPLE-FENCE banners survived prompt assembly:
# BEGIN count == END count, and >= 1 when an example is required. A stripped/garbled fence
# means the agent could mistake the worked example for the subject's data -> refuse to dispatch.
#
# Usage:  council-fence-check.sh [--require] < assembled_prompt
#         council-fence-check.sh [--require] <file>
# exit 0 = fences intact; exit 1 = mismatch/missing (+ reason on stdout).
set -eu
REQUIRE=0
case "${1:-}" in --require) REQUIRE=1; shift ;; esac
if [ $# -ge 1 ] && [ -f "$1" ]; then TEXT="$(cat "$1")"; else TEXT="$(cat)"; fi

B=$(printf '%s' "$TEXT" | grep -c '\[\[IH-EXAMPLE-FENCE v1 BEGIN\]\]' || true)
E=$(printf '%s' "$TEXT" | grep -c '\[\[IH-EXAMPLE-FENCE v1 END\]\]' || true)

if [ "$B" != "$E" ]; then
    echo "SP2 fence-check FAIL: $B BEGIN banner(s) but $E END banner(s) — a worked-example fence was stripped or garbled during prompt assembly. Re-assemble the dispatch so every example is wrapped in a matched [[IH-EXAMPLE-FENCE v1 BEGIN]] ... [[IH-EXAMPLE-FENCE v1 END]] pair."
    exit 1
fi
if [ "$REQUIRE" = 1 ] && [ "$B" -lt 1 ]; then
    echo "SP2 fence-check FAIL: this dispatch must include at least one fenced worked example, but no [[IH-EXAMPLE-FENCE]] banner is present."
    exit 1
fi
exit 0
