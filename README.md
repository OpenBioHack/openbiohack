<!-- DRAFT README for the open-source OpenBioHack repo. Register-checked: educational / non-directive. -->

# OpenBioHack

**A first-principles thinking partner for hard, ambiguous health challenges & optimisation** Free and open source. Runs inside your own Claude Code, on your own data.

> ⚠️ **Read this first — what this is and isn't.**
> OpenBioHack is an **educational and research tool. It is not a medical device, and nothing it produces is medical advice or a diagnosis.** It works in *possibilities*, not verdicts — candidate explanations and low-risk things you could *consider and discuss with a qualified clinician*. It does not tell you (or your doctor) what to do. If something might be urgent, it will tell you to seek medical care, and you always should. **You and your clinician make every decision.**

---

## Why this exists

Whether you're up against a stubborn problem no one's been able to crack, or you're simply trying to push past "normal" toward your best, you tend to hit the same wall: many regular experts look through one narrow lens. Practitioners are — understandably — specialised and time-pressed; each sees their own slice. For anything that spans several systems at once, doesn't fit a standard label, or goes beyond ordinary care into deliberate self-optimisation and biohacking, there's rarely anyone whose job it is to take the *whole* picture, hold many possibilities open at the same time, and reason it through with you, patiently, from first principles.

So the person with the most at stake — and the most to gain — usually ends up having to become their own investigator. That's genuinely hard to do well, and it's exactly what this is built for. It comes out of my own ~7-year journey: it began with a serious health crisis I largely had to work out myself, and over time became an ongoing practice of life enhancement.

## Where it came from

I built this out of my own ~7+ year journey. It started with a life-threatening flesh-eating bacterial infection and a long, intense course of antibiotic chemotherapy that saved my life — and left a long tail of side effects I then had to understand and work through. No single practitioner had the time or the cross-system view to untangle it for me, so I had to learn the biology myself: enough to reason from first principles, form careful hypotheses, and run small, *safe* experiments on myself until I slowly got to much greater health and aliveness than before.

OpenBioHack is that approach **proceduralised** — built not to hand you answers but to **empower you to do this yourself**: it works backward from what you're actually experiencing (or forward from where you want to get to), traces the biology, holds the possibilities open, and proposes low-risk, reversible experiments you can run and observe — showing its reasoning at every step so you genuinely learn how your own body works. 
*(This is my personal experience, shared as context — not a claim about what will happen for you, and not medical advice.)*

## What it does

Given your own health data, it runs a careful investigation and gives you back, in plain language:

- **Possible root-causes** — the processes that could be producing what you're experiencing, held open as a set rather than collapsed to one answer.
- **Low-risk, reversible things you could consider trying** — ranked by safety, by how many things they might address at once, and by how quickly you'd see a signal — as options to discuss with your clinician.
- **A symptom-relief track** you could run in parallel while the deeper questions are still open.
- **Confirmatory tests worth asking your clinician for** — the cheap, specific ones that would actually narrow things down.
- **An honest map of it's uncertainties** and what would resolve it.

Everything is framed as a possibility to explore with your clinician — never an instruction.

## It's built to make *you* more capable

This is the part that matters most. **No practitioner you ever hire — however good — will have as much interest in, or time for, your specific situation as you do.** OpenBioHack isn't just trying to hand you answers. At every stage it shows you the *reasoning* and the *biology*, so you actually learn how your body might work and why each possibility is on the table. The goal is for you to come out of it more able to take charge of your own health — to keep investigating, keep observing, and keep asking sharper questions long after the first run.

It walks you through a process to begin with. But the deeper aim is that you **learn from each stage** — and at the end it hands you a set of questions you can keep asking the AI to keep sharpening its thinking over time (see *Keeping it sharp* below).

---

## A note on the journey — hope, patience, and "everything is figure‑out‑able"

If you're here at all, you're very likely already a high‑agency person — someone who takes charge of their own life. And you may also feel there's further to go. So a few honest words for the road:

