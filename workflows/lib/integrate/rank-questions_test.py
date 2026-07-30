#!/usr/bin/env python3
"""rank-questions_test.py — fixtures for the deterministic interview question-ranker.

Run: python3 lib/integrate/rank-questions_test.py   (exit 0 = all pass, 1 = a failure)

Covers: pool parsing (and NOT parsing the pass-log tables), fork detection, reach from the
expected-answer field, tied-pair targeting outranking a bare fork, high-consequence boost,
answered-row exclusion, person/test split, determinism, and the error paths.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RANK = os.path.join(HERE, "rank-questions.py")
PYEXE = sys.executable


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


K = _load("rank_questions", RANK)
_fails = 0
_tmp = tempfile.mkdtemp(prefix="rank_questions_test_")

HDR = "| q-id | text | expected-answer-per-hyp | sensitivity | specificity | disposition | src |\n|---|---|---|---|---|---|---|\n"

BANK = (
    "# question bank\n\n"
    "## Question pool — H11 (fermentable load)\n\n" + HDR
    # a plain fork that does NOT name both tied members (H5 is not live) -> no tied bonus
    + "| H11-Q1 | Do you notice symptoms after onion and garlic? | H11 predicts yes; H5 predicts no. FORK | high | high | open | - |\n"
    # tied-pair splitter: names both H11 and H26 -> should outrank the plain fork
    + "| H11-Q2 | Does the reaction scale with the amount you eat? | H11 vs H26 diverge here; also H5. FORK | high | high | open | - |\n"
    # already answered -> excluded entirely
    + "| H11-Q3 | Did restriction help? | H11 predicts yes | high | high | answered | [src: notes] |\n"
    # a test question -> the tests list, not the interview list
    + "| H11-Q4 | Have faecal short-chain fatty acids ever been measured? | H11 predicts low | high | high | open | - |\n"
    "\n## Question pool — H33 (high-consequence screen)\n\n" + HDR
    # high-consequence boost, reach 1, no fork
    + "| H33-Q1 | Do the flush episodes wake you at night? | H33 predicts yes | moderate | moderate | partial | - |\n"
    "\n## Pass log\n\n"
    "| q-id | answer as recorded | tier + source | bearing |\n|---|---|---|---|\n"
    # a pass-log row whose first cell is ALSO a q-id — must NOT be parsed as a pooled question
    + "| H11-Q9 | some recorded answer | T4 | bearing text |\n"
)


def ck(desc: str, cond: object, extra: str = "") -> None:
    global _fails
    print(("  PASS  " if cond else "  XX FAIL  ") + desc + ("" if cond else f"   [{extra}]"))
    if not cond:
        _fails += 1


def run(bank_path: str, extra: list[str]) -> tuple[int, dict]:
    p = subprocess.run([PYEXE, RANK, "--bank", bank_path, "--json"] + extra, capture_output=True, text=True)
    try:
        data = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        data = {}
    return p.returncode, data


def test_ranking() -> None:
    bank = os.path.join(_tmp, "question-bank.md")
    with open(bank, "w", encoding="utf-8") as fh:
        fh.write(BANK)
    out = os.path.join(_tmp, "shortlist.md")
    code, data = run(bank, ["--live", "H11,H26,H33", "--tied", "H11:H26",
                            "--high-consequence", "H33", "--top", "10", "--out", out])
    ck("rank: exit 0", code == 0, str(data))
    # 5 pooled questions (the pass-log row is NOT one of them)
    ck("rank: parses ONLY the pool sections (pass-log q-id row ignored)", data.get("nPooled") == 5, str(data.get("nPooled")))
    # H11-Q3 is `answered` -> excluded from askable
    ck("rank: answered rows excluded from askable (4 of 5)", data.get("nAskable") == 4, str(data.get("nAskable")))
    person_ids = [q["qid"] for q in data.get("topPerson", [])]
    test_ids = [q["qid"] for q in data.get("topTests", [])]
    ck("rank: the measured-SCFA question goes to the TESTS list, not the interview list",
       "H11-Q4" in test_ids and "H11-Q4" not in person_ids, f"person={person_ids} tests={test_ids}")
    ck("rank: answered question appears in neither list", "H11-Q3" not in person_ids + test_ids)
    # the tied-pair splitter must outrank the plain fork
    ck("rank: tied-pair splitter (H11-Q2) outranks the plain fork (H11-Q1)",
       person_ids and person_ids[0] == "H11-Q2", str(person_ids))
    why = {q["qid"]: q["why"] for q in data.get("topPerson", [])}
    ck("rank: the tied split is named in the reason", "splits tied H11↔H26" in why.get("H11-Q2", ""), str(why))
    ck("rank: high-consequence boost is named for H33", "high-consequence" in why.get("H33-Q1", ""), str(why))
    shortlist = open(out, encoding="utf-8").read()
    ck("rank: shortlist has both sections", "## Ask the person" in shortlist and "## Tests worth buying" in shortlist)


def test_determinism() -> None:
    bank = os.path.join(_tmp, "question-bank.md")
    a, b = os.path.join(_tmp, "a.md"), os.path.join(_tmp, "b.md")
    run(bank, ["--live", "H11,H26,H33", "--tied", "H11:H26", "--out", a])
    run(bank, ["--live", "H11,H26,H33", "--tied", "H11:H26", "--out", b])
    ck("rank: same inputs -> byte-identical output",
       open(a, encoding="utf-8").read() == open(b, encoding="utf-8").read())


def test_errors() -> None:
    empty = os.path.join(_tmp, "empty.md")
    with open(empty, "w", encoding="utf-8") as fh:
        fh.write("# nothing here\n")
    code, data = run(empty, [])
    ck("rank: a bank with no pool sections -> exit 2", code == 2 and data.get("ranSuccessfully") is False, str(data))
    bank = os.path.join(_tmp, "question-bank.md")
    code, data = run(bank, ["--tied", "H11"])
    ck("rank: a malformed --tied pair -> exit 2", code == 2, str(data))


if __name__ == "__main__":
    test_ranking()
    test_determinism()
    test_errors()
    print("ALL PASS" if _fails == 0 else f"{_fails} FAILED")
    sys.exit(1 if _fails else 0)
