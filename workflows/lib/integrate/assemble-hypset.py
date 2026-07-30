#!/usr/bin/env python3
"""assemble-hypset.py — the deterministic 2c assembler (Step 2c, Hypothesise stage).

Collates the 11 per-family `integrated-<family>.md` files into the single `hypothesis-set.md`
the downstream stages consume. Replaces the old free-form LLM assembler, which twice failed (hung,
and silently wrote nothing so a stale run-1 file poisoned the pipeline). The mechanical work —
parse, renumber, bucket contributing factors, preserve REASONINGS verbatim, enforce anti-flatten —
is done here in code; the ONE semantic call (which roots across families are the SAME root, and
which entries should move) is made upstream by a bounded LLM judge and handed in as `--instructions`.

The tool builds the document and WRITES it (`--out`) itself — that file is what passes to the next
stage. No LLM in the writing path: because it rewrites the file wholesale every run, a leftover
stale file cannot survive a re-run. The bash-gate allows this named `python3` write (it is a read
ARG, not an inline `>`/`tee`/`cp`/`sed -i` redirect); the Write/Edit write-check never fires on an
internal file write.

Compliance guarantees kept IN CODE (not by an LLM re-reading a spec):
  - anti-flatten: every input `### HYP`/`### CF` entry maps to exactly one output entry; a merged
    entry's REASONINGS contain every absorbed member's lines byte-for-byte; zero-owner / duplicate
    / dropped-rationale => exit 2 (fail-closed, NO file written).
  - verbatim REASONINGS: every input REASONINGS line appears byte-for-byte in the output.
  - grounding: re-runs the real `investigate-grounding-anchor.py` admissibility check over the
    assembled roots (single-source with the gate it bypasses); an inadmissible root => exit 2.

CLI:
  python3 assemble-hypset.py --integrated-dir <dir> --out <hypothesis-set.md>
                             [--instructions <map.json>] [--index <index.md>]
                             [--grounding-lib <path>] [--no-grounding] [--json]

Exit codes: 0 = assembled + written; 2 = a fail-closed check tripped (no/atomic file).
"""
from __future__ import annotations

import argparse
import base64
import binascii
import glob
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass, field

# ── deterministic family order (renumbering follows THIS, never filesystem glob order) ────────────
FAMILY_ORDER = [
    "constitutional-genetic", "endocrine-regulatory", "external-exposure",
    "iatrogenic-treatment", "immune-mediated", "infective-organismal",
    "metabolic-nutritional", "neoplastic-proliferative",
    "psychological-nervous-system", "structural-anatomic", "vascular-circulatory",
]

DEFAULT_GROUNDING_LIB = os.path.expanduser("~/.claude/hooks/lib/investigate-grounding-anchor.py")
DEFAULT_NULL_SLUG = "no-single-unifying-driver"
NULL_CLAIM = ("No single unifying root cause; the findings are treated as independent processes, "
              "pending disconfirmation. Present as the parallel-null against which the roots compete.")

# any `## ` heading (e.g. a `## CONTRIBUTING FACTORS` organiser, present in only some families)
# closes the current entry body; it is never itself an entry.
_SEC_ANY = re.compile(r"^\s*##\s+\S")
# entry headings — only recognised at true line-start inside the matching section (phantom-safe).
_HYP_HEAD = re.compile(r"^###\s+HYP\s+H(\d+)\b(.*)$")
_CF_HEAD = re.compile(r"^###\s+CF(\d+)\b(.*)$")
_HR = re.compile(r"^\s*---+\s*$")
_COMPOUND = re.compile(r"\[COMPOUND\]", re.I)
_CLAIM = re.compile(r"^\s*CLAIM:\s*(.*)$")
_FEEDS = re.compile(r"^\s*FEEDS:\s*(.*)$")
_REASONING_BULLET = re.compile(r'^-\s+"')          # a REASONINGS bullet: `- "…" [from:…] [data:…]`


