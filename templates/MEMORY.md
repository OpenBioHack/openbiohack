# OpenBioHack — memory index

> **This file is an INDEX, not a store.** It is loaded into context at the start of every session, so it
> has to stay small and scannable. The rule: **MEMORY.md holds only (a) the handful of things that must be
> seen every single session, and (b) one-line pointers to the deeper files where the real detail lives.**
> Anything longer than a line or two belongs in a topic file — link to it from here; don't paste it here.
>
> **How to structure memory (follow this):**
> - **Keep MEMORY.md under ~200 lines.** If it's growing past that, the detail has leaked in — move it out
>   to a topic file and leave a one-line pointer.
> - **One concern, one file.** Each substantial thread (a working investigation, a genetics analysis, a
>   recurring reaction, a research deep-dive) gets its own file. MEMORY.md gets one line that says what's in
>   it and points to it — ideally with a section/line hint so the reader is one lookup away from the detail.
> - **The index carries enough detail to navigate, not to conclude.** A good pointer line says *what* the
>   file establishes and *why it matters*, so you know whether to open it — e.g. "genetics.md — verified
>   methylation + iron variants; check before recommending B-vitamin forms or iron." It does not restate the
>   findings.
> - **Self-reminders are the exception** — those few critical "never forget / never repeat" facts live
>   inline here (below), because the cost of missing one is high and they must be seen unprompted.
> - **Maintain it.** Update at the end of every session. When a file is archived or a thread closes, prune
>   its line. The index is only useful if it reflects the current state.

## SELF-REMINDERS (read these FIRST every session)

> The single most valuable block in the file. Every time the assistant is corrected on something — a
> contraindication, a misread result, a "don't suggest X again" — add a one-line reminder here so the
> mistake can't recur. Keep each to one line; if it needs more, put the detail in a topic file and leave the
> headline here. **These are illustrative of the *form* — replace them with this person's actual reminders:**
>
> - `[GENETICS] <gene/variant> verified against raw data — <what it changes about supplement form/dose>.`
> - `[REACTION] <substance/form> caused <reaction> — avoid / use <alternative> instead.`
> - `[HARD NO] <thing the person will never use> — don't propose it or workarounds for it.`
> - `[DELIVERY] <vehicle, e.g. liposomal> is a problem in this person's situation — prefer <alternative>.`
> - `[PROCESS] Use /product-search before giving any product URL; verify ingredients, don't trust brand.`

(Add reminders here as the relationship develops. The list grows; entries are rarely removed.)

---

## Current status ([date])
- Primary focus / lens: [one sentence — investigate / optimize / check-in, and on what]
- Current phase: [intake / analysis / experimenting / maintenance]
- Current experiment: [what's being trialed, or "none"] → see `experiment-log.md`

## File map
| File | What's in it | Maintained by |
|------|--------------|---------------|
| MEMORY.md (this file) | This index + self-reminders | end of every session |
| medical-history.md | Full intake: symptoms, timeline, treatments, diet, supplements, goals | as new data arrives |
| genetics.md | Verified genetic findings (raw-data-verified only) | when genetics are analyzed |
| symptom-log.md | Daily/weekly symptom tracking | the person + check-in lens |
| experiment-log.md | N=1 experiments: protocol, prediction, results, learning | per experiment |
| corrections.md | Mistakes made — do NOT repeat these | whenever something is found wrong |
| *(engine artifacts)* | Live mechanism map + hypothesis set live in the investigation run, not here | the `/investigate-health` engine |
| verified-products.md / brand-database.md / product-search-log.md | Caches + audit trail | `/product-search` |
| *(topic files)* | One per deep thread — link each from here with a one-line pointer | as threads open |

## Current supplements / interventions
| Time | What | Daily dose | What it's aimed at |
|------|------|-----------|--------------------|
| [AM/PM/with food] | [name (brand)] | [dose] | [target] |

## Key genetics (if available — RAW DATA VERIFIED ONLY) → detail in `genetics.md`
| Category | SNP(s) | Impact |
|----------|--------|--------|
| [e.g. methylation] | [e.g. MTHFR C677T CT] | [e.g. prefer methylfolate] |

## Key blood work (if available) → detail in `medical-history.md`
| Marker | Value | Date | Trend | Notes |
|--------|-------|------|-------|-------|

## Active next steps (prioritized — keep short)
1. [ ] [the single most valuable next action]
2. [ ] [second]
3. [ ] [third]

## Topic files (one line each — what it establishes + why it matters)
- `[filename].md` — [what it establishes] — [why/when to open it]

## Corrections log (one-liners; full detail in `corrections.md`)
| Date | What was wrong | Correct information |
|------|----------------|---------------------|
