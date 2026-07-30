#!/usr/bin/env python3
"""rank-questions.py — deterministic discrimination-ranker for the interview question bank.

The bank holds ~100 questions; a person can answer ~10-15 well in one sitting. This picks WHICH ones,
by how much each answer would SPLIT the live candidate set — not by its label. A question tagged
"high specificity" is worth nothing if every live candidate predicts the same answer; a question that
separates a genuinely TIED pair is worth far more than one separating candidates already far apart.

Score components (all read off the bank's own metadata — no new judgement invented here):
  fork          the research agent already judged the predictions genuinely diverge (FORK in the
                expected-answer field). That flag IS the "are these answers different" call.
  reach         how many LIVE candidates the expected-answer field names (a question bearing on six
                beats one bearing on one).
  tied-pair     names BOTH members of a currently-unseparated pair -> the ambiguity actually at stake.
  specificity   how well a positive answer separates THIS candidate from the others.
  sensitivity   how strongly a positive answer confirms.
  consequence   bears on a high-consequence candidate (being wrong there is costly), per the same
                consequence-weighting that keeps a safety must-exclude live at a low band.
  disposition   `partial` gets a small boost (the record already gives half the answer, so a short
                confirmation closes it); `answered` rows are excluded entirely.

Person-answerable and needs-a-test questions are ranked into SEPARATE lists — an interview list and a
"tests worth buying" list. Mixing them is a category error (one is free and immediate, the other costs
money and time). NOTE: the bank currently drops step-4c's person/test tag, so when no tag is present
this falls back to a TEXT HEURISTIC and marks the row `tag: inferred` — the real repair is to preserve
the tag through the Phase-0 harvest.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

_POOL_RE = re.compile(r"^##\s+Question pool\s+[—–-]\s+(H\d+)\b(.*)$", re.MULTILINE)
_HID_RE = re.compile(r"\bH(\d+)\b")
_FORK_RE = re.compile(r"\bFORK\b", re.IGNORECASE)
# a question row: | H33-Q1 | text | expected | sensitivity | specificity | disposition | src |
_ROW_RE = re.compile(r"^\|\s*(H\d+-Q\d+)\s*\|(.+)$")

# needs-a-test signals: the answer comes from an assay/procedure, not from the person's experience.
_TEST_RE = re.compile(
    r"\b(measured|assay|test(s|ed|ing)?\b|biopsy|aspirate|endoscop|colonoscop|manometry|culture|"
    r"serolog|panel\b|level(s)?\b|titre|screen(ed|ing)?\b|imaging|scan\b|pcr\b|qpcr\b|sequenc|"
    r"subtyp|profile\b|on file\b|5-hiaa|chromogranin|metanephrine|calcitonin|tryptase|elastase|"
    r"calprotectin|breath\b|stool sample|study\b|manometr)\b",
    re.IGNORECASE)
# answerable-by-person signals: lived experience, timing, what they noticed.
_PERSON_RE = re.compile(
    r"\b(do you|did you|does it|do the|have you|how long|when did|does the|is the|are the|"
    r"notice|feel|wake|taste|smell|worse|better|ever occur)\b", re.IGNORECASE)

_LEVELS = (
    (re.compile(r"^\s*(very high|high)\b", re.IGNORECASE), "high"),
    (re.compile(r"^\s*moderate\s*[—–-]\s*high|^\s*moderate\s*to\s*high", re.IGNORECASE), "moderate-high"),
    (re.compile(r"^\s*moderate\b", re.IGNORECASE), "moderate"),
    (re.compile(r"^\s*low\s*[—–-]\s*moderate|^\s*low\s*to\s*moderate", re.IGNORECASE), "low-moderate"),
    (re.compile(r"^\s*low\b", re.IGNORECASE), "low"),
)
_SPEC_W = {"high": 2.0, "moderate-high": 1.5, "moderate": 1.0, "low-moderate": 0.5, "low": 0.25, "": 0.5}
_SENS_W = {"high": 1.5, "moderate-high": 1.1, "moderate": 0.75, "low-moderate": 0.4, "low": 0.25, "": 0.4}

W_FORK = 3.0
W_REACH = 1.0
REACH_CAP = 4
W_TIED = 4.0
W_CONSEQUENCE = 2.0
W_PARTIAL = 0.5


class RankError(Exception):
    pass


def level_of(text: str) -> str:
    for rx, name in _LEVELS:
        if rx.search(text or ""):
            return name
    return ""


def cells(row_body: str) -> list[str]:
    parts = [c.strip() for c in row_body.split("|")]
    while parts and parts[-1] == "":
        parts.pop()
    return parts


def classify_tag(text: str, expected: str) -> tuple[str, bool]:
    """(tag, inferred). The bank drops step-4c's tag, so fall back to a text heuristic."""
    blob = f"{text} {expected}"
    m = re.search(r"answerable-by-person|needs-a-test", blob, re.IGNORECASE)
    if m:
        return ("person" if m.group(0).lower().startswith("answerable") else "test"), False
    if _TEST_RE.search(text):
        return "test", True
    if _PERSON_RE.search(text):
        return "person", True
    return "person", True


