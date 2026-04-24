# FAQ

## Do I need BMAD first?

Yes. BMADX depends on `bmad-method-codex` and does not replace it.

## Do I have to choose `X1/X2/X3/X4` myself?

Usually no. The normal use pattern is to describe the task in plain language and let BMADX choose the lightest safe mode.

## Does BMADX require GPT-5.5?

No. BMADX `v0.2.4` is tuned for Codex on GPT-5.5, but the installer does not change your Codex model config. Benchmarks should record the model explicitly so GPT-5.4 and GPT-5.5 runs stay comparable.

## When does `X4/FUBAR` happen?

Only when the repo or rollout needs extra structure: messy scope, unclear ownership, or a need for scaffold bundle artifacts. It is intentionally rare.

## Is BMADX cheaper than BMAD?

Not in every case. The honest public claim is that BMADX looks strongest against OMX, while BMAD still wins as the upstream process owner and often on raw token cost.

## Why not just use OMX?

Because BMADX is intentionally lighter. If you want a heavier runtime, OMX is closer to that product.

## Can I use BMADX if I am not a developer?

Yes, if you already use Codex and want a lower-friction workflow layer. The public docs and prompt pack are written for non-technical or semi-technical users.

## What should I do right after install?

Paste one of the prompts from [What to Paste into Codex](what-to-paste-into-codex.md).
