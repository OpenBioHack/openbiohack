# The timeline's source contract

One document. Nothing in it is written by a model. This file declares what may become a block,
what each block's heading means, how a passage is cited, and the six tests a candidate conflict
must pass before it reaches the person.

It carries **no subject data**: the rules below are path shapes and vocabulary, never the
person's words, never their records. The corpus and the document live outside version control.

---

## 1. Only declared primary sources become blocks

A corpus folder is a working directory, not a source folder. Model-written analysis, prior
investigations, audit reports and the timeline itself all sit in it, and byte-identity would
certify any of them as "verbatim" if they were allowed in. So inclusion is declared, not
inferred from "is it a file".

A file becomes eligible only if it matches an `include` glob, matches no `exclude` glob, and is
valid UTF-8 text. Everything else is enumerated in the build ledger with a reason. `build.py`
fails if any file in the corpus is neither included nor excluded for a stated reason.

```json
{
  "include": [
    "_text/*.txt",
    "**/*.md",
    "**/*.txt"
  ],
  "exclude": [
    "_build/**",
    "02-imaging/**",
    "timeline.md",
    "timeline-*.md",
    "_text/*.pos.json",
    "_text/conversion-report.json",
    "**/_build/**",
    "**/__pycache__/**"
  ],
  "exclude_reasons": {
    "_build/**": "derived \u2014 build scripts",
    "*imaging*/**": "binary \u2014 DICOM study data and viewer software, no extractable text",
    "timeline.md": "the document itself",
    "timeline-*.md": "the document itself, and its dated copies",
    "_text/*.pos.json": "derived \u2014 word-geometry sidecar emitted by the converter",
    "_text/conversion-report.json": "derived \u2014 the converter's own run report",
    "**/_build/**": "derived \u2014 build scripts",
    "**/__pycache__/**": "derived \u2014 compiled python"
  }
}
```

Anything specific to ONE corpus — a person's folder layout, the titles of analyses sitting in
it — goes in `timeline-source.local.md` beside this file, which is gitignored and merged in at
load time (lists extend, maps update). Naming them here would publish the shape of somebody's
working directory in an open-source repo.

An `exclude` entry naming a single file also carries a `sha256` in `pinned_shas` where the point
is *this file*, not *this path shape* — so replacing a model-written file with a genuine record
at the same path is caught rather than silently kept out.

```json
{
  "pinned_shas": {}
}
```

### 1b. What kind of source it is

A source becomes blocks in one of three ways. The kind is declared by path shape, so a corpus
nobody has seen before still builds: anything not named below is a `document`, which is the safe
default — one block, the whole record, nothing decided.

| kind | how it becomes blocks | what decides the boundaries |
|---|---|---|
| `document` | one block: the whole file after the converter's own header | nothing — there is nothing to decide |
| `bundle` | split at a repeated record boundary in the file itself | a declared regular expression |
| `narrative` | split into passages | an agent, which emits **boundaries only** — the first few words of each new passage, copied — and never a word of prose |

A `narrative` boundary is resolved to an exact byte offset by matching it in the source. If it
appears twice, or not at all, the build stops and names it. It is never approximately matched.

```json
{
  "kinds": {
    "narrative": [
      "*VERBATIM*",
      "*history*",
      "*narrative*",
      "*interview*",
      "*personal-history*"
    ],
    "bundle": {
      "_text/clinic-letters__*.txt": "(?=Clinician viewed )",
      "_text/*panel-summary*.txt": "(?====== PAGE )"
    }
  }
}
```

`pinned_shas` is empty at the initial build: every named exclusion above is excluded because of
what the path *is* (a prompt, a compilation, a converter sidecar), and the build ledger records
the sha of each one so a later change is visible in a diff of the ledger.

---

## 2. Identifiers

A block is `TL-Snnnn`, assigned once when the block is created and never reassigned. It is not
derived from the block's position and not derived from its date: a position-encoded identifier
would have to be repointed by every insertion, and a date-encoded one would change whenever the
dating changed, which is exactly the moment a citation most needs to stay put.