def parse_bank(text: str) -> list[dict]:
    """Rows from every `## Question pool — Hn` section. Rows outside a pool (the pass-log tables, whose
    first column is also a q-id) are ignored: only pool sections are scanned."""
    pools = list(_POOL_RE.finditer(text))
    if not pools:
        raise RankError("no `## Question pool — Hn` sections found in the question bank")
    out: list[dict] = []
    for i, m in enumerate(pools):
        owner = m.group(1)
        start = m.end()
        end = pools[i + 1].start() if i + 1 < len(pools) else len(text)
        for line in text[start:end].splitlines():
            rm = _ROW_RE.match(line)
            if not rm:
                continue
            c = cells(rm.group(2))
            if len(c) < 5:
                continue
            qtext, expected = c[0], c[1]
            sens, spec, disp = c[2], c[3], (c[4] if len(c) > 4 else "")
            out.append({
                "qid": rm.group(1), "owner": owner, "text": qtext, "expected": expected,
                "sensitivity": level_of(sens), "specificity": level_of(spec),
                "disposition": disp.split("(")[0].strip().lower(),
            })
    return out


def score_row(r: dict, live: set[str], tied: list[tuple[str, str]], high_consequence: set[str]) -> dict:
    named = {f"H{n}" for n in _HID_RE.findall(r["expected"])}
    named.add(r["owner"])
    named_live = named & live if live else named
    fork = bool(_FORK_RE.search(r["expected"]))
    reach = min(len(named_live), REACH_CAP)
    tied_hits = [p for p in tied if p[0] in named and p[1] in named]
    conseq = bool(named_live & high_consequence)
    s = 0.0
    s += W_FORK if fork else 0.0
    s += W_REACH * reach
    s += W_TIED * len(tied_hits)
    s += _SPEC_W.get(r["specificity"], 0.5)
    s += _SENS_W.get(r["sensitivity"], 0.4)
    s += W_CONSEQUENCE if conseq else 0.0
    s += W_PARTIAL if r["disposition"].startswith("partial") else 0.0
    tag, inferred = classify_tag(r["text"], r["expected"])
    why = []
    if fork:
        why.append("FORK")
    if tied_hits:
        why.append("splits tied " + "+".join("↔".join(p) for p in tied_hits))
    why.append(f"reach {len(named_live)}")
    if conseq:
        why.append("high-consequence")
    if r["specificity"]:
        why.append(f"spec {r['specificity']}")
    return {**r, "score": round(s, 2), "named": sorted(named_live), "fork": fork,
            "tied": ["↔".join(p) for p in tied_hits], "tag": tag, "tag_inferred": inferred,
            "why": ", ".join(why)}


