#!/usr/bin/env python3
"""image_reconcile.py — deterministic grounding for the IMAGE extraction path.

A vision read of a lab screenshot has no verbatim source to ground against (unlike the vector-PDF
path, where cite_verify grounds every quote as a substring of the converted text). So the image
path runs TWO independent vision passes over the same image and grounds by AGREEMENT: a per-analyte
row is trusted only when both passes independently produce the same value+unit+flag. Any
disagreement — a differing field, or a row one pass has and the other misses — is FLAGGED for human
sign-off. No single vision read is authoritative.

Each pass is a list of dicts: {"analyte","value","unit","flag"}. Rows match by normalised analyte
name. Comparison is normalised (whitespace/case/edge-punct), and a unit compares equal when either
side is blank (unit-less ratios). Output: {"agreed":[row...], "flagged":[{analyte,reason,a,b}...]}.
"""
from __future__ import annotations

import argparse
import json
import re
import sys


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def norm_val(s: str) -> str:
    # keep digits, dot, and a leading comparator (< > =) — a censored value like "<0.5" must not
    # compare equal to "0.5".
    s = (s or "").strip()
    lead = s[0] if s[:1] in "<>=" else ""
    return lead + re.sub(r"[^0-9.]", "", s)


def norm_unit(s: str) -> str:
    return re.sub(r"[^a-z/]", "", (s or "").lower())


def norm_flag(s: str) -> str:
    return re.sub(r"[^a-z]", "", (s or "").lower())


def _units_agree(a: str, b: str) -> bool:
    na, nb = norm_unit(a), norm_unit(b)
    return na == nb or not na or not nb


def reconcile(pass_a: list[dict], pass_b: list[dict]) -> dict:
    """Compare two independent vision passes. Returns {"agreed": [...], "flagged": [...]}."""
    amap = {norm_name(r.get("analyte", "")): r for r in pass_a}
    bmap = {norm_name(r.get("analyte", "")): r for r in pass_b}
    agreed: list[dict] = []
    flagged: list[dict] = []
    for key in sorted(set(amap) | set(bmap)):
        a, b = amap.get(key), bmap.get(key)
        if a is None or b is None:
            present, missing = (a, "B") if b is None else (b, "A")
            flagged.append({"analyte": present.get("analyte", ""),
                            "reason": f"missing-in-pass-{missing}", "a": a, "b": b})
            continue
        diffs = []
        if norm_val(a.get("value", "")) != norm_val(b.get("value", "")):
            diffs.append("value")
        if not _units_agree(a.get("unit", ""), b.get("unit", "")):
            diffs.append("unit")
        if norm_flag(a.get("flag", "")) != norm_flag(b.get("flag", "")):
            diffs.append("flag")
        if diffs:
            flagged.append({"analyte": a.get("analyte", ""),
                            "reason": "disagree:" + ",".join(diffs), "a": a, "b": b})
        else:
            agreed.append({**a, "provenance": "dual-vision-agree"})
    return {"agreed": agreed, "flagged": flagged}


# ───────────────────────── materialise (the grounding artifact) ─────────────────────────
# The dual-vision-agreed rows are serialised into the image source's OWN `converted` text file, and the
# `[src:]`-cited `.md` extract cites verbatim slices of it. cite_verify then grounds the image extract
# against that text exactly as it grounds a geom/text source — ONE grounding contract, no per-kind
# branch. Disagreements never enter the text/extract; they go to review.json (signedOff:false) and gate
# the accuracy verdict until a human signs off. No LLM constructs the grounding artifact — this is
# deterministic, so a bad vision read cannot smuggle a value in by re-wording it.


def _row_text(r: dict) -> str:
    """One agreed row → its grounding-text line: `analyte | value unit | flag` (blank fields dropped)."""
    vu = " ".join(x for x in [str(r.get("value", "")).strip(), str(r.get("unit", "")).strip()] if x)
    cells = [str(r.get("analyte", "")).strip(), vu, str(r.get("flag", "")).strip()]
    return " | ".join(c for c in cells if c)


def _cite_quote(line: str) -> str:
    """Wrap a text line so cite_verify's CITE_RE parses it without truncating on an internal quote:
    straight delims when the line has no straight quote, else curly (lab values almost never contain
    either; the pathological both-quotes case degrades to straight->single so txt/quote stay consistent)."""
    if '"' not in line:
        return f'"{line}"'
    if "”" not in line:
        return f"“{line}”"
    return f'"{line.replace(chr(34), chr(39))}"'


def materialise(rep: dict, name: str) -> tuple[str, str, dict]:
    """Return (converted_txt, extract_md, review_obj) from a reconcile result. Each `.md` data line's
    quote is the verbatim `.txt` line, so grounding is 0/0 by construction."""
    txt_lines, md_lines = [], []
    for i, r in enumerate(rep["agreed"]):
        line = _row_text(r)
        if not line:
            continue
        txt_lines.append(line)
        vu = " ".join(x for x in [str(r.get("value", "")).strip(),
                                  str(r.get("unit", "")).strip()] if x)
        datum = " ".join(x for x in [str(r.get("analyte", "")).strip(), vu,
                                     str(r.get("flag", "")).strip()] if x)
        md_lines.append(f"- {datum} [src: {name}, dual-vision r{i}, {_cite_quote(line)}]")
    review = {"source": name,
              "entries": [{**f, "signedOff": False} for f in rep["flagged"]]}
    return "\n".join(txt_lines) + "\n", "\n".join(md_lines) + "\n", review


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pass_a", help="JSON array — first vision pass")
    ap.add_argument("pass_b", help="JSON array — second vision pass")
    ap.add_argument("--json", action="store_true", help="emit the full reconcile object as JSON")
    ap.add_argument("--name", help="source name for the [src:] locators (required to --emit-*)")
    ap.add_argument("--emit-txt", help="write the dual-vision-agreed grounding text here")
    ap.add_argument("--emit-md", help="write the [src:]-cited extract here")
    ap.add_argument("--emit-review", help="write the disagreement review.json here")
    args = ap.parse_args()
    a = json.load(open(args.pass_a))
    b = json.load(open(args.pass_b))
    rep = reconcile(a, b)
    if args.emit_txt or args.emit_md or args.emit_review:
        if not args.name:
            raise SystemExit("--name is required to --emit-*")
        txt, md, review = materialise(rep, args.name)
        if args.emit_txt:
            open(args.emit_txt, "w", encoding="utf-8").write(txt)
        if args.emit_md:
            open(args.emit_md, "w", encoding="utf-8").write(md)
        if args.emit_review:
            open(args.emit_review, "w", encoding="utf-8").write(json.dumps(review, indent=1))
    if args.json:
        print(json.dumps({"agreed": len(rep["agreed"]), "flagged": len(rep["flagged"]),
                          "reconcile": rep}, indent=2))
    else:
        print(f"agreed {len(rep['agreed'])}  flagged {len(rep['flagged'])}")
        for f in rep["flagged"]:
            av = "" if f["a"] is None else f"{f['a'].get('value','')} {f['a'].get('unit','')}"
            bv = "" if f["b"] is None else f"{f['b'].get('value','')} {f['b'].get('unit','')}"
            print(f"  FLAG {f['analyte']}: {f['reason']}  A=[{av.strip()}] B=[{bv.strip()}]")
    # exit 1 when anything needs human sign-off, 0 when both passes fully agree.
    return 1 if rep["flagged"] else 0


if __name__ == "__main__":
    sys.exit(main())
