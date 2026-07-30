#!/usr/bin/env python3
"""investigate-extraction-register.py — Foundation-gate register-shape check for Phase-A/B
extraction outputs (extracted/*.md, extracted/compiled/*.md).

The forensic failure this closes: a PRIOR curation turned raw notes into an extract and INJECTED
diagnostic certainty as if it were the subject's record — "This is the likely root cause of the
gut dysbiosis", "confirms bile deficiency", "empirical SIBO diagnostic", "the actual problem is
insufficient bile". Extraction must reorganise, never conclude (extract-health-data: "never
interprets, concludes, or flags"). So a bare declarative CAUSAL / DIAGNOSTIC / MECHANISTIC claim
is inadmissible in an extract UNLESS the same sentence is:
  - tagged as interpretation  ([interpretation] / [prior-analysis note] / **[INFERRED]**), or
  - attributed to a named record/clinician source (records / GP / diagnosed / impression / ...), or
  - carried inside a verbatim source citation ([src: ...]) — a faithfully-quoted primary claim.
    (The [src:] escape is backed downstream by the Layer-3 verbatim-fidelity gate, which proves the
    quote actually resolves in its source, so a fabricated [src:] cannot launder an injected claim.)

Condition-agnostic: keys ONLY on register shape + the pipeline's own tags, never on any disease
name or filename. Runs on the MATCH COPY (Unicode-folded) so homoglyph evasions fold first.

stdin: extract content.  Exit 1 + first offending sentence on stdout if a violation is found.
"""
import sys, re, os
sys.path.insert(0, os.environ.get("IH_LIB", os.path.dirname(os.path.abspath(__file__))))
try:
    from investigate_canon import match_copy
except Exception:
    def match_copy(s):
        return s

text = match_copy(sys.stdin.read())
# strip fenced + inline code (structural, not claims)
text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
text = re.sub(r"`[^`]*`", "", text)

# Injected-certainty / declarative-diagnosis register shapes. Deliberately the STRONG forms that
# appeared in the forensic evidence + their close kin — not soft hedges ("consistent with",
# "may reflect", "possible"), which extraction is allowed to carry verbatim.
CERT = re.compile(
    r"\b(?:the\s+)?(?:likely\s+|actual\s+)?root cause of\b"
    r"|\bthe actual (?:problem|cause|issue|finding) is\b"
    r"|\bthe (?:real|genuine|underlying) (?:cause|problem|driver|issue) is\b"
    r"|\bconfirms?\b"
    r"|\bempirical\b[^.!?]*\bdiagnostic\b"
    r"|\bdiagnostic of\b"
    r"|\bsuggests?\b[^.!?]*\balready present\b"
    r"|\bis (?:the )?(?:most )?likely (?:cause|diagnosis|explanation)\b"
    r"|\bproves?\b"
    r"|\bthis (?:explains|confirms|means|is why)\b"
    r"|\bthe (?:reason|mechanism) (?:is|here is)\b"
    r"|\bwhich is causing\b"
    r"|\bindicates? (?:that )?(?:the|a|an)\b"
    # M5 — broaden beyond the strongest forms to common causal connectives. These carry a [src:]
    # quote in faithful extraction, so a cited line still escapes; an UNcited assertion is caught.
    r"|\bis responsible for\b"
    r"|\b(?:is|are) driven by\b"
    r"|\bstems from\b"
    r"|\bresults from\b"
    r"|\bis attributable to\b"
    r"|\bis caused by\b",
    re.I,
)

# Escapes — any one, present in the SAME sentence, admits the claim.
INTERP = re.compile(r"\[interpretation\]|\[prior-analysis note\]|\*\*\[INFERRED\]\*\*", re.I)
# H1 — the [src:] escape requires a REAL verbatim citation shape [src: F, <loc>, "quote"], not the
# bare substring '[src:'. A bare '[src: notes]' no longer launders an injected claim; and a quoted
# citation to a TEXT source is then re-verified by the src-fidelity check in the same hook (a
# fabricated quote against a binary source remains backstopped by two-pass/spot-check upstream).
SRC = re.compile(r'\[src:\s*[^,\]]+,[^,\]]*,\s*(?:"[^"]+"|“[^”]+”)\s*\]')
# M4 — attribution must BIND to a record/clinician source, not merely contain a common word like
# "notes"/"reports". Requires a clinician noun, a diagnosis verb, or a record-verb phrase.
ATTR = re.compile(
    r"\bclinician\b|\bdoctor\b|\bGP\b|\bpractitioner\b|\bconsultant\b|\bradiologist\b|\bspecialist\b"
    r"|\bdiagnos(?:ed|is|es)\b"
    r"|\bhistory of\b|\bon file\b|\bpast medical\b|\bwas told\b"
    r"|\b(?:records?|charts?|notes?|the letter|the report|the lab) (?:note|notes|noted|state|states|stated|show|shows|showed|read|reads|record|records|recorded)\b"
    r"|\b(?:noted|charted|recorded|documented|reported|listed|labell?ed) (?:by|as|with|in)\b"
    r"|\bper (?:the )?(?:lab|report|letter|clinician|records?|chart)\b"
    r"|\bimpression\s*:",
    re.I,
)


def split_sentences(t):
    return re.split(r"(?<=[.!?])\s+|\n", t)


for raw in split_sentences(text):
    s = raw.strip()
    if not s:
        continue
    # skip structural lines: table rows, separators, headings, HTML-ish
    if s.startswith("|") or s.startswith("#") or s.startswith(">"):
        continue
    if re.match(r"^[\|\s\-:]+$", s):
        continue
    # skip a leading bullet marker so "- The root cause..." is evaluated as prose
    s_body = re.sub(r"^[-*]\s+", "", s)
    if not CERT.search(s_body):
        continue
    if INTERP.search(s) or SRC.search(s) or ATTR.search(s):
        continue
    print(s_body[:240])
    sys.exit(1)

sys.exit(0)
