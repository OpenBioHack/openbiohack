#!/usr/bin/env python3
"""Place each passage in time: two daters, and an adjudicator where they disagree.

The person speaks out of order — a story about 2015 in the middle of a passage about 2022 — so
something has to decide where each passage belongs. That is the one judgement in the whole
document, and it is the only place a model's opinion enters. Its opinion never becomes text: it
returns a date, a precision and evidence, and `move.py` does the placing.

The two daters start from deliberately different places:

  A — the block alone. No neighbours, no file order, no surrounding document. Only what the
      passage itself says.
  B — the block in its source's own order, with the dated records around it. Position and
      external anchors, which A cannot see.

Where they agree, the placement is accepted without review — which is why `calibrate_dating.py`
has to have measured how often they agree *and are both wrong* before this runs at scale. Where
they disagree, C sees both cases and may propose better.

Every piece of evidence a dater cites must be a verbatim substring of the block's own source
span. A fabricated quote is rejected and that dater is re-run; it never reaches the adjudicator.

    date_council.py emit    --doc D --corpus C --out dispatch/
    date_council.py collect --doc D --corpus C --verdicts verdicts/ --report r.md
    date_council.py apply   --doc D --plan plan.json --batch dating
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402

CONTEXT_BYTES = 3000

DATER_A = """You are dating ONE passage from a person's health history. You can see the passage
and nothing else — not what comes before it, not what comes after it, not where it sits in any
file. That is deliberate: your job is to read what the passage ITSELF says about when it happened.

The passage is below, between the markers. It is verbatim: the person's own words, or a
document's own words. It may be transcribed speech, so it may be ungrammatical.

<passage id="{bid}">
{body}
</passage>

Return JSON only:

  {{"date": "...", "prec": "day|month|year|span|unknown", "confidence": 0.0-1.0,
    "evidence": ["...", "..."], "reasoning": "one or two sentences"}}

Rules that matter:

- `date` formats: day `YYYY-MM-DD`, month `YYYY-MM`, year `YYYY`, span `YYYY..YYYY` or
  `YYYY-MM..YYYY-MM`. For `unknown`, use an empty string.
- Choose the COARSEST precision the passage actually supports. If it says "around 2015", that is
  year precision, not a day. Claiming more precision than the words support is the single worst
  thing you can do here.
- Every string in `evidence` MUST be copied character for character from the passage above. It is
  checked against the source file. A quote that is not verbatim gets your whole verdict thrown
  away and this passage re-dated.
- If the passage genuinely says nothing about when it happened, return `unknown` with an empty
  evidence list. That is a useful answer. Guessing is not.
- Date the EVENT the passage is about, not the moment it was said or written."""

DATER_B = """You are dating ONE passage from a person's health history. You can see where it sits
in its source file and what surrounds it, and you can see the dated records from elsewhere in the
history. Another rater is looking at the passage alone with none of this; your job is the other
half — position, sequence and external anchors.

<passage id="{bid}" source="{src}" bytes="{a}:{z}">
{body}
</passage>

<what precedes it in the same file>
{before}
</what precedes it in the same file>

<what follows it in the same file>
{after}
</what follows it in the same file>

<dated records elsewhere in this history>
{anchors}
</dated records elsewhere in this history>

Return JSON only:

  {{"date": "...", "prec": "day|month|year|span|unknown", "confidence": 0.0-1.0,
    "evidence": ["...", "..."], "reasoning": "one or two sentences"}}

Rules that matter:

- Same formats and the same coarsest-precision rule as the other rater.
- Every string in `evidence` MUST be copied character for character **from the passage itself**,
  not from the surrounding context and not from the anchors. It is checked against the source
  file. A quote that is not verbatim gets your whole verdict thrown away.
- Position in a file is evidence about when something was SAID, which is often not when it
  HAPPENED. The person tells stories out of order. Where the passage's own words contradict its
  position in the file, the words win.
