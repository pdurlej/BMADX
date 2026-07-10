# BMADX Subagent Policy for BMADX

- Use smaller, faster subagents for bounded discovery, review support, and verification support.
- Optimize operator time-to-value: the main model keeps moving while helpers answer independent side questions.
- Keep the main model responsible for decisions, synthesis, integration, and final accountability.
- Do not hardcode a single model choice into policy.
- For a single simple `X1`, default to no subagents.
- For batch `X1` or normal `X2`, use one read-only helper when pattern lookup or verification can run in parallel.
- Do not wait on a helper when the next safe action is already obvious.
- In `X4`, use subagents only where the lane is independent and clearly scoped.

Generated: PUBLIC_SAMPLE