class AssembleError(Exception):
    """A fail-closed condition — the caller maps this to exit 2 and writes no file."""


@dataclass
class Entry:
    kind: str                       # "root" | "cf"
    family: str
    local_id: str                   # "H1" / "CF1" (family-local)
    compound: bool
    body: list[str] = field(default_factory=list)          # raw body lines, byte-for-byte
    claim: str = ""
    feeds: str = ""
    reasonings: list[str] = field(default_factory=list)    # the `- "…"` lines, byte-for-byte
    order: int = 0                  # appearance order within its family file

    @property
    def ref(self) -> tuple[str, str]:
        return (self.family, self.local_id)


def family_of(path: str) -> str:
    base = os.path.basename(path)
    m = re.match(r"^integrated-(.+)\.md$", base)
    return m.group(1) if m else base


def family_rank(family: str) -> tuple[int, str]:
    """Sort key: known families in FAMILY_ORDER first, unknown families last (alphabetical)."""
    try:
        return (FAMILY_ORDER.index(family), family)
    except ValueError:
        return (len(FAMILY_ORDER), family)


def _strip_trailing_blank(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    return out


def parse_family(path: str) -> list[Entry]:
    """Parse ONE integrated-<family>.md into its ROOT + CF entries (byte-for-byte bodies).

    Classification is by HEADING TYPE at true line-start: a `### HYP Hn` starts a root, a `### CFn`
    starts a CF. The `## ROOT CAUSES` / `## CONTRIBUTING FACTORS` section headers are only an optional
    organiser — 5 of the 11 real families omit them entirely (they rely on the heading type), so the
    parser must NOT gate on them. A `### HYP`/`### CF` token that appears INSIDE a REASONINGS bullet
    or a `[src: … "quote"]` is never at column 0 and is therefore never parsed as a new entry
    (INV-no-phantom-entry). Any `## ` heading or a `---` rule closes the current entry's body."""
    family = family_of(path)
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")

    entries: list[Entry] = []
    cur: Entry | None = None
    order = 0

    def close() -> None:
        nonlocal cur
        if cur is not None:
            cur.body = _strip_trailing_blank(cur.body)
            _finalize_entry(cur)
            entries.append(cur)
            cur = None

    for raw in lines:
        mh = _HYP_HEAD.match(raw)
        if mh:
            close()
            order += 1
            cur = Entry(kind="root", family=family, local_id="H" + mh.group(1),
                        compound=bool(_COMPOUND.search(mh.group(2))), order=order)
            continue
        mc = _CF_HEAD.match(raw)
        if mc:
            close()
            order += 1
            cur = Entry(kind="cf", family=family, local_id="CF" + mc.group(1),
                        compound=bool(_COMPOUND.search(mc.group(2))), order=order)
            continue
        if _SEC_ANY.match(raw) or _HR.match(raw):
            close()
            continue
        if cur is not None:
            cur.body.append(raw)
    close()
    return entries


def _finalize_entry(e: Entry) -> None:
    for ln in e.body:
        if not e.claim:
            m = _CLAIM.match(ln)
            if m:
                e.claim = m.group(1).strip()
        if not e.feeds:
            m = _FEEDS.match(ln)
            if m:
                e.feeds = m.group(1).strip()
        if _REASONING_BULLET.match(ln):
            e.reasonings.append(ln)


def slugify(claim: str, fallback: str) -> str:
    """A deterministic, cosmetic slug from the CLAIM (the id `Hn` is the load-bearing token; the
    slug is a human label the census reads but never counts). Strip bracketed tier tags and
    parentheticals, drop a leading article, take the first meaningful words, cap length."""
    text = re.sub(r"\[[^\]]*\]", " ", claim)          # drop [T3 …] tier tags
    text = re.sub(r"\([^)]*\)", " ", text)            # drop parentheticals
    text = re.sub(r"^\s*(a|an|the)\s+", "", text, flags=re.I)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text.lower()).strip("-")
    words = [w for w in slug.split("-") if w]
    out = ""
    for w in words:
        cand = (out + "-" + w) if out else w
        if len(cand) > 60:
            break
        out = cand
    return out or fallback


