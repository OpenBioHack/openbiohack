#!/usr/bin/env python3
"""investigate-offer-render.py — the offering's presentation layer.

Turns the plain-Markdown `offering.md` into deliverables a person can actually read and navigate:

  * a styled, standalone **HTML** page with a clickable Contents index (always produced — stdlib only);
  * a **.docx** whose Contents entries are real internal hyperlinks and whose headings are Word
    Heading styles, so Google Docs imports a clickable table of contents, an outline sidebar, and
    collapsible sections (produced only when `pandoc` is on PATH — best-effort, never fatal).

Why a presentation layer at all: `offering.md` is faithful but bare; pasted into a doc its `##`/`**`
show literally and it has no navigation. This step is deterministic (no agent), so it is a safe,
standard final touch after the emitter writes `offering.md`.

Why the TOC is built from links, not pandoc's `--toc`: pandoc's `--toc` emits a Word TOC *field*,
which Google Docs imports as a static, un-clickable block. Explicit `[title](#id)` links against
`{#id}` headings become `w:hyperlink w:anchor` bookmarks Google Docs imports as working links.

The writers' raw heading levels are inconsistent (framing at ##, the possibilities and levers at #,
some peers ## vs #, template field-labels as their own headings). `--normalise` (default) reassigns
levels by ROLE so both the HTML and the docx get a sane, navigable hierarchy.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

# A heading whose text starts with one of these is a top-level landmark (Heading 1).
LANDMARKS = (
    "Three top hypotheses",
    "How each hypothesis",
    "A possibility that",
    "The other thirty-two",
    "Things you could consider trying",
    "Things that could be measured first",
    "Contents",
)

# Template field-labels a couple of section writers emitted as their own headings — within-item
# detail, never landmarks, so they sit a level below the item and out of a level-2 Contents index.
FIELD_LABELS = {
    "where it acts", "what it is", "type", "how it could be run",
    "what the response would tell us", "already tried", "what it would show",
    "the program", "read-out window", "decision branch", "already-tried note",
}


def slugify(text: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "section"
    slug, n = base, 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def norm_level(text: str, orig: int, normalise: bool) -> int:
    if not normalise:
        return orig
    if any(text.startswith(p) for p in LANDMARKS):
        return 1
    if text.strip().lower() in FIELD_LABELS:
        return 3
    if orig >= 3:
        return 3
    return 2


def inline(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    return t


def render_html(md: str, normalise: bool) -> tuple[str, list[tuple[int, str, str]]]:
    lines = md.split("\n")
    out: list[str] = []
    toc: list[tuple[int, str, str]] = []
    used: set[str] = set()
    para: list[str] = []
    bullets: list[str] = []

    def flush_para() -> None:
        if para:
            out.append("<p>" + inline(" ".join(para).strip()) + "</p>")
            para.clear()

    def flush_bullets() -> None:
        if bullets:
            out.append("<ul>")
            out.extend("<li>" + inline(b) + "</li>" for b in bullets)
            out.append("</ul>")
            bullets.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_para()
            flush_bullets()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            flush_bullets()
            txt = m.group(2).strip()
            lvl = norm_level(txt, len(m.group(1)), normalise)
            slug = slugify(re.sub(r"\*+", "", txt), used)
            toc.append((lvl, txt, slug))
            out.append(f'<h{lvl} id="{slug}">' + inline(txt) + f"</h{lvl}>")
            continue
        b = re.match(r"^\s*[-*]\s+(.*)$", line)
        if b:
            flush_para()
            bullets.append(b.group(1).strip())
            continue
        if re.match(r"^\s*---+\s*$", line):
            flush_para()
            flush_bullets()
            out.append("<hr>")
            continue
        para.append(line.strip())
    flush_para()
    flush_bullets()
    return "\n".join(out), toc


def toc_html(toc: list[tuple[int, str, str]], maxlevel: int) -> str:
    items = [t for t in toc if t[0] <= maxlevel and not t[1].startswith("Contents")]
    if not items:
        return ""
    rows = ['<h1 id="contents">Contents</h1>', '<nav class="toc">']
    for lvl, txt, slug in items:
        rows.append(f'<div class="toc-l{lvl}"><a href="#{slug}">{inline(txt)}</a></div>')
    rows.append("</nav>")
    rows.append("<hr>")
    return "\n".join(rows)


def normalise_md(md: str, toc_maxlevel: int = 2) -> str:
    """Heading-normalised Markdown with {#id} anchors and a hyperlinked Contents, for pandoc."""
    used: set[str] = set()
    body: list[str] = []
    toc: list[tuple[int, str, str]] = []
    prev_blank = True
    for raw in md.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)$", raw.rstrip())
        if m:
            txt = m.group(2).strip()
            lvl = norm_level(txt, len(m.group(1)), True)
            slug = slugify(re.sub(r"\*+", "", txt), used)
            if not prev_blank:
                body.append("")
            body.append("#" * lvl + " " + txt + f" {{#{slug}}}")
            body.append("")
            prev_blank = True
            if lvl <= toc_maxlevel:
                toc.append((lvl, txt, slug))
            continue
        body.append(raw)
        prev_blank = not raw.strip()
    contents = ["# Contents {#contents}", ""]
    for lvl, txt, slug in toc:
        contents.append("  " * (lvl - 1) + f"- [{txt}](#{slug})")
    contents += ["", "---", ""]
    return "\n".join(contents + body)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.6;
         color: #1a1a1a; max-width: 46rem; margin: 3rem auto; padding: 0 1.5rem; }}
  h1 {{ font-size: 1.5rem; margin: 2.8rem 0 0.9rem; line-height: 1.3; }}
  h2 {{ font-size: 1.2rem; margin: 2.1rem 0 0.8rem; line-height: 1.3; }}
  h3 {{ font-size: 1.05rem; margin: 1.7rem 0 0.7rem; }}
  h1:first-child, h2:first-child {{ margin-top: 0; }}
  p {{ margin: 0 0 1rem; }}
  ul {{ margin: 0 0 1.2rem; padding-left: 1.4rem; }}
  li {{ margin: 0 0 0.4rem; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 2.4rem 0; }}
  strong {{ font-weight: 700; }}
  nav.toc {{ margin: 0 0 1rem; }}
  nav.toc a {{ color: #1a4a7a; text-decoration: none; }}
  nav.toc a:hover {{ text-decoration: underline; }}
  .toc-l1 {{ margin: 0.5rem 0 0.2rem; font-weight: 700; }}
  .toc-l2 {{ margin: 0.15rem 0 0.15rem 1.4rem; }}
  .toc-l3 {{ margin: 0.1rem 0 0.1rem 2.8rem; font-size: 0.95rem; }}
</style>
</head>
<body>
{toc}
{body}
</body>
</html>
"""


def write_html(md: str, out_path: str, title: str, normalise: bool, toc_maxlevel: int) -> None:
    body, toc = render_html(md, normalise)
    page = PAGE.format(title=html.escape(title), toc=toc_html(toc, toc_maxlevel), body=body)
    _atomic_write(out_path, page)


def write_docx(md: str, out_path: str, title: str) -> bool:
    """Best-effort .docx via pandoc. Returns True on success, False if pandoc is unavailable/failed."""
    if not shutil.which("pandoc"):
        print("investigate-offer-render: pandoc not found — skipping .docx (HTML still produced)")
        return False
    nm = normalise_md(md)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
        tf.write(nm)
        tmp_md = tf.name
    try:
        subprocess.run(
            ["pandoc", tmp_md, "-f", "markdown", "-o", out_path, "--standalone", "-M", f"title={title}"],
            check=True, capture_output=True, text=True)
        print(f"investigate-offer-render: wrote {out_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"investigate-offer-render: pandoc failed ({e.returncode}); .docx skipped: {e.stderr.strip()[:200]}",
              file=sys.stderr)
        return False
    finally:
        os.unlink(tmp_md)


def _atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out-html", required=True)
    ap.add_argument("--out-docx", default="")
    ap.add_argument("--title", default="Your offering — what we are looking at")
    ap.add_argument("--toc-maxlevel", type=int, default=2)
    ap.add_argument("--no-normalise", action="store_true")
    args = ap.parse_args()
    if not os.path.isfile(args.inp):
        print(f"investigate-offer-render: no input at {args.inp}", file=sys.stderr)
        return 2
    with open(args.inp, encoding="utf-8") as fh:
        md = fh.read()
    write_html(md, args.out_html, args.title, not args.no_normalise, args.toc_maxlevel)
    print(f"investigate-offer-render: wrote {args.out_html}")
    if args.out_docx:
        write_docx(md, args.out_docx, args.title)
    return 0  # HTML is the guaranteed deliverable; a missing pandoc is not a failure.


if __name__ == "__main__":
    sys.exit(main())
