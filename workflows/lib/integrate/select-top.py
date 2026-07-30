#!/usr/bin/env python3
"""select-top.py — deterministic Step-4a selector.

Picks the top-N hypotheses to send to deep research by how much RAW DATA each one quotes among its
reasons (a proxy for "built on the fullest picture"): count the `[src: ...]` citations in each root's
card, drop the ones disconfirmation actively PARKED (data-refuted — we don't deep-research those), rank
the survivors by citation count, and take the top N. Everything not selected is carried forward (the
Step-7 reopen pool), never eliminated. Writes `selection.md` directly (a non-gated file) + a `--json`
summary. No LLM: counting is deterministic and an LLM miscounts.

Ranking is deterministic: (citations DESC, family order ASC per the manifest, id number ASC).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

_SRC_RE = re.compile(r"\[src:", re.IGNORECASE)
_STANDING_RE = re.compile(r"STANDING:\s*(survives|parked)", re.IGNORECASE)
_REVERT_RE = re.compile(r"revert[^\n]*\bsurvives\b", re.IGNORECASE)
_HEAD_RE = re.compile(r"^###\s+([HS]\d+)\s+[—–-]\s+(.*?)\s*$", re.MULTILINE)


class SelectError(Exception):
    pass


def count_citations(card_text: str) -> int:
    return len(_SRC_RE.findall(card_text))


def standing_of(disconfirm_text: str) -> str:
    """`survives` | `parked`. A parked card that a reframe reverted counts as survives; a card with no
    parseable standing is treated as survives (a parse miss must not silently drop a candidate)."""
    if _REVERT_RE.search(disconfirm_text):
        return "survives"
    hits = _STANDING_RE.findall(disconfirm_text)
    if hits and hits[-1].lower() == "parked":
        return "parked"
    return "survives"


def slug_from_card(card_text: str, rid: str) -> str:
    m = _HEAD_RE.search(card_text)
    return m.group(2).strip() if m else rid


def load_manifest(cards_dir: str) -> list[tuple[str, list[str]]]:
    path = os.path.join(cards_dir, "_families.json")
    if not os.path.exists(path):
        raise SelectError(f"no _families.json in {cards_dir} (run the assembler with --cards-dir first)")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    fams = data.get("families", [])
    return [(str(g.get("family", "")), [str(x) for x in g.get("ids", [])]) for g in fams]


def build_selection(cards_dir: str, disconfirm_dir: str, top_n: int) -> tuple[str, dict]:
    families = load_manifest(cards_dir)
    # family_rank = position in the manifest (the assembler already emits families in fixed order).
    fam_rank = {fam: i for i, (fam, _ids) in enumerate(families)}
    rows: list[dict] = []
    for fam, ids in families:
        for rid in ids:
            card_path = os.path.join(cards_dir, rid + ".md")
            if not os.path.exists(card_path):
                raise SelectError(f"card missing for {rid}: {card_path}")
            card = open(card_path, encoding="utf-8").read()
            dpath = os.path.join(disconfirm_dir, rid.lower() + ".md")
            standing = standing_of(open(dpath, encoding="utf-8").read()) if os.path.exists(dpath) else "survives"
            rows.append({
                "id": rid, "slug": slug_from_card(card, rid), "citations": count_citations(card),
                "standing": standing, "family": fam, "fam_rank": fam_rank.get(fam, len(families)),
                "id_num": int(re.sub(r"\D", "", rid) or 0),
            })
    survivors = [r for r in rows if r["standing"] == "survives"]
    parked = [r for r in rows if r["standing"] == "parked"]
    # deterministic rank: most cited data first, then fixed family order, then id number.
    survivors.sort(key=lambda r: (-r["citations"], r["fam_rank"], r["id_num"]))
    top = survivors[:top_n]
    carried = survivors[top_n:]
    top_ids = {r["id"] for r in top}

    out = [
        "# Step 4a — selection (deterministic: top-N by cited raw data, disconfirmation survivors)",
        "",
        f"> Selected the {len(top)} survivor hypotheses that quote the most raw data among their reasons"
        f" (a proxy for the fullest evidential picture), out of {len(survivors)} survivors"
        f" ({len(parked)} parked by disconfirmation, carried forward but not researched). Nothing is"
        " eliminated; everything not selected is the Step-7 reopen pool.",
        "",
        f"## Deep-research set (top {len(top)})",
    ]
    for r in top:
        out.append(f"- {r['id']} — {r['slug']} — cited data: {r['citations']}")
    out.append("")
    out.append("## Carried forward (not researched now — reopen pool)")
    for r in carried:
        out.append(f"- {r['id']} — {r['slug']} — survives — cited data: {r['citations']}")
    for r in parked:
        out.append(f"- {r['id']} — {r['slug']} — parked (disconfirmation) — cited data: {r['citations']}")
    text = "\n".join(out).rstrip("\n") + "\n"
    meta = {
        "ranSuccessfully": True,
        "top": [{"id": r["id"], "slug": r["slug"], "citations": r["citations"]} for r in top],
        "nSurvivors": len(survivors), "nParked": len(parked), "nCarried": len(carried),
        "nTop": len(top),
    }
    return text, meta


def atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic top-N-by-cited-data selector for Step 4a.")
    ap.add_argument("--cards-dir", required=True, help="hypotheses/cards dir (holds H*.md + _families.json)")
    ap.add_argument("--disconfirm-dir", required=True, help="disconfirm/ dir (holds h*.md standings)")
    ap.add_argument("--top", type=int, default=10, help="how many survivors to select (default 10)")
    ap.add_argument("--out", help="write selection.md here")
    ap.add_argument("--json", action="store_true", help="print the summary JSON to stdout")
    args = ap.parse_args()
    try:
        text, meta = build_selection(args.cards_dir, args.disconfirm_dir, args.top)
        if args.out:
            atomic_write(args.out, text)
        if args.json:
            print(json.dumps(meta))
        return 0
    except (SelectError, OSError, ValueError) as e:
        if args.json:
            print(json.dumps({"ranSuccessfully": False, "note": str(e)}))
        else:
            print(f"select-top: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