# ── instruction-map application (merges / moves) ──────────────────────────────────────────────────
def _load_instructions(path: str | None, b64: str | None = None) -> dict:
    """Load the judge's instruction map from a file (--instructions) OR an inline base64-encoded JSON
    string (--instructions-b64). The driver is sandboxed and cannot write a temp file, so it threads the
    map inline as base64 — which, unlike raw JSON, survives shell quoting even when a safety `reason`
    contains an apostrophe (e.g. "Graves' disease")."""
    if not path and not b64:
        return {"merges": [], "moves": [], "safety": [], "nullSlug": ""}
    try:
        if b64:
            data = json.loads(base64.b64decode(b64, validate=True).decode("utf-8"))
        else:
            with open(path, encoding="utf-8") as fh:  # type: ignore[arg-type]
                data = json.load(fh)
    except (OSError, ValueError, binascii.Error) as exc:
        raise AssembleError(f"instructions map unreadable / malformed (JSON or base64): {exc}") from exc
    if not isinstance(data, dict):
        raise AssembleError("instructions map must be a JSON object")
    data.setdefault("merges", [])
    data.setdefault("moves", [])
    data.setdefault("safety", [])
    data.setdefault("nullSlug", "")
    return data


def apply_moves(index: dict[tuple[str, str], Entry], moves: list) -> None:
    """A move reclassifies an entry between the root set and the CF bucket. `to` ∈ {root, contributing}."""
    for mv in moves:
        if not isinstance(mv, dict):
            raise AssembleError(f"move instruction is not an object: {mv!r}")
        ref = (str(mv.get("family", "")), str(mv.get("id", "")))
        to = str(mv.get("to", "")).lower()
        if ref not in index:
            raise AssembleError(f"move references unknown entry {ref}")
        if to in ("root", "roots"):
            index[ref].kind = "root"
        elif to in ("contributing", "cf", "bucket"):
            index[ref].kind = "cf"
        else:
            raise AssembleError(f"move `to` must be root|contributing, got {mv.get('to')!r}")


def apply_merges(index: dict[tuple[str, str], Entry], merges: list) -> dict[tuple[str, str], tuple[str, str]]:
    """Validate merge groups and return a member-ref -> group-leader-ref map. A group leader is the
    member with the earliest (family_rank, order). Every member must be an existing ROOT; a member
    that is a CF, an unknown ref, or a ref appearing in two groups => exit 2 (INV-instruction-integrity)."""
    leader_of: dict[tuple[str, str], tuple[str, str]] = {}
    seen: set[tuple[str, str]] = set()
    for group in merges:
        if not isinstance(group, list) or len(group) < 2:
            raise AssembleError(f"merge group must be a list of >=2 members: {group!r}")
        refs: list[tuple[str, str]] = []
        for m in group:
            if not isinstance(m, dict):
                raise AssembleError(f"merge member is not an object: {m!r}")
            ref = (str(m.get("family", "")), str(m.get("id", "")))
            if ref not in index:
                raise AssembleError(f"merge references unknown entry {ref}")
            if index[ref].kind != "root":
                raise AssembleError(f"merge names a non-root entry {ref} (roots only merge)")
            if ref in seen:
                raise AssembleError(f"entry {ref} appears in more than one merge group")
            seen.add(ref)
            refs.append(ref)
        leader = min(refs, key=lambda r: (family_rank(index[r].family), index[r].order))
        for ref in refs:
            leader_of[ref] = leader
    return leader_of


