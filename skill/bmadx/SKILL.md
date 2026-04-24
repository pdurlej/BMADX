---
name: bmadx
description: Use for choosing the lightest safe Codex workflow on top of BMAD, especially when the user wants less manual process selection, clearer verification, or a rescue mode for a messy project.
---

# BMADX

BMADX is a BMAD-first tactical overlay for Codex.

It does not replace BMAD and it must not create a second process source of
truth. It adds a practical decision layer inspired by selected OMX ideas:
routing, verify-before-done, capability-based subagent usage, and an
`X4/FUBAR` scaffold bundle for high-entropy projects.

Since `v0.2.4`, BMADX is tuned for Codex on GPT-5.5. Treat stronger models as
better executors, not as permission to skip boundaries: BMADX remains a
boundary and verification layer, not a substitute for BMAD process ownership.

Non-negotiable rule:
- `BMAD > BMADX`

## Use this skill when

- the user wants the right work mode chosen for them instead of a random one-shot,
- the user wants BMAD with lighter day-to-day routing discipline,
- the task needs to be classified into `X1`, `X2`, `X3`, or `X4`,
- the task may need a rescue/scaffold bundle on top of BMAD,
- the user talks about a messy project, unclear scope, escalation, planning, or ownership structure.

## Do not use this skill when

- the user already knows they want a normal BMAD workflow and does not need the overlay,
- the task is straightforward execution inside an already-established BMAD story,
- the user is only asking about BMAD version/sync health; use `$bmad-method-codex` instead.

## Dependency gate

Since `v0.2.2`, BMADX follows the contract:
- classify first,
- gate second.

The user usually should not choose a gear manually. BMADX should classify the
task first, then check the compact gate for the chosen gear.

### Preferred routing flow

1. Classify the task using the embedded skill contract.
2. Open reference docs only if the task is ambiguous or boundary-shaped.
3. Run the compact gate for the chosen gear:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --gear X1 --compact
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --gear X2 --compact
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --gear X3 --compact
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --gear X4 --compact
```

4. Read the compact report in this order:
- if `classification_allowed = false`, stop and report the local BMADX problem,
- if `classification_allowed = true`, keep the correct gear classification,
- for `X1/X2`, treat `warning` as soft guidance; missing cache does not block execution,
- for `X3/X4`, treat `execution_allowed = false` as a hard stop for execution,
- if `cache_used = true`, `X1/X2` can continue from the last healthy BMAD snapshot without a live check.

5. Keep the full JSON check for smoke/debug only:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --json
```

### Gate rules

