# Trigger Matrix

Operational matrix for classifying tasks without guessing.

This file is mainly for boundary cases. In the obvious `X1/X2` happy path, use
the heuristics embedded in `SKILL.md` and do not open reference docs.

| Signal | X1 | X2 | X3 | X4 |
| --- | --- | --- | --- | --- |
| 1 local file | yes | no | no | no |
| a few files / local blast radius | no | yes | no | no |
| needs a new BMAD artifact | no | no | yes | yes |
| user says `plan` | no | questions | questions | questions |
| ambiguous scope | no | questions | questions | questions |
| API/schema/auth/perf/concurrency risk | no | sometimes | yes | yes |
| rollout and ownership need design | no | no | sometimes | yes |
| scaffold bundle beyond BMAD | no | no | no | yes |

## Recommended thresholds

- `X1`: simple fix or simple upgrade.
- `X2`: bounded multi-file local change.
- `X3`: normal BMAD flow.
- `X4`: BMAD plus bundle when BMAD alone does not yet provide enough operational structure.

## Gate after classification

- the correct classification should remain correct even when BMAD is red,
- `X1/X2` use `check --gear X1|X2 --compact` and the cached fast path,
- `X1/X2` without cache should get a warning instead of a block,
- `X3/X4` use `check --gear X3|X4 --compact` with the full live gate,
- without healthy BMAD, execution for `X3/X4` must stop,
- the last healthy BMAD cache softens communication for `X1/X2`, but must not unlock `X3/X4`.

## Example classifications

- "Fix a typo in one component" -> `X1`
- "Add support for a new field in a few places and run tests" -> `X2`
- "Implement a story from the current BMAD sprint" -> `X3`
- "Set up a working approach for a difficult repo and generate scaffolding" -> `X4`
