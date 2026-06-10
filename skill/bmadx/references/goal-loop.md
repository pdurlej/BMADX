# Goal and Loop Discipline

This reference is for longer Codex work that needs a persistent definition of
done or a bounded repair loop. It must stay small: BMADX remains a routing and
verification layer, not a runtime platform.

## Boundary

Goal and loop discipline does not change the gear:

- `X1/X2`: usually no goal and no loop.
- `X3`: use a goal when the work spans multiple steps and needs explicit proof.
- `X4`: use a goal and loop only when Rescue Mode execution needs repeated
  evidence-driven passes.

`/goal` belongs to Codex. BMADX only decides whether the task shape benefits
from using it and what completion criteria should be attached.

## Goal Contract

Recommend a goal when:

- the work may span several turns or compactions,
- the definition of done can be made measurable,
- proof criteria are easy to lose mid-thread,
- the user asks Codex to keep working until the task is actually done.

Do not recommend a goal for obvious one-shot work, copy edits, tiny doc changes,
or classification-only benchmark answers.

Goal text should include:

1. outcome,
2. proof,
3. stop condition,
4. hard constraints or non-goals.

Contract line:

```text
Goal: yes — use `/goal` because the work needs a persistent definition of done.
```

Use `Goal: no` when the work is bounded enough for the normal gear contract.

## Loop Contract

Use a loop only when feedback from one pass should drive the next pass.

The loop shape is:

1. review,
2. repair,
3. validate,
4. carry forward only the remaining delta.

Stop when:

- validation passes,
- the maximum attempt count is reached,
- the remaining delta stops shrinking,
- a BMADX/BMAD hard stop appears,
- human review is needed.

Default attempt cap:

- `X3`: max 2 passes unless the user asked for more.
- `X4`: max 3 passes for real rescue execution.

Contract line:

```text
Loop: yes — max 3 review/repair/validate passes; stop on pass, stale delta, hard stop, or human review.
```

Use `Loop: no` when one verify pass is enough.

## Forbidden Drift

Goal and loop discipline must not introduce:

- hooks,
- MCP setup,
- plugins,
- subagents,
- worker lanes,
- dispatch commands,
- model-lane choices,
- persistent run IDs,
- runtime state,
- a second plan store,
- auto-merge or auto-deploy behavior.

BMAD remains the process source of truth. BMADX may export a goal-ready
objective or a bounded repair loop contract, but it must not become the loop
executor.
