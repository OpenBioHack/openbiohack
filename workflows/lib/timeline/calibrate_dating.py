#!/usr/bin/env python3
"""Measure how often the two raters agree AND are both wrong. Before the council is trusted.

The council accepts a placement without review whenever its two raters agree. That is only safe
if agreement is actually informative — if the two can agree and be wrong together at some rate,
the whole document is silently mis-dated at that rate and nothing downstream can tell.

So: take segments whose true date is known because the record itself states it, hide the date
cues from the raters, run exactly the same two prompts, and count three things.

    agreement rate        how often A and B agree at all
    accuracy on agreement how often, when they agree, they are right
    false-agreement rate  how often they agree and are BOTH wrong  ← the number that matters

A missing calibration report blocks the council rather than defaulting to accept.

    calibrate_dating.py emit    --doc D --corpus C --n 25 --redact-cues --out calib-dispatch/
    calibrate_dating.py score   --doc D --corpus C --verdicts calib-verdicts/ --out calib.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402
import date_council as dc  # noqa: E402

MONTHS = ("january|february|march|april|may|june|july|august|september|october|november|december"
          "|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec")
CUE_PATTERNS = [
    r"\b(19|20)\d{2}\b",                                   # a bare year
    r"\b\d{1,2}[/.-]\d{1,2}[/.-](19|20)?\d{2}\b",          # 11/07/2019, 11-7-19
    rf"\b\d{{1,2}}\s+({MONTHS})\s+(19|20)?\d{{2}}\b",      # 11 July 2019
    rf"\b({MONTHS})\s+\d{{1,2}},?\s+(19|20)?\d{{2}}\b",    # July 11, 2019
    rf"\b({MONTHS})\b",                                    # a bare month name
]


def redact(text: str) -> tuple[str, int]:
    n = 0
    out = text
    for pat in CUE_PATTERNS:
        out, k = re.subn(pat, "[date redacted]", out, flags=re.I)
        n += k
    return out, n


def known_dated(doc: tl.Document) -> list[tl.Block]:
    """Blocks whose true date is known because the record states it, not because we chose it.

    Day and month precision both qualify: a clinic letter's clinic date and a lab's collection
    month are both printed on the record. Scoring compares at year level, so a month-precision
    truth is as usable as a day-precision one.
    """
    return [b for b in doc.blocks if b.prec in ("day", "month")]


def pick(doc: tl.Document, n: int) -> list[tl.Block]:
    """A spread across the whole history, chosen deterministically — never a random sample."""
    pool = known_dated(doc)
    if not pool:
        tl.die("no block in the document carries a date the record itself states, so there is "
               "nothing to calibrate against. Calibration cannot run.")
    if len(pool) <= n:
        print(f"NOTE: {n} segments were asked for and the document has {len(pool)} whose true "
              f"date is stated by the record. Calibrating on all {len(pool)}; the report says "
              f"so, and a rate measured on {len(pool)} carries the uncertainty of {len(pool)}.")
        return pool
    step = len(pool) / n
    return [pool[int(i * step)] for i in range(n)]


def emit(doc: tl.Document, corpus: Path, out: Path, n: int, do_redact: bool) -> int:
    out.mkdir(parents=True, exist_ok=True)
    chosen = pick(doc, n)
    key: dict[str, dict[str, object]] = {}
    anchors = dc.anchors_for(doc)
    total_cues = 0
    for b in chosen:
        a, z = b.span
        raw = tl.source_bytes(corpus / b.src)
        body, cues = redact(b.body) if do_redact else (b.body, 0)
        before, _ = redact(raw[max(0, a - dc.CONTEXT_BYTES):a].decode("utf-8", "ignore")) \
            if do_redact else (raw[max(0, a - dc.CONTEXT_BYTES):a].decode("utf-8", "ignore"), 0)
        after, _ = redact(raw[z:z + dc.CONTEXT_BYTES].decode("utf-8", "ignore")) \
            if do_redact else (raw[z:z + dc.CONTEXT_BYTES].decode("utf-8", "ignore"), 0)
        anc, _ = redact(anchors) if do_redact else (anchors, 0)
        total_cues += cues
        (out / f"{b.bid}-A.txt").write_text(dc.DATER_A.format(bid=b.bid, body=body),
                                            encoding="utf-8")
        (out / f"{b.bid}-B.txt").write_text(
            dc.DATER_B.format(bid=b.bid, body=body, src=b.src, a=a, z=z,
                              before=before, after=after, anchors=anc), encoding="utf-8")
        key[b.bid] = {"true_date": b.date, "true_prec": b.prec, "cues_hidden": cues}
    (out / "key.json").write_text(json.dumps(key, indent=1) + "\n", encoding="utf-8")
    print(f"emitted {len(chosen) * 2} dispatches over {len(chosen)} segments with known dates")
    print(f"date cues hidden: {total_cues}" if do_redact
          else "WARNING: cues NOT hidden — the raters can read the answer off the text")
    print(f"the answer key is {out / 'key.json'} — it is not in any dispatch")
    return 0


def year_of(d: str) -> str:
    return str(d).split("..")[0][:4]


def score(verdicts: Path, keyfile: Path, out: Path, rule: str) -> int:
    key = json.loads(keyfile.read_text(encoding="utf-8"))
    rows, agreed, agreed_right, agreed_wrong, no_agree = [], 0, 0, 0, 0
    for bid, truth in sorted(key.items()):
        va = dc.read_verdict(verdicts / f"{bid}-A.json")
        vb = dc.read_verdict(verdicts / f"{bid}-B.json")
        if va is None or vb is None:
            rows.append((bid, "absent", "", "", str(truth["true_date"]), ""))
            continue
        ok = dc.agree(va, vb, rule)
        # Right = the same year as the record states. A rater that returns a coarser precision
        # covering the true date is right at its own precision, not wrong.
        right = ok and year_of(str(va["date"])) == year_of(str(truth["true_date"]))
        if ok:
            agreed += 1
            agreed_right += bool(right)
            agreed_wrong += (not right)
        else:
            no_agree += 1
        rows.append((bid, "agreed" if ok else "disagreed", str(va["date"]), str(vb["date"]),
                     str(truth["true_date"]), "right" if right else ("WRONG" if ok else "—")))

    n = agreed + no_agree
    rate = (agreed / n) if n else 0.0
    acc = (agreed_right / agreed) if agreed else 0.0
    false_agreement = (agreed_wrong / n) if n else 0.0

    lines = [
        "# Dating calibration — is agreement informative?", "",
        f"Segments with independently known dates: **{n}**. Date cues were hidden from both "
        f"raters, so neither could read the answer off the text.", "",
        f"- agreement rate: **{rate:.0%}** ({agreed} of {n})",
        f"- accuracy when they agree: **{acc:.0%}** ({agreed_right} of {agreed})",
        f"- **false-agreement rate: {false_agreement:.0%}** ({agreed_wrong} of {n}) — they "
        f"agreed and were both wrong", "",
        "The last number is the one that decides whether the council is safe to run at scale, "
        "because agreement is accepted without review. Every one of those is a passage that "
        "would be placed in the wrong part of the person's life with nothing downstream able to "
        "notice.", "",
    ]
    if false_agreement > 0.10:
        lines += ["## Read this before running the council", "",
                  f"At {false_agreement:.0%}, agreement is not informative enough to accept "
                  f"without review. Tighten the rule (`--agree-rule year`, which accepts only "
                  f"agreement on the year and places at year precision), or send agreed "
                  f"placements to the adjudicator as well.", ""]
    else:
        lines += [f"At {false_agreement:.0%}, accepting agreement without review costs about "
                  f"{agreed_wrong} mis-placement(s) in {n}. Whether that is acceptable is a "
                  f"judgement for the person whose history it is, not for this script.", ""]
    lines += ["| block | outcome | A | B | true | verdict |", "|---|---|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"agreement {rate:.0%} · accuracy-on-agreement {acc:.0%} · "
          f"false-agreement {false_agreement:.0%}")
    print(f"report: {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["emit", "score"])
    ap.add_argument("--doc", type=Path)
    ap.add_argument("--corpus", type=Path)
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--redact-cues", action="store_true")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--verdicts", type=Path)
    ap.add_argument("--key", type=Path)
    ap.add_argument("--agree-rule", default="exact", choices=["exact", "year"])
    args = ap.parse_args()

    if args.mode == "emit":
        if not (args.doc and args.corpus):
            tl.die("--doc and --corpus are required to emit")
        return emit(tl.parse(args.doc), args.corpus.resolve(), args.out, args.n,
                    args.redact_cues)
    if not args.verdicts:
        tl.die("--verdicts is required to score")
    keyfile = args.key or (args.verdicts.parent / "calib-dispatch" / "key.json")
    if not keyfile.exists():
        tl.die(f"no answer key at {keyfile}")
    return score(args.verdicts, keyfile, args.out, args.agree_rule)


if __name__ == "__main__":
    sys.exit(main())
