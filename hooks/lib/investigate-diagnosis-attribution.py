#!/usr/bin/env python3
# Deny if "diagnosis"/"diagnoses" appears in a sentence WITHOUT a practitioner-attribution marker.
# The tool speaks in processes/possibilities; "diagnosis" is allowed only when reporting what a
# practitioner recorded. Runs on OUTPUT artifacts only (never source extracts).
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from investigate_canon import match_copy
except Exception:
    def match_copy(s):
        return s
text = match_copy(sys.stdin.read())
text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
text = re.sub(r"`[^`]*`", "", text)
text = re.split(r"(?im)^##\s+labels referenced.*?$", text)[0]
diag = re.compile(r"\bdiagnos(is|es)\b", re.I)
# Attribution markers must denote a RECORD/clinician source, not just any temporal co-occurrence.
# L1 fix: dropped the bare temporal adverbs 'prior'/'previous' (they let tool-voice sentences
# like "the prior probability of this diagnosis is low" pass). 'previously diagnosed' is still
# covered by 'diagnosed'; recorded prior dxes by 'records'/'history of'/'on file'/'past medical'.
attr = re.compile(r"(records?|noted|charted?|clinician|doctor|\bGP\b|practitioner|diagnosed|"
                  r"history of|listed (as|with)|labell?ed (as|with)|on file|was told|past medical)", re.I)
for sent in re.split(r"(?<=[.!?])\s+|\n", text):
    if diag.search(sent) and not attr.search(sent):
        print(sent.strip()[:200]); sys.exit(1)
sys.exit(0)
