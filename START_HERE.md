# Start Here

If you are new to BMADX, start here instead of reading the whole repo.

## What BMADX is

BMADX is a low-friction Codex layer on top of BMAD.

It helps Codex pick the lightest safe way to work:
- tiny fixes stay tiny,
- normal changes stay compact,
- BMAD-heavy work escalates when it should,
- messy repos can use a rare Rescue Mode (`X4/FUBAR`).

BMAD still stays in charge of process and artifacts.

The goal is not to teach you software architecture jargon. The goal is to help
you describe the product problem clearly, then let Codex work inside safer
architecture and verification boundaries.

BMADX uses a simple Architecture Guardrail Card behind the scenes:

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

For tiny and normal work, BMADX should answer these silently. It should ask you
only when the answer changes the safe mode.

For harder calls, the recommended stack is:
- Oracle for expert second opinions with the right files attached,
- BMAD for process and architecture source of truth,
- BMADX for choosing the lightest safe Codex mode,
- Guardrails.md-style constraints for hard repo lessons,
- pyfallow and CI/tests for deterministic code evidence.

## What to do first

1. Check that BMAD is already installed in your Codex skills.
2. Run the install wrapper from [5-Minute Quickstart](docs/5-minute-quickstart.md).
3. Paste one of the starter prompts from [What to Paste into Codex](docs/what-to-paste-into-codex.md).

## Check BMAD first

BMADX requires BMAD for Codex. If this file exists, the usual dependency is
present:

```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills/bmad-method-codex/SKILL.md"
```

If it does not exist, install BMAD for Codex first. BMADX is intentionally not a
standalone replacement for BMAD.

## Fastest install path

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

The installer copies the BMADX skill into your Codex skills folder, verifies the
BMAD dependency, runs the BMADX sync/check path, and prints the next prompt to
paste into Codex. It does not edit your global Codex model config.

## First prompt to try

```text
Use BMADX for this repo. Pick the lightest safe mode. Keep it lightweight unless BMAD is truly needed.

My task:
Add a pricing section to the landing page and keep the change small.

What I care about:
speed, clarity, and not overengineering it
```

## What a correct first answer looks like

```text
Choice: X1 / tiny local change
Why: This is copy/UI-only and does not touch auth, billing, data, production, or migrations.
Next step: Make the smallest page change and verify the landing page renders.
```

For a normal bounded task, expect a short `X2` plan with at most a few concrete
steps and verification checks. You should not have to pick `X1/X2/X3/X4`
yourself for typical work.

## Good first tests

Try BMADX on one small task and one risky task before judging it:

- a tiny copy or UI tweak, where the right answer is "do not add ceremony";
- an auth, billing, data, migration, or architecture task, where the right
  answer is "slow down and prove the change is safe."

If the classification surprises you, share the prompt and expected outcome in
[GitHub Discussions](https://github.com/pdurlej/BMADX/discussions). The project
gets better from real misroutes, not from perfect demo prompts.

## Read next

- [5-Minute Quickstart](docs/5-minute-quickstart.md)
- [Install for Vibe Coders](docs/install-for-vibe-coders.md)
- [What to Paste into Codex](docs/what-to-paste-into-codex.md)
- [Architecture Guardrail Card](docs/architecture-guardrail-card.md)
- [Choose BMAD vs BMADX vs OMX](docs/choose-bmad-bmadx-omx.md)
- [Community Feedback](docs/community-feedback.md)
- [Ecosystem and Strategic Stance](docs/ecosystem-and-stance.md)
- [FAQ](docs/faq.md)
