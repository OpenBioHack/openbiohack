# Installing OpenBioHack

OpenBioHack runs **inside Claude Code, on your own machine, on your own data.** Nothing you put in leaves
your computer; the authors never see it. This guide gets you from zero to a first run.

> **Before anything else, read the safety notice at the top of `README.md`.** OpenBioHack is an educational
> and research tool — not a medical device, not medical advice, not a diagnosis. It speaks in possibilities
> to discuss with a qualified clinician, and every decision is yours and your clinician's.

---

## 1. Prerequisites

- **Claude Code** — the CLI from Anthropic. If you don't have it: follow the official guide at
  **claude.com/claude-code** (typically install Node.js, then `npm install -g @anthropic-ai/claude-code`,
  then run `claude` and sign in).
- **A paid Claude plan (Pro or Max).** The free tier can't run this — a full investigation does a lot of
  work under the hood (it reads all your data, runs many parallel lines of analysis, and cross-checks
  itself). On Pro a full run can be slow and may bump usage limits partway through; that's expected — you
  can run it in stages, or use Max for more headroom. Be patient with it; thoroughness is the point.

---

## 2. What's in this bundle

```
openbiohack/
├── CLAUDE.md             # the orchestrator — the front door + shared register/safety/epistemics
├── README.md             # what it is, why, and how to get the most from it
├── INSTALL.md            # this file
├── LICENSE / NOTICE / CITATION.cff
├── skills/               # the engine and its siblings
│   ├── investigate-health/      # the investigation engine (the spine)
│   ├── extract-health-data/     # turns raw records into structured, traceable data (incl. scripts/)
│   ├── research/                # first-principles mechanism/claim research
│   ├── research-practitioner/   # practitioner-grounded deep research
│   └── product-search/          # ingredient-by-ingredient product vetting
├── hooks/                # the enforcement layer (register + gated-write guards) + hooks.json
├── templates/            # starting files for your private, local memory
│   ├── symptom-log.md  experiment-log.md   # the ongoing N=1 layer
│   ├── medical-history.md  genetics.md  MEMORY.md  corrections.md
├── references/           # read by the system as it works
│   ├── optimization.md          # the optimize lens (4-layer ceiling + forward-trace)
│   ├── high-value-levers.md     # candidate levers catalogue (examples, not prescriptions)
│   └── n1-protocol.md           # how to run a careful self-experiment
└── build/                # how the bundle is regenerated from the canonical engine (maintainers)
```

---

## 3. Install the skills

Copy the five skill folders into your Claude Code skills directory.

- **For all your projects** (recommended): copy into `~/.claude/skills/`
- **For one project only**: copy into that project's `.claude/skills/`

```bash
# from inside the openbiohack/ folder:
cp -R skills/* ~/.claude/skills/
```

Verify they're picked up: start `claude` in any folder and the `/investigate-health`, `/extract-health-data`,
`/research`, `/research-practitioner`, and `/product-search` skills should be available.

### The enforcement hooks (important — this is what keeps the engine rigorous)

`investigate-health`'s discipline (the non-directive register reminder on every turn, the gated-write checks,
the "read the document, don't synthesise from a summary" guard) is enforced by the scripts in `hooks/`.
Installed as a **Claude Code plugin**, `hooks/hooks.json` registers them automatically (paths resolve via
`${CLAUDE_PLUGIN_ROOT}`) — nothing to do. If you instead copied the skills in manually, the hooks won't be
active until you register them: merge the entries from `hooks/hooks.json` into your project's
`.claude/settings.json` (pointing the commands at wherever you put `hooks/`). The engine still *runs* without
them, but you lose the guardrails — so for real use, install the plugin (or register the hooks).

---

## 4. Set up a private project folder for yourself

Make a folder that will hold *your* data and *your* memory. This folder is yours alone — keep it off any
shared drive if you like.

```bash
mkdir -p ~/my-health/data ~/my-health/memory
cd ~/my-health
```

1. **Drop the orchestrator in.** Copy `CLAUDE.md` (and the `references/` folder) into your project root so
   Claude Code auto-loads the orchestrator when you work here:
   ```bash
   cp /path/to/openbiohack/CLAUDE.md .
   cp -R /path/to/openbiohack/references .
   ```
2. **Seed your memory** with the templates (the system will fill these in as you go — you don't edit them
   by hand unless you want to):
   ```bash
   cp /path/to/openbiohack/templates/* memory/
   ```
3. **Put your data in `data/`.** The more, the better the result — see *What to bring* in `README.md`. In
   short: blood tests over time; your raw genetic data file (not a third-party interpretation); a thorough,
   honest description of symptoms and history; any imaging, functional tests, or clinician letters.

---

## 5. Run it

From your project folder, start `claude`, then:

- **To investigate something** (stuck / unwell, or a mix): run **`/investigate-health`** and follow the
  conversation. Expect real back-and-forth — the more carefully you describe and observe, the further it
  goes.
- **To optimize** (you feel okay, want to feel great): say so at the start; the orchestrator picks the
  optimize lens and still runs the same engine, forward-traced. (See `references/optimization.md`.)
- **Either way, keep your logs.** Update `memory/symptom-log.md` and `memory/experiment-log.md` as you go
  (templates included, method in `references/n1-protocol.md`). Bring them back into the conversation and the
  investigation sharpens over time — this is the part that makes it better than a one-shot report.

The orchestrator (`CLAUDE.md`) is the front door; for any real analysis it hands off to the
`investigate-health` engine. You don't have to think about the routing — just describe what's going on.

---

## 6. A note for builders

The eval harness lives in `skills/investigate-health/eval/`. New regression/eval cases that catch a real
failure are the single most valuable contribution — see `README.md` ("please help us make it better"). A
proper Claude Code **plugin/marketplace** package and a portable single-file prompt are planned packaging
formats; this bundle is the source-of-truth repo behind them.
