#!/usr/bin/env python3
"""Find the places where two things in the document cannot both be true — and almost never ask.

Two agents, deliberately unequal. A narrow proposer, which may only point at pairs of passages by
identifier. A separate adversarial verifier, whose default answer is *not a conflict* and which
has to be argued out of it, one named test at a time.

The six tests are in references/timeline-source.md. A candidate is dismissed the moment it fails
one, and the dismissal records which one. Two of them are checked mechanically here rather than
being left to a model's judgement:

  test 1 — both sides are actually asserted. Each side must be a `[[TL-…]]` citation that
           resolves to verbatim text. An inference cannot be one side of a conflict.
  test 5 — the person can resolve it. Never ask them to corroborate a recorded objective
           finding: a lab value, an imaging report, a measurement.

The other four are the verifier's judgement, but it must state which test each one passed and
why. A missing reason is a dismissal, not a pass. Silence never becomes agreement.

    reconcile.py emit   --doc D --corpus C --out dispatch/
    reconcile.py verify --doc D --corpus C --fixtures F --report r.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402
import cite  # noqa: E402

TESTS = ["both-asserted", "same-thing", "same-time", "cannot-both-be-true",
         "person-can-resolve", "changes-something"]

TEST_TEXT = {
    "both-asserted": "Both sides are actually asserted — each is a verbatim span of a named "
                     "block, not an inference from one.",
    "same-thing": "They are about the same thing — the same symptom, the same substance, the "
                  "same episode. Not two things that share a word.",
    "same-time": "They are about the same time. Two statements about different periods are a "
                 "history, not a contradiction.",
    "cannot-both-be-true": "They cannot both be true. Change over time, partial recall and "
                           "hedging are not conflict. A hedged statement conflicts with nothing.",
    "person-can-resolve": "The person is the one who can resolve it. Never ask them to "
                          "corroborate a recorded objective finding.",
    "changes-something": "Resolving it would change something. If both answers lead to the same "
                         "next step, it is not worth their time.",
}

# Tags that mark a block as a recorded objective finding — test 5 refuses to ask about these.
OBJECTIVE_TAGS = {"lab", "imaging", "genetics", "procedure"}

PROPOSER = """You are reading one person's health history. Every passage in it is verbatim — their
own words, or a document's own words — and every passage has an identifier.

Point at pairs of passages that MIGHT not both be true. Nothing more. You do not decide anything;
a separate reader will try to knock each one down, and most of them will fall.

<document>
{doc}
</document>

Return JSON only:

  {{"candidates": [
     {{"id": "c01", "left": "TL-S0042", "right": "TL-S0087",
       "claim": "one sentence: what would have to be false for both to hold"}}
   ]}}

Rules:

- `left` and `right` are identifiers from the document. Never quote the text — the identifier IS
  the quote, and it is resolved for you downstream.
- A person's account changing over years is not a conflict. Neither is hedging, neither is
  partial recall, neither is one source being more precise than another.
- If you cannot find any, return an empty list. That is a good answer. The last run of this
  produced eleven candidates and two survived; manufacturing candidates wastes the person's
  time and trains everyone to ignore the output."""

VERIFIER = """A candidate conflict has been proposed in a person's health history. **Your default
answer is that it is not a conflict.** You are being asked to knock it down, and you should
expect to succeed — most candidates are not conflicts.

<candidate id="{cid}">
{claim}
</candidate>

<left id="{left}" date="{left_date}" tags="{left_tags}">
{left_text}
</left>

<right id="{right}" date="{right_date}" tags="{right_tags}">
{right_text}
</right>

It survives only if it passes ALL SIX of these. It is dismissed the moment it fails one, and you
say which.

{tests}

Return JSON only:

  {{"id": "{cid}", "survives": true|false, "fails": "<the test name, or empty>",
    "why": "one or two sentences",
    "passed": {{"both-asserted": "...", "same-thing": "...", "same-time": "...",
                "cannot-both-be-true": "...", "person-can-resolve": "...",
                "changes-something": "..."}},
    "question": "if it survives, the one question to put to the person"}}