def build(text: str, live: set[str], tied: list[tuple[str, str]], high_consequence: set[str],
          top: int) -> tuple[str, dict]:
    rows = parse_bank(text)
    askable = [r for r in rows if not r["disposition"].startswith("answered")]
    scored = [score_row(r, live, tied, high_consequence) for r in askable]
    # deterministic: score DESC, then fork first, then reach, then q-id
    scored.sort(key=lambda r: (-r["score"], not r["fork"], -len(r["named"]), r["qid"]))
    person = [r for r in scored if r["tag"] == "person"]
    tests = [r for r in scored if r["tag"] == "test"]
    top_person, top_tests = person[:top], tests[:top]

    out = [
        "# Interview shortlist — ranked by discriminating value",
        "",
        f"> Scored {len(scored)} askable questions (of {len(rows)} pooled; "
        f"{len(rows) - len(scored)} already answered by the records). Ranked by how much each answer "
        "would SPLIT the live candidate set: fork-flagged predictions, how many live candidates the "
        "question bears on, whether it separates a currently-tied pair, its specificity/sensitivity, and "
        "a boost where a high-consequence candidate is at stake. Person-answerable and needs-a-test are "
        "ranked separately — one is free and immediate, the other costs money and time.",
        "",
        f"Live candidates: {', '.join(sorted(live, key=lambda x: int(x[1:]))) if live else '(all)'}"
        + (f" · tied pairs targeted: {', '.join('↔'.join(p) for p in tied)}" if tied else "")
        + (f" · high-consequence: {', '.join(sorted(high_consequence))}" if high_consequence else ""),
        "",
        f"## Ask the person (top {len(top_person)})",
        "",
    ]
    for i, r in enumerate(top_person, 1):
        out.append(f"{i}. **[{r['qid']}, score {r['score']}]** {r['text']}")
        out.append(f"   - _{r['why']}_" + ("  ·  tag inferred" if r["tag_inferred"] else ""))
        out.append(f"   - bears on: {', '.join(r['named'])}")
        out.append("")
    out.append(f"## Tests worth buying (top {len(top_tests)}) — not interview questions")
    out.append("")
    for i, r in enumerate(top_tests, 1):
        out.append(f"{i}. **[{r['qid']}, score {r['score']}]** {r['text']}")
        out.append(f"   - _{r['why']}_" + ("  ·  tag inferred" if r["tag_inferred"] else ""))
        out.append("")
    text_out = "\n".join(out).rstrip("\n") + "\n"
    meta = {
        "ranSuccessfully": True, "nPooled": len(rows), "nAskable": len(scored),
        "nPerson": len(person), "nTest": len(tests),
        "topPerson": [{"qid": r["qid"], "score": r["score"], "why": r["why"], "bearsOn": r["named"]}
                      for r in top_person],
        "topTests": [{"qid": r["qid"], "score": r["score"], "why": r["why"]} for r in top_tests],
    }
    return text_out, meta


def atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Rank interview questions by discriminating value.")
    ap.add_argument("--bank", required=True, help="question-bank.md")
    ap.add_argument("--live", default="", help="comma-separated live candidate ids (default: all named)")
    ap.add_argument("--tied", action="append", default=[], help="a tied pair, e.g. H11:H26 (repeatable)")
    ap.add_argument("--high-consequence", default="", help="comma-separated high-consequence ids")
    ap.add_argument("--top", type=int, default=15, help="how many per list (default 15)")
    ap.add_argument("--out", help="write the shortlist here")
    ap.add_argument("--json", action="store_true", help="print the summary JSON")
    args = ap.parse_args()
    try:
        with open(args.bank, encoding="utf-8") as fh:
            text = fh.read()
        live = {x.strip().upper() for x in args.live.split(",") if x.strip()}
        hc = {x.strip().upper() for x in args.high_consequence.split(",") if x.strip()}
        tied: list[tuple[str, str]] = []
        for t in args.tied:
            parts = [p.strip().upper() for p in re.split(r"[:,x↔]", t) if p.strip()]
            if len(parts) != 2:
                raise RankError(f"--tied expects two ids like H11:H26, got {t!r}")
            tied.append((parts[0], parts[1]))
        out_text, meta = build(text, live, tied, hc, args.top)
        if args.out:
            atomic_write(args.out, out_text)
        if args.json:
            print(json.dumps(meta))
        return 0
    except (RankError, OSError, ValueError) as e:
        if args.json:
            print(json.dumps({"ranSuccessfully": False, "note": str(e)}))
        else:
            print(f"rank-questions: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