A sentence unit inside a block is `TL-Snnnn-uNN`, numbered from `u01` in reading order and
frozen when the block is created. Units tile the block body exactly, so no character sits
outside a unit.

Anywhere in the pipeline, a passage is referred to by writing `[[TL-S0042]]` or
`[[TL-S0042-u07]]`. An agent writes the identifier; `cite.py` substitutes the exact words. An
unknown identifier is a hard error, never an empty string and never silently stale.

---

## 3. Heading

```
## <date> · <ID> · <≤3 tags> · <the block's own opening words>
```

The date is rendered from the stored value and its stored precision:

| precision | stored     | rendered      |
|-----------|------------|---------------|
| `day`     | 2019-07-11 | `2019-07-11`  |
| `month`   | 2023-06    | `2023-06`     |
| `year`    | 2015       | `~2015`       |
| `span`    | 2019-2021  | `~2019–2021`  |
| `unknown` | —          | `undated`     |

A year-precision placement has no code path that renders it as a specific day.

The opening words are copied from the block's own first characters and cut at a word boundary.
They are not a title and nobody writes them.

---

## 4. Tag vocabulary — closed

At most three per block, from this list only. A tag names *which part of the record this is*,
never what it means.

`childhood` · `travel-exposure` · `diet` · `antibiotics` · `medication` · `supplement` ·
`gut` · `urology` · `dermatology` · `respiratory` · `cardiac` · `hepatic` · `renal` ·
`endocrine` · `neuro` · `musculoskeletal` · `dental` · `ophthalmic` · `infection` ·
`imaging` · `lab` · `genetics` · `procedure` · `clinic-letter` · `symptom-onset` ·
`symptom-change` · `treatment-response` · `family-history` · `sleep` · `stress` ·
`exercise` · `alcohol` · `self-report` · `undated`

---

## 5. Which field is the event date, per document type

Read the wrong field and the whole placement moves. These are stated per document type because
a clinic letter's `Clinic Date` is the date of the appointment, and the letter may have been
dictated days later.

| document type          | event date field                    | not the event date |
|------------------------|-------------------------------------|--------------------|
| clinic / outpatient letter | `Clinic Date`                   | dictation date, typing date, the date it was scanned |
| discharge summary      | date of discharge                   | date the summary was produced |
| imaging report         | date of the study                   | date of the report, date of an addendum |
| imaging addendum       | date of the addendum                | date of the original study |
| lab result             | date the sample was taken           | date the result was released |
| stool / breath test    | date the sample was collected       | report date |
| ECG / procedure report | date performed                      | report date |
| the person's own account | the date the described event happened | the date they said it |
| the person's own notes | the date the described event happened | the date the file was saved |

Two letters carrying the same clinic date and different dictation dates are two records. Both
are placed; neither is discarded as a duplicate.

---

## 6. The six tests a candidate conflict must pass

A candidate is dismissed the moment it fails one, and the dismissal records which one. The
default answer is *not a conflict*.

1. **Both sides are actually asserted.** Each side is a verbatim span of a named block, not an
   inference from one.
2. **They are about the same thing.** The same symptom, the same substance, the same episode —
   not two things that share a word.
3. **They are about the same time.** Two statements about different periods are a history, not
   a contradiction.
4. **They cannot both be true.** Change over time, partial recall and hedging are not conflict.
   A hedged statement conflicts with nothing.
5. **The person is the one who can resolve it.** Never ask them to corroborate a recorded
   objective finding — a lab value, an imaging report, a measurement.
6. **Resolving it would change something.** If both answers lead to the same next step, it is
   not worth their time.

---

## 7. What is never done

- Nothing is summarised, paraphrased, shortened or re-worded. Every character in a block is
  copied from a source by script.
- The document is built once. After that, no tool rewrites it: every change is an insert, a
  move, or an annotation. `build.py` is the only script with a whole-file write path.
- A move is a move. A relocated block keeps its identifier, its text, its provenance and its
  sha; it is never deleted and re-created.
- Nothing about the corpus or the document enters version control. Backups are dated file
  copies.
