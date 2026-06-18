#!/usr/bin/env python3
"""
genericize.py — re-apply the personal-data scrubs to freshly-regenerated bundle skills.

Each entry is an exact OLD (canonical) -> NEW (generic) replacement. Idempotent: if NEW is
already present it is skipped; if neither OLD nor NEW is found it WARNS (an anchor changed in
canonical and the scrub needs updating) rather than silently leaving personal data. It never
corrupts — a missed anchor is caught loudly here and again by build-bundle.sh's final scan.

Run:  python3 build/genericize.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # openbiohack/

SCRUBS = [
 # (relative path under skills/, OLD canonical text, NEW generic text)
 ("investigate-health/SKILL.md",
  """  Worked example: in May 2026 the working frame was Malassezia folliculitis for five
  days; the first photo, when it came, showed lacy blanching redness with no papules
  and calf involvement — none of which fit Malassezia. The frame would have changed
  inside thirty seconds if a photo had been required at the start. If no photo exists""",
  """  Worked example: a rash carried for days under one working frame on the strength of a
  written description can be overturned in thirty seconds by the first photo — when the
  shape turns out to show, say, lacy blanching redness with no papules and an unexpected
  body distribution that the frame never predicted. The picture would have changed at the
  start if a photo had been required then. If no photo exists"""),

 ("investigate-health/SKILL.md",
  """   than the one being investigated (e.g. investigating Haneen while the session's project
   memory is Teo's hard-no list), that other subject's facts leak into \"blind\" enumeration""",
  """   than the one being investigated (e.g. investigating subject B while the session's project
   memory holds subject A's hard-no list), that other subject's facts leak into \"blind\" enumeration"""),

 ("investigate-health/references/rubrics/self-report-pattern.md",
  '''### Case 1 — "Every time I eat X, Y happens within an hour" (Teo's red-meat pattern)

**Primary source.** "Every time I eat red meat in the evening, within ~3-6
hours I get worse flank itch the next morning. Observed at least 5 times
over April-May."''',
  '''### Case 1 — recurring food→symptom pattern (synthetic)

**Primary source.** "Every time I eat aged cheese in the evening, within ~3-6
hours I get facial flushing and a headache that same evening. Observed at least 5 times
over a couple of months."'''),

 ("investigate-health/references/rubrics/self-report-pattern.md",
  "Axis 2: 3 (red meat as a class — could",
  "Axis 2: 3 (aged cheese as a class — could"),

 ("research/SKILL.md",
  """When using research in content:
- Research discusses therapy. Teo does NOT practice therapy. He's an IFS-trained coach.
- Frame research as: "Here's what the evidence shows about [topic]" — separate from "Here's what I do in my coaching work"
- Never imply Greater Human provides therapy. It's a wellness app.
- See `reference/regulatory-guardrails.md` for full rules.""",
  """When using research in any public-facing content:
- Keep "here's what the evidence shows about [topic]" clearly separate from "here's what I do / what this product does." Researching a clinical topic is not a claim that you or your product treat it.
- Never imply a service or product provides medical or psychological treatment unless it lawfully does. Stay in the lane your credentials and registration support.
- If a `reference/regulatory-guardrails.md` exists for your context, follow it."""),

 ("research/SKILL.md",
  "   - Relevance to Teo's content pillars",
  "   - Relevance to your goals / the focus areas you're working in"),

 ("research/SKILL.md",
  "   - Summarize key findings in Teo's own words (never copy)",
  "   - Summarize key findings in your own words (never copy)"),
]

applied = skipped = warned = 0
for rel, old, new in SCRUBS:
    p = os.path.join(ROOT, "skills", rel)
    if not os.path.isfile(p):
        print(f"  WARN missing file: {rel}"); warned += 1; continue
    t = open(p).read()
    if new in t:
        skipped += 1; continue
    if old in t:
        open(p, "w").write(t.replace(old, new, 1)); applied += 1
        print(f"  scrubbed: {rel}")
    else:
        print(f"  WARN anchor not found (canonical changed?) in {rel}: {old[:60]!r}…"); warned += 1

print(f"genericize: {applied} applied, {skipped} already-clean, {warned} warnings")
sys.exit(1 if warned else 0)
