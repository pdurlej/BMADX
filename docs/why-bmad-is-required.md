# Why BMAD Is Required

BMADX is intentionally not a standalone framework.

It depends on BMAD because BMAD already owns the hard part:
- process structure,
- workflow vocabulary,
- artifacts such as PRDs, architecture, and stories,
- the upstream source of truth for how serious work should be run.

BMADX only adds the Codex-side operational layer:
- lightweight routing,
- verify discipline,
- compact dependency checks,
- rare Rescue Mode scaffolding for difficult repos.

In plain language:
- BMAD is the planning brain,
- BMADX is the lighter day-to-day operator layer.
- Oracle can add expert second opinions,
- pyfallow, Guardrails.md, tests, and scanners can add hard facts or safety memory,
- none of those owns the plan.

For non-technical builders, that split matters. BMADX should make it easier to
ask for product outcomes in plain English while BMAD keeps the architecture and
process backbone from becoming ad-hoc prompting.

If you do not want the BMAD dependency model, BMADX is probably not the right tool.

Red-zone tasks make this dependency more important, not less. Auth, billing,
data deletion, permissions, migrations, secrets, and production config should
enter BMAD unless the change is purely textual.
