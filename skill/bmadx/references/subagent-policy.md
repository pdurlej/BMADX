# Capability-Based Subagent Policy

BMADX promotes capability-based subagent usage rather than a single hardcoded
model name.

## Rule

- use smaller and faster subagents for bounded, read-heavy, parallel support,
- keep the main model responsible for decisions, integration, and final accountability.

## Good uses

- repo mapping and discovery,
- diff review support,
- verification support,
- comparing two implementation options,
- reading long artifacts without polluting the main context.

## Bad uses

- delegating the whole problem without synthesis,
- spawning subagents for simple `X1`,
- parallelizing work that is actually sequentially dependent,
- using subagents to hide indecision.

## BMADX policy by gear

- `X1`: default to no subagents.
- `X2`: optionally use one bounded helper.
- `X3`: use subagents only if they accelerate discovery, review, or verify.
- `X4`: multiple bounded lanes are acceptable, but ownership and synthesis stay with the main model.

## Future-proofing

Do not hardcode:
- one model,
- one vendor,
- one subagent type.

Do hardcode:
- what the helper should investigate,
- what its write scope is,
- what output it must return.