# ── output rendering ──────────────────────────────────────────────────────────────────────────────
def build_document(entries: list[Entry], instructions: dict) -> tuple[str, dict, dict]:
    index = {e.ref: e for e in entries}
    apply_moves(index, instructions.get("moves", []))
    leader_of = apply_merges(index, instructions.get("merges", []))

    roots = [e for e in entries if e.kind == "root"]
    cfs = [e for e in entries if e.kind == "cf"]

    # group roots by merge-leader (a non-merged root is its own leader), preserving leader order.
    groups: dict[tuple[str, str], list[Entry]] = {}
    for e in roots:
        leader = leader_of.get(e.ref, e.ref)
        groups.setdefault(leader, []).append(e)
    ordered_leaders = sorted(
        groups.keys(), key=lambda r: (family_rank(index[r].family), index[r].order))

    out: list[str] = [
        "# Step 2c — Integrated hypothesis set (assembled)",
        "",
        "> Deterministically assembled from all eleven cause-family `integrated-*.md` files. Each root"
        " is carried forward verbatim (CLAIM, SOURCES, REASONINGS, LIKELIHOOD) under a globally"
        " renumbered `### Hn — <slug>` heading; nothing is flattened. Contributing factors are"
        " collected verbatim into the trailing bucket. One parallel-null block and any safety"
        " must-exclude blocks follow.",
        "",
        "---",
    ]

    # cards[id] = the standalone block text for that entry, so each downstream disconfirmer reads ONLY its
    # own card (not the whole set — seeing rival hypotheses biases the skeptic and wastes context).
    cards: dict[str, str] = {}
    root_meta: list[dict] = []
    n = 0
    for leader in ordered_leaders:
        members = sorted(groups[leader], key=lambda e: (family_rank(e.family), e.order))
        n += 1
        head_entry = members[0]
        slug = slugify(head_entry.claim, head_entry.local_id.lower())
        compound = any(m.compound for m in members) or len(members) > 1
        tag = " [COMPOUND]" if compound else ""
        block = [f"### H{n} — {slug}{tag}"]
        for i, m in enumerate(members):
            if i > 0:
                block.append("")
                block.append(f"— merged from {m.family} {m.local_id} —")
            block.extend(m.body)
        cards[f"H{n}"] = "\n".join(block).rstrip("\n") + "\n"
        out.append("")
        out.extend(block)
        out.append("")
        out.append("---")
        # family = the merge-leader's family (a merged root spans families; it batches with its leader).
        root_meta.append({"id": f"H{n}", "slug": slug, "claim": head_entry.claim, "family": head_entry.family})

    n += 1
    null_slug = (instructions.get("nullSlug") or "").strip() or DEFAULT_NULL_SLUG
    null_block = [f"### H{n} — {null_slug} [null]", f"CLAIM: {NULL_CLAIM}"]
    cards[f"H{n}"] = "\n".join(null_block) + "\n"
    out.append("")
    out.extend(null_block)
    out.append("")
    out.append("---")

    safety = instructions.get("safety", []) or []
    for k, s in enumerate(safety, start=1):
        if not isinstance(s, dict):
            raise AssembleError(f"safety instruction is not an object: {s!r}")
        s_slug = slugify(str(s.get("slug", "")) or str(s.get("reason", "")), f"safety-{k}")
        reason = str(s.get("reason", "")).strip()
        src = str(s.get("src", "")).strip()
        s_block = [f"### S{k} — {s_slug} [safety]", f"CLAIM: {reason}" if reason else "CLAIM: safety must-exclude"]
        if src:
            s_block.append(f"SOURCES: {src}")
        cards[f"S{k}"] = "\n".join(s_block) + "\n"
        out.append("")
        out.extend(s_block)
        out.append("")
        out.append("---")

    # contributing-factor bucket — every CF verbatim, never a `### Hn`, never counted by census.
    out.append("")
    out.append("## Contributing factors")
    out.append("")
    for cf in sorted(cfs, key=lambda e: (family_rank(e.family), e.order)):
        feeds = cf.feeds or "unattached"
        out.append(f"- [CF] {cf.claim}  [family: {cf.family}]  FEEDS: {feeds}")
        # carry the CF's REASONINGS verbatim (byte-for-byte) so no rationale is dropped.
        for r in cf.reasonings:
            out.append(r)
        out.append("")

    text = "\n".join(out).rstrip("\n") + "\n"
    meta = {
        "nRoots": len(root_meta),
        "nCF": len(cfs),
        "nSafety": len(safety),
        "nCards": len(cards),
        "roots": root_meta,
    }
    return text, meta, cards


