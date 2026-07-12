# Independent Scenario Audit Prompt

Review the attached BMADX decision-value study scenario set before any live
model outputs exist. You are auditing the task distribution, not scoring BMADX.

## Questions

1. Does the set resemble a credible distribution of coding-planning decisions
   for a solo AI operator, including ordinary work and consequential work?
2. Are any tasks worded to reward BMADX-specific concepts, terminology, or
   preferred answers?
3. Are any tasks worded to favor a low-process control regardless of risk?
4. Which scenarios are materially duplicative?
5. Which common task shapes are missing?
6. Are there task details that make one answer obviously correct without real
   judgment?
7. Should the set be approved unchanged, approved after named edits, or
   rejected?

Return only a completed copy of `scenario-audit-v1.json`. Use a pseudonymous
reviewer ID. Set `independent_of_bmadx_authorship=true` only if you did not
author BMADX or these scenarios. Set `completed_before_live_run=true` only if
you have not seen any study responses or arm-level outcomes.

An approval is valid only when `status` is `approved_before_live_run` and
`required_edits` is empty. Do not request or inspect the future arm mapping,
opaque aliases, activation nonces, or response outputs.
