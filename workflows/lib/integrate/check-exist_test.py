#!/usr/bin/env python3
"""check-exist_test.py — the deterministic existence checker: present, absent, empty, mixed."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "check-exist.py")
_tmp = tempfile.mkdtemp(prefix="check_exist_test_")
_fails = 0


def ck(desc: str, cond: object, extra: str = "") -> None:
    global _fails
    print(("  PASS  " if cond else "  XX FAIL  ") + desc + ("" if cond else f"   [{extra}]"))
    if not cond:
        _fails += 1


def run(paths: list[str]) -> dict:
    p = subprocess.run([sys.executable, TOOL, "--paths", *paths, "--json"], capture_output=True, text=True)
    return json.loads(p.stdout)


def w(name: str, content: str) -> str:
    p = os.path.join(_tmp, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(content)
    return p


present = w("present.md", "# real content\n")
empty = w("empty.md", "")
absent = os.path.join(_tmp, "does-not-exist.md")

r = run([present])
ck("present non-empty file → missing == []", r["missing"] == [] and r["checked"] == 1, str(r))
ck("present → ranSuccessfully true", r["ranSuccessfully"] is True)

r = run([absent])
ck("absent file → missing == [that path]", r["missing"] == [absent], str(r))

r = run([empty])
ck("empty (zero-byte) file → counted MISSING", r["missing"] == [empty], str(r))

r = run([present, absent, empty])
ck("mixed → only the absent + empty are missing, in input order",
   r["missing"] == [absent, empty] and r["checked"] == 3, str(r))

print(f"\n{'ALL PASS' if _fails == 0 else str(_fails) + ' FAILURE(S)'}")
sys.exit(1 if _fails else 0)
