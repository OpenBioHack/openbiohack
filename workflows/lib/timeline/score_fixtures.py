#!/usr/bin/env python3
"""Score a reconciliation run against a withheld answer key.

The gate this replaces was passable by a reconciler that dismissed everything, so both
directions are scored: genuine conflicts must SURVIVE, false candidates must be DISMISSED, and
the dismissals must spread across the six tests rather than all landing on one.

Three anti-cheat conditions, enforced here rather than assumed:

  - the key is never inside the fixtures the reconciler reads, and no fixture carries a label
    that gives the answer away;
  - the false candidates are split into a set the tests were derived from and a set held out, and
    the held-out numbers are reported separately;
  - the held-out set contains a genuine conflict that was not the one used to design any of this.

    score_fixtures.py --report r.md --key key.json --fixtures F --out score.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402

GIVEAWAY = re.compile(r"PLANTED|GENUINE|ANSWER[_-]?KEY|\bis_?genuine\b", re.I)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--key", required=True, type=Path)
    ap.add_argument("--fixtures", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    key = json.loads(args.key.read_text(encoding="utf-8"))

    # ── anti-cheat, checked before anything is scored ─────────────────────────
    if args.fixtures:
        if args.key.resolve().is_relative_to(args.fixtures.resolve()):
            tl.die(f"the answer key sits inside {args.fixtures} — the reconciler reads that "
                   f"directory, so the key must live outside it")
        for p in sorted(args.fixtures.rglob("*")):
            if p.is_file():
                if GIVEAWAY.search(p.name):
                    tl.die(f"fixture filename gives the answer away: {p.name}")
                if GIVEAWAY.search(p.read_text(encoding="utf-8", errors="replace")):
                    tl.die(f"fixture content gives the answer away: {p}")
        ids_in_fixtures = set(json.loads((args.fixtures / "candidates.json")
                                         .read_text(encoding="utf-8"))["candidates"][0].keys())
        if {"genuine", "truth", "label"} & ids_in_fixtures:
            tl.die("the candidates file carries a truth label")

    # ── read the outcomes out of the report ───────────────────────────────────
    outcomes: dict[str, tuple[str, str]] = {}
    for line in args.report.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"\|\s*(c\d+)\s*\|\s*(survived|dismissed)\s*\|\s*([^|]*?)\s*\|", line)
        if m:
            outcomes[m.group(1)] = (m.group(2), m.group(3).strip())

    missing = sorted(set(key) - set(outcomes))
    if missing:
        tl.die(f"the report says nothing about {len(missing)} candidate(s): "
               f"{', '.join(missing[:6])}")

    res = {"genuine_survived": 0, "genuine_missed": [], "false_dismissed": 0,
           "false_survived": [], "heldout_genuine_survived": 0, "heldout_false_dismissed": 0,
           "derivation_false_dismissed": 0, "tests_exercised": [], "wrong_test": []}
    tests: set[str] = set()
    for cid, meta in sorted(key.items()):
        outcome, failing = outcomes[cid]
        genuine = bool(meta["genuine"])
        held = bool(meta.get("held_out"))
        if genuine:
            if outcome == "survived":
                res["genuine_survived"] += 1                       # type: ignore[operator]
                if held:
                    res["heldout_genuine_survived"] += 1           # type: ignore[operator]
            else:
                res["genuine_missed"].append(cid)                  # type: ignore[union-attr]
        else:
            if outcome == "dismissed":
                res["false_dismissed"] += 1                        # type: ignore[operator]
                if held:
                    res["heldout_false_dismissed"] += 1            # type: ignore[operator]
                else:
                    res["derivation_false_dismissed"] += 1         # type: ignore[operator]
                tests.add(failing)
                if meta.get("expect_fails") and failing != meta["expect_fails"]:
                    res["wrong_test"].append(                      # type: ignore[union-attr]
                        f"{cid}: dismissed against {failing}, expected {meta['expect_fails']}")
            else:
                res["false_survived"].append(cid)                  # type: ignore[union-attr]
    res["tests_exercised"] = sorted(t for t in tests if t)

    ok = (res["genuine_survived"] >= 5 and res["false_dismissed"] >= 5      # type: ignore[operator]
          and res["heldout_genuine_survived"] >= 1                          # type: ignore[operator]
          and len(res["tests_exercised"]) >= 5)                             # type: ignore[arg-type]
    res["pass"] = bool(ok)
    args.out.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")

    print(f"genuine survived      {res['genuine_survived']}  (need 5)")
    print(f"false dismissed       {res['false_dismissed']}  (need 5) — "
          f"{res['derivation_false_dismissed']} from the derivation set, "
          f"{res['heldout_false_dismissed']} held out")
    print(f"held-out genuine      {res['heldout_genuine_survived']}  (need 1)")
    print(f"tests exercised       {len(res['tests_exercised'])}/6  "        # type: ignore[arg-type]
          f"{res['tests_exercised']}")
    if res["genuine_missed"]:
        print(f"MISSED genuine        {res['genuine_missed']}")
    if res["false_survived"]:
        print(f"WAVED THROUGH false   {res['false_survived']}")
    if res["wrong_test"]:
        print("dismissed for the wrong reason:")
        for w in res["wrong_test"]:                                # type: ignore[union-attr]
            print("  " + w)
    print(("PASS" if ok else "FAIL") + f"  →  {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
