#!/usr/bin/env python3
"""Read a round-1 answer back and name the sections that came out thin.

Round 1 is one pass over seven things. Asking seven separate times got seven separate starts;
asking once and then checking gets one continuous account plus a short, specific follow-up.

What this does NOT do is judge the answer. It counts: how much of the transcript touches each
section, using each section's own vocabulary, and reports the sections that barely register. A
section can be thin because there is nothing to say — that is a real answer, and the follow-up
asks whether that is the case rather than assuming it is not.

    interview_coverage.py --transcript t.md --out coverage.md --prompts followups/
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402

# Each section's own vocabulary. Deliberately plain words, because the person speaks plainly and
# a transcript of speech does not contain clinical terms.
SECTIONS: list[tuple[str, str, list[str]]] = [
    ("whole-story", "The whole story, from wherever it starts",
     ["start", "began", "first", "then", "after that", "since", "years", "story", "happened"]),
    ("decades", "Your life, decade by decade — where you lived, what you ate, what you were doing",
     ["lived", "moved", "school", "university", "job", "work", "city", "country", "house",
      "diet", "ate", "eating", "food", "water"]),
    ("before", "Before any of it started — childhood, family, what normal was",
     ["child", "childhood", "kid", "born", "birth", "mother", "mum", "mom", "father", "dad",
      "parents", "brother", "sister", "family", "grew up"]),
    ("body-sweep", "Your body, one part at a time",
     ["skin", "eyes", "mouth", "teeth", "chest", "breathing", "lungs", "heart", "stomach",
      "bowel", "gut", "urin", "genital", "joint", "muscle", "nerve", "sleep", "energy", "mood",
      "head", "feet", "legs", "hands"]),
    ("tried", "Everything you've tried",
     ["took", "taking", "tried", "started", "stopped", "course", "dose", "supplement",
      "antibiotic", "protocol", "treatment", "diet", "fast", "surgery", "procedure"]),
    ("no-difference", "What made no difference",
     ["no difference", "nothing", "didn't help", "did not help", "no effect", "didn't do",
      "no change", "unchanged", "same"]),
    ("theory", "What you think is going on",
     ["i think", "i suspect", "my sense", "my theory", "i reckon", "my guess", "i believe",
      "feels like", "seems like"]),
]

THIN = 3          # fewer than this many distinct cue hits and the section is thin
SPARSE_WORDS = 120  # ...or fewer than this many words of nearby text


def score(text: str) -> list[dict[str, object]]:
    low = text.lower()
    words = low.split()
    out = []
    for key, title, cues in SECTIONS:
        hits = {c: len(re.findall(re.escape(c), low)) for c in cues}
        distinct = sum(1 for v in hits.values() if v)
        total = sum(hits.values())
        # Words within 40 tokens of any cue — a rough measure of how much was actually said.
        near = 0
        positions = [i for i, w in enumerate(words)
                     if any(w.strip(".,;:!?").startswith(c.split()[0]) for c in cues)]
        if positions:
            covered: set[int] = set()
            for p in positions:
                covered.update(range(max(0, p - 20), min(len(words), p + 20)))
            near = len(covered)
        out.append({"key": key, "title": title, "distinct_cues": distinct, "hits": total,
                    "words_near": near,
                    "thin": distinct < THIN or near < SPARSE_WORDS,
                    "top": sorted((c for c, v in hits.items() if v), key=lambda c: -hits[c])[:6]})
    return out


FOLLOWUP = """You covered most of it, and I'd rather not make you repeat yourself.

One area I didn't get much on: **{title}**.

{quoted}

Is there more there, or is that genuinely all there is? Either answer is useful — "that's all"
is a real answer and I'll record it as one."""

FOLLOWUP_EMPTY = """You covered most of it, and I'd rather not make you repeat yourself.

One area that didn't come up at all: **{title}**.

Is there anything there? If there genuinely isn't, say so and I'll record that — a blank because
there's nothing is different from a blank because we ran out of time."""


def quoted_bits(text: str, cues: list[str], limit: int = 3) -> str:
    """What they already said about this section, copied — never paraphrased back at them."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    low = [s.lower() for s in sentences]
    picked = [s.strip() for s, l in zip(sentences, low)
              if any(c in l for c in cues) and len(s.split()) > 6][:limit]
    return "\n".join(f"> {s}" for s in picked)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True, type=Path, nargs="+",
                    help="the verbatim round-1 answer, one or more files")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--prompts", type=Path, help="where to write a follow-up per thin section")
    args = ap.parse_args()

    text = "\n\n".join(p.read_text(encoding="utf-8") for p in args.transcript)
    rows = score(text)
    thin = [r for r in rows if r["thin"]]

    lines = ["# Round-1 coverage — what came out thin", "",
             f"{len(text.split())} words across {len(args.transcript)} file(s). "
             f"**{len(rows) - len(thin)} of {len(rows)} sections covered.**", "",
             "A thin section is not a failure — it may be thin because there is nothing there. "
             "The follow-up asks which it is, and quotes back what was already said so nobody is "
             "asked to repeat themselves.", "",
             "| section | cues | hits | words nearby | |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['title']} | {r['distinct_cues']} | {r['hits']} | {r['words_near']} | "
                     f"{'**thin**' if r['thin'] else 'covered'} |")
    if thin:
        lines += ["", "## Ask about these, and only these", ""]
        lines += [f"- **{r['title']}**" for r in thin]
    else:
        lines += ["", "All seven covered. There is no round-2 coverage question to ask.", ""]
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.prompts and thin:
        args.prompts.mkdir(parents=True, exist_ok=True)
        by_key = {k: c for k, _, c in SECTIONS}
        for r in thin:
            q = quoted_bits(text, by_key[str(r["key"])])
            body = (FOLLOWUP.format(title=r["title"], quoted=q) if q
                    else FOLLOWUP_EMPTY.format(title=r["title"]))
            (args.prompts / f"{r['key']}.md").write_text(body + "\n", encoding="utf-8")

    print(f"{len(rows) - len(thin)}/{len(rows)} sections covered; thin: "
          + (", ".join(str(r["key"]) for r in thin) or "none"))
    print(f"report: {args.out}")
    if args.prompts and thin:
        print(f"follow-ups: {args.prompts} ({len(thin)} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
