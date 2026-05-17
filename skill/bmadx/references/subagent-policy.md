# Capability-Based Subagent Policy

BMADX promotes capability-based subagent usage rather than a single hardcoded
model name.

## Rule

- use smaller and faster subagents for bounded, read-heavy, parallel support,
- optimize operator time-to-value: the main model should keep moving while a
  helper checks an independent side question,
- keep the main model responsible for decisions, integration, and final accountability.

## Good uses

- repo mapping and discovery,
- diff review support,
- verification support,
- comparing two implementation options,
- reading long artifacts without polluting the main context,
- running a quick read-only check while the main model prepares the patch,
- finding existing patterns before a bounded `X2` implementation,
- checking whether a tiny change is repeated in multiple places.

## Bad uses

- delegating the whole problem without synthesis,
- spawning subagents for every simple `X1`,
- parallelizing work that is actually sequentially dependent,
- using subagents to hide indecision,
- waiting on a helper when the main model can already make the safe patch,
- assigning overlapping write scopes that will collide.

## BMADX policy by gear

- `X1`: default to no subagents for a single tiny change; optionally use one
  read-only helper for batch copy, duplicated UI text, or quick verification if
  it saves operator time without blocking the patch.
- `X2`: prefer one bounded helper when repo discovery, pattern lookup, or
  verification can run in parallel with the main implementation.
- `X3`: use subagents only if they accelerate discovery, review, or verify.
- `X4`: multiple bounded lanes are acceptable, but ownership and synthesis stay with the main model.

## Time-to-value heuristic

- if the next main-model action is obvious, do it locally and do not wait,
- if a helper can answer an independent question in parallel, use one,
- if the helper result is a prerequisite for the next step, keep it local instead,
- close helper lanes as soon as their evidence is integrated.

## Future-proofing

Do not hardcode:
- one model,
- one vendor,
- one subagent type.

Do hardcode:
- what the helper should investigate,
- what its write scope is,
- what output it must return.