- `X1/X2`: fast path through the compact gate; unhealthy BMAD without cache yields a warning, not a block
- `X3/X4`: full live gate; unhealthy BMAD blocks execution, not classification
- cached healthy BMAD only softens `X1/X2`
- blocked `X3/X4` remediation must point to exactly:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmad-method-codex/scripts/sync_bmad_method.py" check --json
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmad-method-codex/scripts/sync_bmad_method.py" sync
```

## Obvious `X1/X2` fast path

For obvious `X1` and `X2`, do not open reference docs. `SKILL.md` should be
enough.

On GPT-5.5, keep obvious `X1/X2` even quieter: classify, run the compact gate,
and answer in the short contract without explaining the machinery unless the
gate warns or blocks.

Treat the task as an obvious happy path if:
- `X1`: one tiny local change, typo/copy/small fix, no contract/process risk
- `X2`: bounded local work, short plan, a few checks, but no BMAD artifact needed
- the prompt does not contain major ambiguity or process-escalation signals
- the compact gate is green or soft-warning only

Open `gearbox.md`, `trigger-matrix.md`, or `verify-discipline.md` only if:
- `X1/X2/X3` signals conflict,
- the user asks for a plan but it is unclear whether this is still `X2` or full BMAD,
- the prompt mentions BMAD story ownership, new process artifacts, rollout, schema/API/auth/perf risk,
- the compact gate is red and the escalation needs explanation.

Do not narrate that you are “using the skill”, “reading refs”, or “checking the gate” unless that explanation is needed.

## Automatic gearbox

Classify first. Only then recommend the work mode.

- `X1` — One-shot
- `X2` — Regular
- `X3` — Complex (BMAD)
- `X4` — Rescue Mode (`X4/FUBAR`, BMAD+)

Details:
- [gearbox.md](references/gearbox.md)
- [trigger-matrix.md](references/trigger-matrix.md)

Selection rule:
- if the user explicitly asks for a plan or the task is highly ambiguous, ask clarifying questions before committing to a gear
- if the intent is clear, choose the gear and justify it briefly
- after classification, check only the compact gate for the chosen gear
- for obvious `X1/X2`, do not open refs; answer directly in the short format
- if the task depends on BMAD artifacts, `X3/X4` must stay BMAD-first
- if the gear is `X3/X4` but execution is blocked, keep the correct classification and report the execution block separately

## Response contract

### `X1` obvious happy path

Format:
- `Choice: ...`
- `Why: ...`
- `Next step: ...`

Rules:
- maximum `5` lines
- maximum `650` characters
- one sentence for why, one sentence for the next step
- do not mention the gate if it is green
- mention the gate only for a warning or block

### `X2` obvious happy path

Format:
- `Choice: ...`
- `Why: ...` as one short sentence
- `Plan:`
- `1. ...`
- `2. ...`
- `Verify:`
- `1. ...`
- `2. ...`

Rules:
- maximum `12` lines
- maximum `1000` characters
- no blank lines between sections
- prefer exactly `2` plan lines and `2` verify lines unless the user explicitly asks for more detail
- keep the plan concrete but short
- keep verify to the strongest checks only
- keep each plan/verify line tight and operational; do not narrate
- keep `Why:` under roughly `160` characters
- keep each plan/verify line under roughly `120` characters
- do not mention the compact gate if it is green
- do not add `Next step:` in the obvious happy path unless the user explicitly asks for it
- do not end with “if you want, I can...” unless the user asked for the next step

### `X3/X4`

Do not compress these into the same limits. For `X3/X4`, correctness matters more than terseness:
- correct classification
- explicit execution gate state
- BMAD-first behavior
- stronger models do not bypass BMAD artifacts, BMAD ownership, or the hard gate

For planning-only or benchmark prompts that say not to implement, do not inline
full X4 bundle files, long templates, or draft artifacts. State the correct
Rescue Mode entry path, name the bundle surfaces, and defer rendering/drafting
until execution is explicitly requested and the hard gate allows it.

## Gear guide

### X1 — One-shot

Use for tiny local changes with a low blast radius.

- no new BMAD artifacts
- 1–2 final checks
- quick execution plus proof

### X2 — Regular

Use for small-to-medium bounded work that needs a short plan but not full BMAD.

- short plan
- execution
- verify-before-done
- optional `/review` for a non-trivial diff

### X3 — Complex (BMAD)

Use when the work should enter a full BMAD flow.

- BMAD defines phases, workflow maps, and artifacts
- `project-context.md` and BMAD artifacts stay the source of truth
- BMADX only adds routing, review, and verification discipline

### X4 — Rescue Mode (`X4/FUBAR`, BMAD+)

Use when the project is broad, risky, messy, or needs a scaffold bundle on top
of BMAD.

`X4` is not the default mode. It is the ace in the sleeve.
GPT-5.5 does not make `X4` normal; use Rescue Mode only when the repo, rollout,
or ownership problem is genuinely rescue-shaped.

In `X4`:
- choose the correct BMAD flow
- start with `/bmad-bmm-create-prd`, then `/bmad-bmm-create-architecture`
- treat `_bmad-output/project-context.md` as durable technical memory
- generate the scaffold bundle from templates
- clarify ownership, verification, and rollout
- keep the decision hierarchy simple: BMAD > BMADX

Bundle spec:
- [fubar-bundle-spec.md](references/fubar-bundle-spec.md)

Render the bundle:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/render_fubar_bundle.py" \
  --project-name "Project name" \
  --project-path "$PWD" \
  --output-dir /tmp/bmadx-fubar
```

## Verify before done

BMADX enforces verify-before-done in every gear.

- `X1`: minimum 1–2 checks or the strongest available oracle
- `X2`: plan + checks + optional `/review`
- `X3/X4`: checks must align with BMAD criteria and the current `project-context.md`

Details:
- [verify-discipline.md](references/verify-discipline.md)

## Subagents

BMADX promotes capability-based subagent usage.

- smaller/faster models: bounded discovery, repo mapping, diff review support, verification support
- main model: decisions, synthesis, integration, final responsibility
- avoid hardcoding one model or one vendor

Details:
- [subagent-policy.md](references/subagent-policy.md)

## BMADX vs BMAD boundaries

BMAD remains the owner of:
- phases
- workflow maps
- artifacts
- process vocabulary

BMADX remains the owner of:
- gear choice
- operational discipline
- verification gate
- scaffold bundle for `X4`

Boundaries and ownership:
- [bmadx-vs-bmad.md](references/bmadx-vs-bmad.md)

## Resources

- `scripts/sync_bmadx.py` — health check, drift check, healthy BMAD cache, soft/hard dependency gate
- `scripts/test_sync_bmadx.py` — smoke/unit tests for sync
- `scripts/render_fubar_bundle.py` — generator for the `X4/FUBAR` scaffold bundle
- `assets/templates/` — templates and snippets for the bundle
- `references/` — gearbox, trigger matrix, boundaries, verify, subagents
