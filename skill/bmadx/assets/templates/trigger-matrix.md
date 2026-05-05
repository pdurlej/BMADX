# BMADX Trigger Matrix for {{project_name}}

| Signal | X1 | X2 | X3 | X4 |
| --- | --- | --- | --- | --- |
| 1 local file | yes | no | no | no |
| a few files | no | yes | no | no |
| needs BMAD artifact | no | no | yes | yes |
| auth / billing / permissions / data deletion / secrets | no | no | yes | yes |
| rollout and ownership design | no | no | sometimes | yes |
| repeated failures or unclear architecture owner | no | no | sometimes | yes |
| scaffold bundle | no | no | no | yes |

## When this becomes BMAD

- Red-zone task -> `X3` minimum unless purely textual.
- Red-zone task with unclear owner, rollback risk, incident recovery, or no proof path -> `X4`.
- Existing BMAD story or architecture artifact dependency -> `X3`.
- Need for scaffold bundle, ownership cleanup, failure patterns, or rollout matrix -> `X4`.

## Architecture Guardrail Card

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

Generated: {{generated_at}}