- If nothing supports a placement, return `unknown`. Guessing is not useful."""

ADJUDICATOR = """Two raters placed the same passage in time and disagreed. You can see the
passage, both verdicts and both sets of evidence. Every quote below has already been machine-
checked as verbatim, so you are judging reasoning, not honesty.

<passage id="{bid}">
{body}
</passage>

<rater A — saw the passage alone>
{a_verdict}
</rater A — saw the passage alone>

<rater B — saw its position and the surrounding records>
{b_verdict}
</rater B — saw its position and the surrounding records>

Return JSON only:

  {{"date": "...", "prec": "day|month|year|span|unknown", "confidence": 0.0-1.0,
    "evidence": ["..."], "reasoning": "why this rather than the other",
    "chose": "A|B|neither"}}

You may propose a placement neither of them gave, including a coarser one. Two raters
disagreeing at day precision is usually a sign the honest answer is a month or a year: if their
disagreement is itself the evidence that the passage does not pin down a day, say so and return
the coarser precision. Your evidence quotes must be verbatim from the passage."""


def anchors_for(doc: tl.Document, limit: int = 40) -> str:
    """Dated records from elsewhere in the history — B's external frame."""
    dated = [b for b in doc.blocks if b.prec in ("day", "month")]
    step = max(1, len(dated) // limit)
    return "\n".join(f"{tl.render_date(b.date, b.prec)} — {tl.opening_words(b.body, 80)}"
                     for b in dated[::step][:limit])


def emit(doc: tl.Document, corpus: Path, out: Path, only: str | None) -> int:
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    anchors = anchors_for(doc)
    for b in doc.blocks:
        if only and b.bid != only:
            continue
        a, z = b.span
        raw = tl.source_bytes(corpus / b.src)
        before = raw[max(0, a - CONTEXT_BYTES):a].decode("utf-8", errors="ignore")
        after = raw[z:z + CONTEXT_BYTES].decode("utf-8", errors="ignore")
        for role, template, fields in (
            ("A", DATER_A, {}),
            ("B", DATER_B, {"src": b.src, "a": a, "z": z, "before": before, "after": after,
                            "anchors": anchors}),
        ):
            (out / f"{b.bid}-{role}.txt").write_text(
                template.format(bid=b.bid, body=b.body, **fields), encoding="utf-8")
            n += 1
    print(f"emitted {n} dispatches for {n // 2} blocks → {out}")
    print("each is a complete prompt. A dater returns JSON to "
          f"{out.name.rstrip('/')}/../verdicts/<block>-<role>.json")
    return 0


def read_verdict(p: Path) -> dict[str, object] | None:
    if not p.exists():
        return None
    try:
        v = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        tl.die(f"{p.name}: the dater did not return JSON — {e}")
        return None
    for k in ("date", "prec", "evidence"):
        if k not in v:
            tl.die(f"{p.name}: verdict is missing {k!r}")
    if v["prec"] not in tl.PRECISIONS:
        tl.die(f"{p.name}: precision {v['prec']!r} is not one of {tl.PRECISIONS}")
    tl.render_date(str(v["date"]), str(v["prec"]))
    return v


def evidence_ok(block: tl.Block, corpus: Path, verdict: dict[str, object]) -> tuple[bool, str]:
    """Every cited quote is a verbatim substring of THIS block's own source span.

    Stricter than the pipeline's general citation verifier, and deliberately so: here the span is
    known exactly, so there is no reason to allow whitespace-insensitive matching.
    """
    a, z = block.span
    span_text = tl.slice_source(corpus / block.src, a, z)
    for q in verdict.get("evidence", []):        # type: ignore[union-attr]
        if not str(q).strip():
            return False, "an empty evidence quote"
        if str(q) not in span_text:
            return False, f"not verbatim in {block.src} {a}:{z}: {str(q)[:60]!r}"
    if verdict["prec"] != "unknown" and not verdict.get("evidence"):
        return False, "a placement with no evidence at all"
    return True, ""


def agree(x: dict[str, object], y: dict[str, object], rule: str) -> bool:
    if x["prec"] == "unknown" or y["prec"] == "unknown":
        return False                     # a dater returning nothing is absent, not agreeing
    if rule == "exact":
        return x["date"] == y["date"] and x["prec"] == y["prec"]
    if rule == "year":                   # tightened form: agree only on the year, place at year
        return str(x["date"])[:4] == str(y["date"])[:4]
    tl.die(f"unknown agreement rule {rule!r}")
    return False


def collect(doc: tl.Document, corpus: Path, verdicts: Path, rule: str, report: Path,
            plan_out: Path) -> int:
    rows, plan, rerun, needs_c = [], [], [], []
    for b in doc.blocks:
        va = read_verdict(verdicts / f"{b.bid}-A.json")
        vb = read_verdict(verdicts / f"{b.bid}-B.json")
        if va is None or vb is None:
            rows.append((b.bid, "absent", "", "a dater returned nothing"))
            continue
        for role, v in (("A", va), ("B", vb)):
            ok, why = evidence_ok(b, corpus, v)
            if not ok:
                rerun.append((b.bid, role, why))
                v["_rejected"] = why
        if any("_rejected" in v for v in (va, vb)):
            rows.append((b.bid, "re-run", "", "; ".join(f"{r}: {w}" for _, r, w in rerun
                                                        if _ == b.bid)))
            continue
        vc = read_verdict(verdicts / f"{b.bid}-C.json")
        if agree(va, vb, rule):
            rows.append((b.bid, "agreed", f"{va['date']} ({va['prec']})", ""))
            plan.append({"block": b.bid, "date": va["date"], "prec": va["prec"],
                         "how": "agreed", "evidence_verified": True})
        elif vc is not None:
            ok, why = evidence_ok(b, corpus, vc)
            if not ok:
                rerun.append((b.bid, "C", why))
                rows.append((b.bid, "re-run", "", f"C: {why}"))
                continue
            rows.append((b.bid, "adjudicated", f"{vc['date']} ({vc['prec']})",
                         f"A said {va['date']}, B said {vb['date']}"))
            plan.append({"block": b.bid, "date": vc["date"], "prec": vc["prec"],
                         "how": "adjudicated", "evidence_verified": True})
        else:
            needs_c.append(b.bid)
            rows.append((b.bid, "needs C", "", f"A said {va['date']}, B said {vb['date']}"))

    lines = ["# Dating — what the council decided", "",
             f"Agreement rule: `{rule}`. Where the two raters agree the placement is accepted "
             f"without review, so the calibration report is what says whether that is safe.", "",
             "| block | outcome | placed at | note |", "|---|---|---|---|"]
    lines += [f"| {b} | {o} | {p} | {n} |" for b, o, p, n in rows]
    counts: dict[str, int] = {}
    for _, o, _, _ in rows:
        counts[o] = counts.get(o, 0) + 1
    lines += ["", "## Totals", ""] + [f"- {k}: {v}" for k, v in sorted(counts.items())]
    if rerun:
        lines += ["", "## Rejected for unverifiable evidence — these raters are re-run", ""]
        lines += [f"- {b} rater {r}: {w}" for b, r, w in rerun]
    if needs_c:
        lines += ["", "## Waiting on the adjudicator", "", ", ".join(needs_c)]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    plan_out.write_text(json.dumps({"placements": plan}, indent=1) + "\n", encoding="utf-8")

    print(f"{len(doc.blocks)} blocks: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    if rerun:
        print(f"{len(rerun)} verdict(s) rejected — evidence was not verbatim. Re-run those raters.")
    print(f"report: {report}\nplan:   {plan_out}")
    return 0


def apply(doc_path: Path, plan_path: Path, batch: str) -> int:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))["placements"]
    doc = tl.parse(doc_path)
    ordered = sorted(plan, key=lambda p: tl.sort_key(str(p["date"]), str(p["prec"]), 0))
    here = Path(__file__).resolve().parent
    applied = 0
    for i, p in enumerate(ordered):
        if not p.get("evidence_verified"):
            tl.die(f"{p['block']}: the plan does not record its evidence as verified")
        anchor = ordered[i - 1]["block"] if i else None
        cmd = [sys.executable, str(here / "move.py"), "--doc", str(doc_path),
               "--block", str(p["block"]), "--date", str(p["date"]), "--prec", str(p["prec"]),
               "--batch", batch]
        cmd += ["--after", str(anchor)] if anchor else ["--before", doc.blocks[0].bid]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            tl.die(f"placing {p['block']} failed: {r.stdout + r.stderr}")
        applied += 1
    print(f"placed {applied} blocks with move.py; every one kept its identifier and its text")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["emit", "collect", "apply"], nargs="?", default="collect")
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--corpus", type=Path)
    ap.add_argument("--out", type=Path, default=Path("dispatch"))
    ap.add_argument("--verdicts", type=Path, default=Path("verdicts"))
    ap.add_argument("--report", type=Path, default=Path("dating-report.md"))
    ap.add_argument("--plan", type=Path, default=Path("dating-plan.json"))
    ap.add_argument("--agree-rule", default="exact", choices=["exact", "year"])
    ap.add_argument("--calibration", type=Path,
                    help="the calibration report. The council will not run at scale without it.")
    ap.add_argument("--block", help="one block only")
    ap.add_argument("--batch", default="dating")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = tl.parse(args.doc)

    if args.block and args.json:
        b = doc.by_id(args.block)
        va = read_verdict(args.verdicts / f"{b.bid}-A.json")
        vb = read_verdict(args.verdicts / f"{b.bid}-B.json")
        vc = read_verdict(args.verdicts / f"{b.bid}-C.json")
        out: dict[str, object] = {"block": b.bid, "have_A": va is not None,
                                  "have_B": vb is not None}
        if va and vb and args.corpus:
            oks = [evidence_ok(b, args.corpus.resolve(), v) for v in (va, vb) + ((vc,) if vc else ())]
            out["evidence_verified"] = all(o for o, _ in oks)
            out["why"] = [w for o, w in oks if not o]
            out["agreed"] = agree(va, vb, args.agree_rule)
            chosen = va if out["agreed"] else vc
            out["date"] = chosen["date"] if chosen else ""
            out["prec"] = chosen["prec"] if chosen else "unknown"
            out["how"] = "agreed" if out["agreed"] else ("adjudicated" if vc else "needs C")
        else:
            out["evidence_verified"] = False
            out["why"] = ["no verdicts collected for this block yet"]
        print(json.dumps(out, ensure_ascii=False))
        return 0

    if args.mode in ("emit", "collect") and not args.block:
        if not args.calibration or not args.calibration.exists():
            tl.die("the council does not run at scale without a calibration report. Run "
                   "calibrate_dating.py first and read it: where the two raters agree, the "
                   "placement is accepted without review, so how often they agree AND are both "
                   "wrong is the number that decides whether this is safe.")

    if args.mode == "emit":
        if not args.corpus:
            tl.die("--corpus is required to emit dispatches")
        return emit(doc, args.corpus.resolve(), args.out, args.block)
    if args.mode == "apply":
        if args.dry_run:
            print(json.dumps(json.loads(args.plan.read_text(encoding="utf-8")), indent=1))
            return 0
        return apply(args.doc, args.plan, args.batch)
    if not args.corpus:
        tl.die("--corpus is required to check evidence")
    return collect(doc, args.corpus.resolve(), args.verdicts, args.agree_rule, args.report,
                   args.plan)


if __name__ == "__main__":
    sys.exit(main())
