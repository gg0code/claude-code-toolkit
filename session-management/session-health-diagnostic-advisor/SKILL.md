---
name: session-health-diagnostic-advisor
description: Project-agnostic session health monitor for Claude Code. Tracks token consumption, cost, and context bloat across a long working session and tells the user when to run /cost, /compact, or /clear. Use this skill whenever the user starts a multi-hour or multi-phase Claude Code build, says they want to "monitor my session," "watch token usage," "track spend," "stay within budget," or asks Claude to advise on when to compact or clear. Trigger it proactively at the start of any project work that spans multiple phases (data → models → frontend, spec → API → tests, research → draft → revise, etc.), even if the user does not explicitly ask for monitoring — the diagnostic value is highest when started early.
---

# Session Health Diagnostic Advisor

A reusable, project-agnostic diagnostic layer for any Claude Code session that spans more than 30–60 minutes or more than one logical phase of work. Its job is to make the user's session spend, token usage, and context health visible — and to prompt the right action at the right time.

This skill never runs slash commands on its own. Slash commands like `/cost`, `/compact`, and `/clear` are user-initiated in Claude Code. What this skill does is **tell the user when to run them, read the output back, and convert numbers into decisions.**

---

## What this skill does

1. **Establishes a session baseline** when activated — captures the project's phases, the user's budget thresholds, and the user's preferred checkpoint cadence.
2. **Prompts the user at logical breakpoints** to run `/cost` and report the output.
3. **Interprets each `/cost` reading** against thresholds and against the previous reading — flagging trends, not just absolutes.
4. **Recommends an action** at each checkpoint: keep going, `/compact`, `/clear`, or stop.
5. **Maintains a running checkpoint log** so the user can see the cost trajectory across the session.
6. **Produces a session summary** at the end — total spend, tokens, phase-by-phase breakdown, and one lesson to carry forward.

---

## Step 1 — Activation interview

When this skill first triggers in a session, ask the user a short setup interview. Keep it tight — three questions, no more. The goal is to calibrate thresholds and checkpoint logic to *this* project, not to interrogate.

Ask in one message:

> Before we start, three quick questions so I can monitor session health properly:
>
> 1. **What are the major phases of this work?** (e.g., "data gen → model training → frontend → tests" — just a rough list)
> 2. **What's your session budget?** Either a dollar figure ("under $15") or "I don't care, just warn me if it gets weird."
> 3. **How often should I check in?** Options: *light* (only at phase boundaries), *normal* (every 45–60 min or phase change), *aggressive* (every 20–30 min).

If the user says "use defaults," apply these:

| Setting | Default |
|---|---|
| Phases | "I'll detect them as we go" |
| Budget | Warn at $10, urge `/compact` at $20, urge `/clear` at $40 |
| Cadence | Normal (every ~45 min or phase change) |

Record the answers in the session log (see Step 5).

---

## Step 2 — Threshold rubric

Use this rubric to interpret `/cost` output. These thresholds are **defaults — override them with whatever the user set in Step 1.**

### Dollar-based (default)

| Spend so far | Status | Recommendation |
|---|---|---|
| Under $5 | 🟢 Healthy | Keep going. |
| $5 – $10 | 🟡 Watch | Note the per-turn rate. If climbing fast, prepare to `/compact` at next breakpoint. |
| $10 – $20 | 🟠 Compact | Run `/compact` at the next natural pause. History is likely bloating. |
| $20 – $40 | 🔴 Clear or stop | Consider `/clear` and restarting with a fresh context, or wrap the session. |
| Over $40 | ⛔ Stop | Wrap the session, log lessons, start fresh next time. |

### Token-based (alternative when cost isn't shown)

| Tokens used | Status |
|---|---|
| Under 50k | 🟢 |
| 50k – 100k | 🟡 |
| 100k – 150k | 🟠 (compact recommended) |
| 150k – 200k | 🔴 (clear recommended) |
| Over 200k | ⛔ (context exhaustion imminent) |

### Trend signal (often more important than absolutes)

Compare the latest reading to the previous one:

- **Cost-per-turn rising sharply** between checkpoints → history is bloating → `/compact` is the right move *even if* the absolute total is still in the green.
- **Input tokens growing faster than output tokens** → Claude is re-reading large context every turn → `/compact` will help.
- **Spend roughly linear with active work done** → healthy, no action needed.

---

## Step 3 — When to prompt for a checkpoint

Don't ask for `/cost` randomly. Use these triggers:

1. **Phase boundary detected** — the user finishes a logical chunk ("data generation done," "models trained," "first template built"). This is the highest-value moment for a checkpoint because it aligns with a natural decision point.
2. **Time-based** — roughly aligned with the cadence chosen in Step 1 (light / normal / aggressive). Don't watch the clock obsessively; estimate from the volume of work done since the last check.
3. **Pre-large-task** — before any task likely to generate a lot of output (build all the templates, refactor a whole module, write extensive documentation).
4. **Self-noticed bloat** — if Claude notices it has been re-reading the same large files repeatedly, or the conversation has accumulated many long code blocks, flag it even if no other trigger fires.