If `survives` is true, every entry in `passed` must carry a real reason. An empty reason is a
dismissal, not a pass. If you are unsure, it does not survive."""


def load_json(p: Path) -> dict[str, object]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        tl.die(f"{p.name}: not JSON — {e}")
        raise


def mechanical(doc: tl.Document, corpus: Path, cand: dict[str, object]) -> tuple[str, str]:
    """Tests 1 and 5, applied here rather than trusted to a model. Returns (failed_test, why)."""
    for side in ("left", "right"):
        ref = str(cand.get(side, ""))
        if not tl.CITE_RE.fullmatch(f"[[{ref}]]"):
            return "both-asserted", f"{side} side {ref!r} is not a block identifier"
        try:
            cite.resolve(doc, corpus, ref)
        except SystemExit:
            return "both-asserted", f"{side} side {ref} does not resolve to text in the document"
    left, right = doc.by_id(str(cand["left"])), doc.by_id(str(cand["right"]))
    if OBJECTIVE_TAGS & set(left.tags) and OBJECTIVE_TAGS & set(right.tags):
        return ("person-can-resolve",
                "both sides are recorded objective findings — the person cannot resolve a "
                "measurement by remembering it, and must never be asked to")
    return "", ""


def emit(doc: tl.Document, corpus: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    body = "\n\n".join(f"[{b.bid}] {tl.render_date(b.date, b.prec)}\n{b.body}"
                       for b in doc.blocks)
    (out / "proposer.txt").write_text(PROPOSER.format(doc=body), encoding="utf-8")
    print(f"proposer dispatch → {out / 'proposer.txt'}")
    print("its candidates go to verify, which dispatches one adversarial verifier per candidate")
    return 0


def verify_all(doc: tl.Document, corpus: Path, fixtures: Path, report: Path,
               dispatch: Path | None) -> int:
    cands = load_json(fixtures / "candidates.json")["candidates"]     # type: ignore[index]
    verdict_dir = fixtures / "verdicts"
    rows, survived = [], []
    if dispatch:
        dispatch.mkdir(parents=True, exist_ok=True)

    tests_block = "\n".join(f"{i}. **{t}** — {TEST_TEXT[t]}" for i, t in enumerate(TESTS, 1))
    for c in cands:                                                   # type: ignore[union-attr]
        cid = str(c["id"])
        failed, why = mechanical(doc, corpus, c)                      # type: ignore[arg-type]
        if failed:
            rows.append((cid, "dismissed", failed, why))
            continue
        left, right = doc.by_id(str(c["left"])), doc.by_id(str(c["right"]))
        if dispatch:
            (dispatch / f"{cid}.txt").write_text(VERIFIER.format(
                cid=cid, claim=c.get("claim", ""), left=left.bid, right=right.bid,
                left_date=tl.render_date(left.date, left.prec),
                right_date=tl.render_date(right.date, right.prec),
                left_tags=",".join(left.tags), right_tags=",".join(right.tags),
                left_text=left.body, right_text=right.body, tests=tests_block),
                encoding="utf-8")
        vp = verdict_dir / f"{cid}.json"
        if not vp.exists():
            rows.append((cid, "dismissed", "no-verdict",
                         "the verifier returned nothing; silence is not agreement"))
            continue
        v = load_json(vp)
        if not v.get("survives"):
            f = str(v.get("fails") or "unstated")
            if f not in TESTS and f != "unstated":
                tl.die(f"{cid}: dismissed against {f!r}, which is not one of the six tests")
            rows.append((cid, "dismissed", f, str(v.get("why", ""))))
            continue
        passed = v.get("passed") or {}
        missing = [t for t in TESTS if not str(passed.get(t, "")).strip()]  # type: ignore[union-attr]
        if missing:
            rows.append((cid, "dismissed", missing[0],
                         f"claimed to survive but gave no reason for {', '.join(missing)} — an "
                         f"empty reason is a dismissal, not a pass"))
            continue
        if not str(v.get("question", "")).strip():
            rows.append((cid, "dismissed", "changes-something",
                         "no question was produced, so there is nothing to put to the person"))
            continue
        rows.append((cid, "survived", "", str(v.get("question"))))
        survived.append(cid)

    per_test: dict[str, int] = {}
    for _, outcome, t, _ in rows:
        if outcome == "dismissed":
            per_test[t] = per_test.get(t, 0) + 1
    lines = ["# Reconciliation — what is worth asking about", "",
             f"{len(cands)} candidate(s) proposed, **{len(survived)} survived** all six tests.",  # type: ignore[arg-type]
             "", "The ratio is kept visible on purpose: it is the check on whether this is "
             "finding conflicts or manufacturing them.", "",
             "| candidate | outcome | failing test | note |", "|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c or '—'} | {d} |" for a, b, c, d in rows]
    lines += ["", "## Dismissals by test", ""]
    lines += [f"- {k}: {v}" for k, v in sorted(per_test.items())] or ["- none"]
    if survived:
        lines += ["", "## To put to him", ""]
        lines += [f"- **{a}** — {d}" for a, b, c, d in rows if b == "survived"]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(cands)} candidates, {len(survived)} survived  →  {report}")  # type: ignore[arg-type]
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["emit", "verify"], nargs="?", default="verify")
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--fixtures", type=Path, help="candidates.json plus verdicts/")
    ap.add_argument("--dispatch", type=Path, help="where to write verifier prompts")
    ap.add_argument("--out", type=Path, default=Path("dispatch"))
    ap.add_argument("--report", type=Path, default=Path("reconcile-report.md"))
    args = ap.parse_args()

    doc = tl.parse(args.doc)
    corpus = args.corpus.resolve()
    if args.mode == "emit":
        return emit(doc, corpus, args.out)
    if not args.fixtures:
        tl.die("--fixtures is required: it holds the proposed candidates and the verifiers' "
               "verdicts")
    return verify_all(doc, corpus, args.fixtures, args.report, args.dispatch)


if __name__ == "__main__":
    sys.exit(main())