**If you're here for a hard health challenge:** these journeys can be slow, and they test us. The most important things we can bring are **hope, persistence, and patience** — the willingness to keep iterating, keep experimenting, and keep observing, even when progress is quiet. Hold onto the conviction that **everything is figure‑out‑able.** That belief is not naive; it's what carries us through the difficult stretches, and in my experience it tends to be true more often than the difficulty makes it feel.

**If you're here to optimize:** what becomes *possible* in a body can far exceed what most of us would ever imagine. After surviving chemo and returning to health, I got to keep upgrading my body and mind: Have not injured myself in 5 years; reduced instances of illness (like colds or other infections) by 95%; have stable high energy and focus all day to the point I can work 12 hr days without tiredness;  body sensitivity to the point of feeling individual vertebrae in my spine, or the shape of my beating heart; can regulate my body temperature enough to hike near‑freezing mountains in just shorts; can perceive waves of vibration through my body at will, generating an incredible sense of aliveness. 
And this is just some of the experience — there is far, far more. The whole journey has brought me an enormous amount of *aliveness*. *(These are my own experiences, built up carefully over years — shared as what became possible for me, not as a promise, a protocol, or medical advice. Bodies differ; build slowly, and don't copy anything risky without your own care and research.)*

---

## Getting started

**You'll need Claude Code and a paid Claude plan.** If you're not on Claude Code yet, it's quick to set up — and worth it; this won't run without it.

1. **Get Claude Code.** Follow the official install guide at **claude.com/claude-code** (typically: install Node.js, then `npm install -g @anthropic-ai/claude-code`, then run `claude` and sign in). A **paid plan is required** (Pro or Max) — the free tier can't run this.
2. **Install the OpenBioHack skills** into your project (instructions in `INSTALL.md`).
3. **Put your data in a folder** — see *What to bring* below.
4. **Run `/investigate-health`** and follow the conversation.
5. **Keep a symptom log and an experiment log** as you go (templates included) — this is how it gets better over time.

### A note on time, tokens, and plans
This does a *lot* of work under the hood — it reads all your data, runs many parallel lines of analysis, researches mechanisms, and cross-checks itself. That means it can **use a lot of tokens and take a while**, especially if you have a lot of data to share. On the **Pro** (lowest paid) tier a full run can be slow and may hit usage limits partway through — that's expected; you can run it in stages, or use **Max** for more headroom and speed. Be patient with it: thoroughness is the point.

### What to bring (the more, the better the result)
The quality of what you get out depends heavily on what you put in, and on **how well you've observed your own situation.** To get a genuinely useful result, it helps a lot to have:

- **Blood tests** — as many as you have, over time (trends matter more than a single snapshot).
- **Genetic / DNA data if you have it** — the **raw data file** (e.g. from 23andMe/Ancestry), not a third-party interpretation.
- **A thorough, honest description of your symptoms and history** — when things started, what was happening in your life then, what makes them better or worse, everything you've already tried and exactly how you responded. Expect real **back-and-forth**: the more carefully you can describe and observe, the further this goes.
- Any imaging, functional tests (gut, hormone panels), clinician letters, or records you have.

If you don't have much data yet, that's okay — it will still help, and one of its outputs is *which cheap tests would tell you the most next*.

---

## This isn't one-and-done — the ongoing part

Real understanding of a body comes from **tracking over time**, not a single report. OpenBioHack includes two simple ongoing logs (templates in `templates/`):

- **Symptom log** — a quick daily/weekly record (0–10 scales, sleep, digestion, energy, anything notable). Brief is fine; *consistency* is what makes it useful.
- **Experiment log** — each thing you try, treated as a small, careful **N=1 experiment**: a baseline first, one change at a time, what you predicted, what you observed (including confounders), and what it taught you about *your* biology.

Bring these back into the conversation and the investigation sharpens — possibilities rise and fall on real evidence from your own life, which is exactly how you learn what's actually going on.

## Keeping it sharp — questions to keep asking

The investigation gets better the more you push on it. Some questions worth asking it again and again over time:

- *"What's an affordable test or observation that would best separate the possibilities still on the table?"*
- *"What would have to be true for your current leading explanation to be wrong — and what would disprove it?"*
- *"My last experiment showed X. Which possibilities does that raise, which does it lower, and by how much?"*
- *"Are you anchoring on one explanation? Argue the strongest case for a different one."*
- *"Explain the biology here from first principles and without jargon so I actually understand it — where is this reasoning weakest?"*
- *"Given everything so far, what's the most upstream thing I could safely influence, and what would I watch to know if it's helping?"*
- *"What am I not observing or tracking that would help you think more clearly about this?"*

---

## This is open source — please help us make it better

OpenBioHack is free and open. If you have skills in this space — biology, medicine, data, biohacking, prompt/skill engineering — **we'd genuinely love your help improving the procedure**, and we'd love to hear how it went for you. Contributions and feedback are what make it sharper for everyone.

### Specifically, the feedback that helps us most
*(Please redact/anonymize before sharing anything — never include identifying information. You're never required to share your data; this is entirely opt-in.)*

- **What you and your clinician decided to pursue, and what happened** — which candidate pathway, and how it played out.
- **Results of any safe experiments you tried** — what it was, how long, what you observed (the metric you tracked *and* confounders), and whether it seemed to help, not help, or was unclear. The honest "didn't work" cases are as valuable as the wins.
- **Where it was right or wrong** — anything a clinician later found that the investigation *missed*, or anything it over-weighted that turned out not to matter.
- **Any "see a doctor now" flag** that turned out to genuinely matter — or that was a false alarm.
- **Where the tone or language felt off** — too confident, too vague, anything that read as telling you what to do, or anything that scared you unnecessarily.
- **Friction with your data** — what was hard to extract, upload, or get it to read; formats that broke.
- **Cost and time on your plan** — which tier, how long a run took, whether you hit usage limits, how much data you had.
- **Whether the "keep asking" questions actually sharpened it** over repeated sessions.
- **For builders:** concrete improvements to the procedure, prompts, rubrics, or new test cases that expose a gap.

Open an issue, start a discussion, or send a pull request. New regression/eval cases that catch a real failure are a super valuable contribution.

---

## Resources from my own journey

- **A personal log of what I actually tried** — the specific experiments, what worked and what didn't, including the psychological side of the journey. *Strong caveat: this is my own n=1, specific to my body and situation. It may not be reliable, useful, or safe for yours. It is a log, not advice and not a protocol — discuss anything you're curious about with your clinician.* → **[SculptYourSelf — my personal log of what worked](https://www.notion.so/greater-human-org/SculptYourSelf-e1df5551a2c54b5e93c26077f1e7e4d3)**
- **The psychological side matters as much as the biology.** On a long health journey, the mind carries a heavy load. The method I found most powerful for that is **Internal Family Systems (IFS)** — which is also what I now build: **[greaterhuman.ai](https://greaterhuman.ai)**, a tool for self-guided personal growth using the IFS method.

---

## Safety & limits (please read)

- Educational/research only. **Not medical advice, not a diagnosis, not a medical device.**
- It speaks in possibilities and should never tell you or your clinician what to do. Every option is something to **discuss with a qualified clinician** before acting.
- **Like any AI, it can be confidently wrong — so don't follow it blindly.** Treat everything it produces as a starting point to *check*, not an answer to act on. **Verify the claims that matter yourself** — read the primary sources and studies it points to, more than once if it's important — and take them to your clinician. You'd apply that caution to any general AI model; apply it here too. (Every document it generates carries this reminder at the bottom, on purpose.)
- It is designed around **low-risk, reversible** options and will flag anything that needs medical evaluation — but it cannot see everything. **If something might be serious or urgent, seek medical care now.**
- **You remain in charge of every decision.** This is a thinking tool to make *you* more capable — not something to hand your judgment to.
- Your data stays with you — it runs locally in your Claude Code; the authors receive nothing unless you choose to send feedback.

## Credits & license

Created by **Teo Embers**, who also builds **[greaterhuman.ai](https://greaterhuman.ai)**, a tool for self-guided personal growth using the Internal Family Systems method — because the psychological side of a long health journey matters too. Licensed **Apache-2.0** (see `LICENSE` / `NOTICE`). Built on the Claude Code skill framework.

If this helps you, the best thanks is to **share what you learned** so the next person's investigation starts further along.
