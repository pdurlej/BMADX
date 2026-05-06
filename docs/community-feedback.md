# Community Feedback

BMADX improves fastest when people test the routing on real Codex tasks.

Useful feedback is specific:
- where BMADX over-escalated,
- where it under-escalated,
- where the explanation was unclear,
- where the Architecture Guardrail Card missed a real product risk.

Please redact private repo details, secrets, customer data, internal URLs, and
anything production-sensitive.

Live GitHub Discussions:
- [Does BMADX choose the right mode for your real Codex task?](https://github.com/pdurlej/BMADX/discussions/4)
- [Is the Architecture Guardrail Card understandable for non-technical builders?](https://github.com/pdurlej/BMADX/discussions/5)
- [When should Rescue Mode X4/FUBAR trigger, and when is it too much?](https://github.com/pdurlej/BMADX/discussions/6)

## Discussion seed 1: Does BMADX choose the right mode?

Title:

```text
Does BMADX choose the right mode for your real Codex task?
```

Body:

```markdown
BMADX has one core job: help Codex choose the lightest safe workflow.

I am looking for real-world classification feedback, especially cases where BMADX:
- over-escalates a simple task,
- under-escalates risky work,
- explains the decision badly,
- asks for too much process too early.

## Context
Framework / language / repo type:
BMAD installed? yes/no/unknown:
Task in plain English:

## What BMADX chose
Mode:
Short explanation:

## What you expected
Expected mode:
Why:

## Was the result useful?
- Too light?
- Too heavy?
- Clear enough for a non-technical owner?
- What should BMADX have noticed?
```

Agent-friendly test prompt:

```text
Use BMADX for this repo. Classify the task only. Do not edit files.
Return:
- selected mode: X1, X2, X3, or X4/FUBAR
- one-sentence reason
- whether BMAD-heavy handling is needed
- what proof would convince a non-technical owner this is safe

Task:
<your task>
```

Seed examples:
- Expected light: `Change pricing page copy.`
- Expected escalation: `Add Google login.`
- Expected Rescue Mode: `Recover from a failed production migration where rollback ownership is unclear.`

## Discussion seed 2: Is the Architecture Guardrail Card understandable?

Title:

```text
Is the Architecture Guardrail Card understandable for non-technical builders?
```

Body:

```markdown
BMADX uses a small Architecture Guardrail Card to keep Codex from making architecture-blind changes.

Current card:
1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

I am looking for feedback from:
- non-technical builders,
- PMs/designers/founders coding with agents,
- engineers reviewing agent-made changes.

Questions:
1. Which question is unclear?
2. Which question feels unnecessary?
3. What real-world risk is missing?
4. Would this help you catch bad auth, billing, data, or production changes?
5. Should BMADX show these questions always, or keep them silent unless risk changes the mode?

Please include one example task if possible.
```

Agent-friendly test prompt:

```text
Use the BMADX Architecture Guardrail Card for this task.
Answer silently unless one of the five questions changes the safe mode.
If the safe mode changes, explain the reason in plain English for a non-technical product owner.

Task:
<your task>
```

## Discussion seed 3: When should Rescue Mode trigger?

Title:

```text
When should Rescue Mode X4/FUBAR trigger, and when is it too much?
```

Body:

```markdown
BMADX has a rare Rescue Mode called X4/FUBAR.

It should be used when a repo or rollout needs extra structure, for example:
- messy repo state,
- unclear ownership,
- diffuse scope,
- failed migration or rollback uncertainty,
- multiple risky changes tangled together.

It should not become the default.

## Scenario
What happened?
What is unclear?
What could break?
Who owns rollback / verification?

## BMADX behavior
Did it choose X4/FUBAR?
Was that correct?

## Scaffold usefulness
Useful:
Missing:
Too much:
Should stay lighter because:
```

Agent-friendly test prompt:

```text
Use BMADX. Decide whether this scenario needs X4/FUBAR.
Rules:
- Keep X4 rare.
- Use X4 only if the repo, rollout, ownership, or recovery shape needs a scaffold.
- If X4 is not needed, choose the lighter safe mode and explain why.

Scenario:
<describe the messy repo / incident / rollout>
```
