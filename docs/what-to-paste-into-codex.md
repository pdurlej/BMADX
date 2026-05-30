# What to Paste into Codex

Use these as starter prompts after BMADX is installed.

## Generic normal change

```text
Use BMADX for this repo. Pick the lightest safe mode. Keep it lightweight unless BMAD is truly needed.
Use the Architecture Guardrail Card silently unless a risk changes the safe mode.
Suggest the thinking budget only if it matters for this task.

My task:
<describe the change in plain English>

What I care about:
speed, clarity, and not overengineering it
```

## Non-technical product builder

```text
Use BMADX for this repo. Pick the lightest safe mode and keep the architecture understandable.
If the task touches auth, billing, data, permissions, secrets, or production config, escalate to BMAD instead of treating it as a quick task.
Recommend the thinking budget for this run, but do not change global Codex config.

My task:
I understand the product problem, but I do not want to manually decide the technical approach.
Help me turn this into a safe implementation path:
<describe the outcome in plain English>

What I care about:
clear tradeoffs, a small first step, and verification I can understand
```

## Founder MVP change

```text
Use BMADX for this repo. Pick the lightest safe mode.

My task:
Add a pricing page and connect the CTA buttons to the waitlist form.

What I care about:
shipping quickly, keeping the scope small, and not breaking the existing landing page
```

## Designer landing page tweak

```text
Use BMADX for this repo. Pick the lightest safe mode.

My task:
Improve the hero section, tighten the copy, and make the call-to-action more obvious.

What I care about:
clarity, visual polish, and keeping the diff easy to review
```

## PM-style bounded feature change

```text
Use BMADX for this repo. Pick the lightest safe mode.
If this changes data, contracts, permissions, or ownership, ask before implementing and use BMAD if needed.

My task:
Add support for a new status field across the API handler, validator, and UI label.

What I care about:
correctness, a short plan, and clear verification
```

## Bug fix

```text
Use BMADX for this repo. Pick the lightest safe mode.

My task:
Fix the empty-state bug in the dashboard where the CTA disappears after refresh.

What I care about:
a small fix, strong verification, and no unnecessary refactor
```

## Rescue a messy repo

```text
Use BMADX for this repo. Pick the lightest safe mode, but escalate if this needs rescue-level structure.

My task:
This project is messy, ownership is unclear, and we need a safe way to move forward.

What I care about:
clear next steps, explicit ownership, rollout safety, and a scaffold if needed
```

## Red-zone task

```text
Use BMADX for this repo. This might be red-zone work, so do not use X1.
Classify it safely, use BMAD if needed, and explain the proof in plain English.

My task:
<auth / billing / permissions / migration / data deletion / secrets / production config change>

What I care about:
not breaking users, data, security, or rollout safety
```

## Working from an existing BMAD story

```text
Use BMADX for this repo. Pick the lightest safe mode, but keep BMAD as the source of truth.

My task:
Implement the existing BMAD story for onboarding analytics and stay aligned with the process artifacts.

What I care about:
process alignment, correctness, and a clean verify path
```
