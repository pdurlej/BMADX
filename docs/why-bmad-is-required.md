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

If you do not want the BMAD dependency model, BMADX is probably not the right tool.