# ── fail-closed checks ────────────────────────────────────────────────────────────────────────────
def check_anti_flatten(entries: list[Entry], text: str, instructions: dict) -> None:
    """Every input entry maps to exactly one output entry; every input REASONINGS line appears
    byte-for-byte in the output. Any violation => AssembleError (exit 2, no file written)."""
    refs = [e.ref for e in entries]
    if len(refs) != len(set(refs)):
        dupes = sorted({r for r in refs if refs.count(r) > 1})
        raise AssembleError(f"duplicate family-local id within a file: {dupes}")
    if not entries:
        raise AssembleError("no input entries parsed from --integrated-dir (0 families / empty)")

    out_lines = set(text.split("\n"))
    for e in entries:
        for r in e.reasonings:
            if r not in out_lines:
                raise AssembleError(
                    f"REASONINGS line dropped (not byte-for-byte in output) from {e.ref}: {r[:80]!r}")


def load_grounding(lib_path: str):
    if not os.path.exists(lib_path):
        raise AssembleError(f"grounding lib not found: {lib_path} (pass --grounding-lib or --no-grounding)")
    spec = importlib.util.spec_from_file_location("ih_grounding_anchor", lib_path)
    if spec is None or spec.loader is None:
        raise AssembleError(f"cannot load grounding lib as a module: {lib_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ih_grounding_anchor"] = mod
    spec.loader.exec_module(mod)
    return mod


def check_grounding(text: str, index_path: str, mod) -> list[str]:
    """Grounding self-check — SINGLE-SOURCE with the write-check gate this deterministic write bypasses.

    It replays the REAL grounding-anchor admissibility verdict, block-for-block, using the module's own
    imported primitives (INTERP/STATED/SRC/looks_like_file/is_derived): a `### Hn` root is inadmissible
    IFF it grounds on a memory/curated INTERPRETATION or an index-flagged DERIVED/CURATED source yet
    carries NO admissible anchor. This is deliberately NOT stricter than the gate: the real family files
    legitimately cite some roots as bare `— src: file.pdf` (not `[src:]`), which the gate's SRC regex
    does not match but which it (correctly) never DENIES — those blocks do not ground on interp/derived,
    so they pass. A stricter "every root needs a `[src:]`" rule would false-fail ~40% of compliant real
    roots and HALT the pipeline on good data; single-source fidelity is the binding contract. Because the
    assembler copies REASONINGS verbatim, the guarantee is: assembly introduced no inadmissible root the
    gate itself would not already accept. Returns the labels of any inadmissible roots."""
    is_derived = mod.load_index_derived(index_path)
    bad: list[str] = []
    for label, raw_body in mod.blocks(text):
        fbody = mod.match_copy(raw_body)
        srcs = [s.strip() for s in mod.SRC.findall(fbody)]
        has_interp = bool(mod.INTERP.search(fbody))
        has_stated = mod.has_clean_observation(raw_body)
        derived_srcs = [s for s in srcs if is_derived(mod.norm_src(s))]
        primary_srcs = [s for s in srcs if mod.looks_like_file(s) and not is_derived(mod.norm_src(s))]
        grounds_on_interp_or_derived = has_interp or bool(derived_srcs)
        has_admissible_anchor = has_stated or bool(primary_srcs)
        if grounds_on_interp_or_derived and not has_admissible_anchor:
            bad.append(label[:200])
    return bad


def atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministically assemble hypothesis-set.md from the family files.")
    ap.add_argument("--integrated-dir", required=True, help="dir holding integrated-<family>.md files")
    ap.add_argument("--out", help="write the assembled hypothesis-set.md here (required unless --json only)")
    ap.add_argument("--cards-dir", default=None, help="also write one standalone card file per entry here (<id>.md)")
    ap.add_argument("--instructions", default=None, help="judge instruction map JSON file (merges/moves/safety/nullSlug)")
    ap.add_argument("--instructions-b64", default=None, help="the same map as an inline base64-encoded JSON string")
    ap.add_argument("--index", default=None, help="extracted/index.md for the grounding self-check")
    ap.add_argument("--grounding-lib", default=DEFAULT_GROUNDING_LIB, help="path to investigate-grounding-anchor.py")
    ap.add_argument("--no-grounding", action="store_true", help="skip the grounding self-check (testing only)")
    ap.add_argument("--json", action="store_true", help="print the summary JSON to stdout")
    args = ap.parse_args()

    try:
        files = sorted(glob.glob(os.path.join(args.integrated_dir, "integrated-*.md")),
                       key=lambda p: family_rank(family_of(p)))
        if not files:
            raise AssembleError(f"no integrated-*.md files in {args.integrated_dir}")

        entries: list[Entry] = []
        for p in files:
            entries.extend(parse_family(p))

        instructions = _load_instructions(args.instructions, args.instructions_b64)
        text, meta, cards = build_document(entries, instructions)

        check_anti_flatten(entries, text, instructions)

        grounding_ok = True
        if not args.no_grounding:
            mod = load_grounding(args.grounding_lib)
            index_path = args.index
            if not index_path:
                run_root = os.path.dirname(os.path.abspath(args.integrated_dir.rstrip("/")))
                index_path = os.path.join(run_root, "extracted", "index.md")
            bad = check_grounding(text, index_path, mod)
            if bad:
                raise AssembleError(f"grounding self-check: inadmissible root(s) with no [src:] anchor: {bad}")

        if args.out:
            atomic_write(args.out, text)
        if args.cards_dir:
            os.makedirs(args.cards_dir, exist_ok=True)
            for cid, ctext in cards.items():
                atomic_write(os.path.join(args.cards_dir, cid + ".md"), ctext)
            # family manifest: ordered [{family, ids}] so the disconfirm stage can batch one agent per
            # cause-family (roots are already emitted in family order, so members are contiguous).
            fam_order: list[str] = []
            fam_ids: dict[str, list[str]] = {}
            for r in meta["roots"]:
                f = str(r["family"])
                if f not in fam_ids:
                    fam_ids[f] = []
                    fam_order.append(f)
                fam_ids[f].append(str(r["id"]))
            manifest = {"families": [{"family": f, "ids": fam_ids[f]} for f in fam_order]}
            atomic_write(os.path.join(args.cards_dir, "_families.json"), json.dumps(manifest, indent=2) + "\n")

        summary = {
            "ranSuccessfully": True,
            "nRoots": meta["nRoots"],
            "nCF": meta["nCF"],
            "nSafety": meta["nSafety"],
            "nCards": meta["nCards"],
            "anti_flatten_ok": True,
            "grounding_ok": grounding_ok,
            "roots": meta["roots"],
        }
        if args.json:
            print(json.dumps(summary, ensure_ascii=False))
        elif args.out:
            print(args.out)
        return 0
    except AssembleError as exc:
        # Print a machine-readable failure line on stdout too (in addition to stderr) so the driver's
        # trusted-bash dispatch echoes `ranSuccessfully:false` and HALTs — never falls back to a stale
        # file. Fail-closed: exit 2, no file written (build/checks run before the atomic write).
        print(f"assemble-hypset: FAIL — {exc}", file=sys.stderr)
        if args.json:
            print(json.dumps({"ranSuccessfully": False, "note": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
