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

1. Make sure BMAD is already installed in your Codex skills.
2. Run the install wrapper from [5-Minute Quickstart](docs/5-minute-quickstart.md).
3. Paste one of the starter prompts from [What to Paste into Codex](docs/what-to-paste-into-codex.md).

## Fastest install path

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

## First prompt to try

```text
Use BMADX for this repo. Pick the lightest safe mode. Keep it lightweight unless BMAD is truly needed.

My task:
Add a pricing section to the landing page and keep the change small.

What I care about:
speed, clarity, and not overengineering it
```

## Read next

- [5-Minute Quickstart](docs/5-minute-quickstart.md)
- [Install for Vibe Coders](docs/install-for-vibe-coders.md)
- [What to Paste into Codex](docs/what-to-paste-into-codex.md)
- [Architecture Guardrail Card](docs/architecture-guardrail-card.md)
- [Choose BMAD vs BMADX vs OMX](docs/choose-bmad-bmadx-omx.md)
- [Ecosystem and Strategic Stance](docs/ecosystem-and-stance.md)
- [FAQ](docs/faq.md)
