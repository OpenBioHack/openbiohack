#!/usr/bin/env python3
"""select-top_test.py — fixtures for the deterministic Step-4a selector.

Run: python3 lib/integrate/select-top_test.py   (exit 0 = all pass, 1 = a failure)

Covers: citation counting, parked-exclusion, reframe revert-to-survives counted as survives, top-N
cutoff, deterministic tie-break (family order then id), carried-forward completeness, and the
degenerate/error paths (missing manifest, missing card -> exit 2).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SEL = os.path.join(HERE, "select-top.py")
PYEXE = sys.executable


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


S = _load("select_top", SEL)
_fails = 0
_tmp = tempfile.mkdtemp(prefix="select_top_test_")


def ck(desc: str, cond: object, extra: str = "") -> None:
    global _fails
    print(("  PASS  " if cond else "  XX FAIL  ") + desc + ("" if cond else f"   [{extra}]"))
    if not cond:
        _fails += 1


def write(path: str, text: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def card(rid: str, slug: str, n_src: int) -> str:
    body = "\n".join(f"REASONINGS: point {i} [src: file.md, r{i}, \"a quote\"]" for i in range(n_src))
    return f"### {rid} — {slug}\nCLAIM: {slug}\n{body}\n"


def disc(standing: str, revert: bool = False) -> str:
    t = f"YOUR HYPOTHESIS\nSTANDING: {standing}\nREASON: because\n"
    if revert:
        t += "Reframe: this was parked myopically; its standing should revert to survives.\n"
    return t


def run(cards_dir: str, disc_dir: str, top: int, out: str) -> tuple[int, dict]:
    p = subprocess.run([PYEXE, SEL, "--cards-dir", cards_dir, "--disconfirm-dir", disc_dir,
                        "--top", str(top), "--out", out, "--json"], capture_output=True, text=True)
    try:
        data = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        data = {}
    return p.returncode, data


def test_topn_and_parked() -> None:
    d = os.path.join(_tmp, "run1")
    cd = os.path.join(d, "cards")
    dd = os.path.join(d, "disconfirm")
    manifest = {"families": [{"family": "a", "ids": ["H1", "H2"]}, {"family": "b", "ids": ["H3", "H4", "H5"]}]}
    write(os.path.join(cd, "_families.json"), json.dumps(manifest))
    write(os.path.join(cd, "H1.md"), card("H1", "alpha-one", 3))
    write(os.path.join(cd, "H2.md"), card("H2", "alpha-two", 5))   # most-cited but PARKED -> excluded
    write(os.path.join(cd, "H3.md"), card("H3", "beta-three", 2))
    write(os.path.join(cd, "H4.md"), card("H4", "beta-four", 2))   # parked-then-REVERTED -> survives
    write(os.path.join(cd, "H5.md"), card("H5", "beta-five", 0))
    write(os.path.join(dd, "h1.md"), disc("survives"))
    write(os.path.join(dd, "h2.md"), disc("parked"))
    write(os.path.join(dd, "h3.md"), disc("survives"))
    write(os.path.join(dd, "h4.md"), disc("parked", revert=True))
    write(os.path.join(dd, "h5.md"), disc("survives"))
    out = os.path.join(d, "selection.md")
    code, data = run(cd, dd, 2, out)
    ck("select: exit 0", code == 0, str(data))
    # survivors = H1(3), H3(2), H4(2 reverted), H5(0); parked = H2 (excluded though it cites the most)
    ck("select: nParked == 1 (H2), nSurvivors == 4", data.get("nParked") == 1 and data.get("nSurvivors") == 4, str(data))
    top_ids = [t["id"] for t in data.get("top", [])]
    # rank: H1(3) > then tie H3 vs H4 at 2 -> family b order then id -> H3 before H4 -> top2 = [H1, H3]
    ck("select: top2 = [H1, H3] (most-cited survivors; H2 parked is out despite 5)", top_ids == ["H1", "H3"], str(top_ids))
    sel = open(out, encoding="utf-8").read()
    ck("select: H2 (parked) never in the deep-research set", "H2 —" not in sel.split("## Carried")[0])
    ck("select: H2 appears carried-forward as parked", "H2 — alpha-two — parked" in sel, sel)
    ck("select: H4 counted a survivor (reframe revert), carried not parked", "H4 — beta-four — survives" in sel)
    ck("select: nCarried == 2 (H4, H5)", data.get("nCarried") == 2, str(data))


def test_top_exceeds_survivors() -> None:
    """--top larger than the survivor count returns all survivors, no crash, no padding."""
    d = os.path.join(_tmp, "run2")
    cd, dd = os.path.join(d, "cards"), os.path.join(d, "disconfirm")
    write(os.path.join(cd, "_families.json"), json.dumps({"families": [{"family": "a", "ids": ["H1"]}]}))
    write(os.path.join(cd, "H1.md"), card("H1", "only-one", 2))
    write(os.path.join(dd, "h1.md"), disc("survives"))
    code, data = run(cd, dd, 10, os.path.join(d, "selection.md"))
    ck("select: top>survivors returns all (nTop==1)", code == 0 and data.get("nTop") == 1, str(data))


def test_missing_manifest() -> None:
    d = os.path.join(_tmp, "run3")
    cd, dd = os.path.join(d, "cards"), os.path.join(d, "disconfirm")
    os.makedirs(cd, exist_ok=True)
    os.makedirs(dd, exist_ok=True)
    code, data = run(cd, dd, 10, os.path.join(d, "selection.md"))
    ck("select: missing _families.json -> exit 2", code == 2 and data.get("ranSuccessfully") is False, str(data))


def test_missing_card() -> None:
    d = os.path.join(_tmp, "run4")
    cd, dd = os.path.join(d, "cards"), os.path.join(d, "disconfirm")
    write(os.path.join(cd, "_families.json"), json.dumps({"families": [{"family": "a", "ids": ["H1", "H2"]}]}))
    write(os.path.join(cd, "H1.md"), card("H1", "present", 1))   # H2 card intentionally absent
    write(os.path.join(dd, "h1.md"), disc("survives"))
    code, data = run(cd, dd, 10, os.path.join(d, "selection.md"))
    ck("select: a manifest id with no card -> exit 2 (no silent drop)", code == 2, str(data))


if __name__ == "__main__":
    test_topn_and_parked()
    test_top_exceeds_survivors()
    test_missing_manifest()
    test_missing_card()
    print(("ALL PASS" if _fails == 0 else f"{_fails} FAILED"))
    sys.exit(1 if _fails else 0)