When prompting, keep it short and non-naggy:

> 📊 **Session-health checkpoint**: just finished [phase / ~45 min of work / about to start templates]. Run `/cost` and paste the output back — I'll interpret.

Never prompt more often than every ~20 min in *aggressive* mode, every ~45 min in *normal* mode, every phase boundary in *light* mode. Checkpoints themselves cost tokens; over-monitoring defeats the purpose.

---

## Step 4 — Interpreting a `/cost` reading

When the user pastes `/cost` output, do this in order:

1. **Extract the numbers**: total spend, total tokens, input vs output split, session duration if shown.
2. **Compute the delta** from the previous checkpoint (if any): spend since last check, time since last check, cost-per-minute trend.
3. **Map to rubric**: which threshold band? Trend rising, stable, or falling per-turn?
4. **Recommend** with a clear single action: keep going / `/compact` / `/clear` / stop. Give one sentence of reasoning, not a paragraph.
5. **Log it** to the running checkpoint table (Step 5).

### Example interpretation

> **Checkpoint 3** — $6.40 spent, 142k tokens, ~2h 10m session.
> Since checkpoint 2 (40 min ago, $3.80), you've added $2.60 in 40 min — per-minute spend has roughly doubled vs. the first hour. Input tokens climbed 60k, output only 18k, so the conversation history is doing most of the work.
> **Recommendation: run `/compact` before starting the analytics page.** It'll trim re-reads of the model-training history you no longer need.

---

## Step 5 — Running checkpoint log

Maintain a lightweight log throughout the session. Update it at every checkpoint. Keep it inline in the conversation as a small table, so the user can see the trajectory at a glance.

Format:

```
SESSION HEALTH LOG — [project name if known]
Budget: [from Step 1]   Cadence: [from Step 1]

| #  | Time     | Phase        | Spend    | Tokens  | Δ Spend | Action taken          |
|----|----------|--------------|----------|---------|---------|------------------------|
| 1  | 00:32    | data gen     | $1.20    | 48k     | —       | keep going             |
| 2  | 01:30    | models       | $3.80    | 102k    | +$2.60  | keep going             |
| 3  | 02:10    | pre-frontend | $6.40    | 142k    | +$2.60  | recommend /compact     |
| 4  | 02:18    | post-compact | $6.55    | 38k     | +$0.15  | resume — context fresh |
```

Notice that after `/compact`, total tokens drop sharply (history was compressed) but total spend keeps climbing (it's cumulative for the session). That's expected — call it out the first time so the user understands.

---

## Step 6 — End-of-session summary

When the user signals they're wrapping up ("I'm done," "let's stop here," "good for today"), produce a session summary. Keep it crisp:

```
SESSION SUMMARY — [project / topic]
Duration:        [Xh Ym]
Total spend:     [$X.XX]
Total tokens:    [Xk]
Checkpoints:     [N]
/compact calls:  [N]
/clear calls:    [N]

Phase breakdown:
  - data gen        ~$1.20    (efficient)
  - model training  ~$2.60    (normal)
  - frontend        ~$3.20    (output-heavy — expected)

One lesson for next session:
  [single sentence — e.g., "Frontend phase was 2× more expensive than data gen
  because of HTML output volume — consider building templates in shorter
  sub-sessions next time."]
```

The "one lesson" is the most valuable output — it's how the user's intuition about Claude Code cost calibration improves across projects. Always include it. One sentence, project-specific, actionable.

---

## Edge cases and judgment calls

- **User refuses the interview**: skip it, use defaults, proceed silently. Don't argue.
- **Very short session (< 30 min)**: this skill is overhead. If you detect the user is doing a quick one-off task, suppress checkpoints and just offer a single end-of-task `/cost` if relevant.
- **User pastes `/cost` output without being asked**: interpret it, log it, treat it as a checkpoint. Don't lecture about cadence.
- **`/cost` output format varies by Claude Code version**: extract whatever numbers are present (spend, tokens, or both). Don't fail if one is missing.
- **Multi-day work on one project**: each new session resets the meter. If the user mentions they're "continuing yesterday's work," note that the session log starts fresh — past totals belong in `CLAUDE.md` or a separate project ledger, not in this session's log.
- **User says "stop monitoring"**: stop. Don't prompt again unless they re-invoke the skill. Confirm with one line: "Session-health monitoring paused. Re-invoke any time."

---

## What this skill deliberately does NOT do

- Does not run `/cost`, `/compact`, or `/clear` itself — those are user-initiated.
- Does not estimate cost predictively (e.g., "this task will cost $3"). Estimates are unreliable; observations are reliable. Wait for the next `/cost` reading.
- Does not modify project files, code, or `CLAUDE.md`. Its scope is the session itself.
- Does not enforce thresholds. It recommends; the user decides.
- Does not lecture. One-sentence rationales, never paragraphs about token economics.

---

## Mental model to keep

`/cost` is the fuel gauge. `/compact` improves fuel economy by shrinking re-read context. `/clear` is a full refuel-and-restart. This skill is the dashboard light that tells the user which one to act on, and when.
