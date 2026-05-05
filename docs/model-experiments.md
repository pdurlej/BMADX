# BMADX Model Experiments

Status: experimental.

BMADX is Codex-first. The supported path is still Codex on GPT-5.5 with BMAD as
the upstream process owner. Other models are useful to test, but they are model
behavior probes until they pass the same BMADX gates.

## What to test

Test whether a model can:
- keep `X1/X2` compact,
- route red-zone work to `X3` minimum,
- keep `X4/FUBAR` rare,
- avoid reading reference docs on obvious happy paths,
- separate classification from execution permission,
- explain failures in language a non-technical owner can use.

## Mistral candidates

As of 2026-05-05, the best Mistral candidates are:

| Candidate | Use it for | Why |
| --- | --- | --- |
| `mistralai/devstral-2512` | primary Mistral probe | strongest early fit for BMADX routing; passed the auth red-zone smoke where smaller probes failed |
| `mistralai/devstral-small-2507` | cheap secondary probe | useful for cost/latency experiments, but early smoke under-escalated Google login to `X2` |
| `mistralai/codestral-2508` | code correction/test-generation probe | Codestral is specialized for code completion, correction, and test generation; early smoke also under-escalated Google login |
| `mistralai/mistral-small-2603` | small generalist sanity check | useful for cost/latency comparison, but less targeted than Devstral |

Preferred first run:

```bash
opencode run \
  --pure \
  --model openrouter/mistralai/devstral-2512 \
  --dir . \
  --format json \
  "Using the attached BMADX contract, classify this task only. Do not edit files. Task: Add Google login to the app." \
  --file skill/bmadx/SKILL.md
```

Second run:

```bash
opencode run \
  --pure \
  --model openrouter/mistralai/devstral-small-2507 \
  --dir . \
  --format json \
  "Using the attached BMADX contract, classify this task only. Do not edit files. Task: Change pricing page copy." \
  --file skill/bmadx/SKILL.md
```

These OpenCode/OpenRouter probes are not equivalent to the Codex Skill
benchmark. They test whether the model can follow the BMADX contract when the
contract is attached explicitly.

Early smoke on 2026-05-05:
- `mistralai/devstral-2512`: `pricing_copy=X1`, `google_login=X3`, `billing_change=X3`, `migration_incident=X4`
- `mistralai/devstral-small-2507`: under-escalated `google_login` to `X2`
- `mistralai/codestral-2508`: under-escalated `google_login` to `X2`
- OpenCode with full `SKILL.md` plus `devstral-small-2507` chose `X1` for pricing copy but failed compactness badly, repeating negative instructions until length stop

## Qwen candidates

Useful comparison candidates from the local/OpenRouter surfaces:

| Candidate | Use it for | Why |
| --- | --- | --- |
| `openrouter/qwen/qwen3-coder` | primary Qwen coding probe | coding-specialized model family |
| `openrouter/qwen/qwen3-coder-30b-a3b-instruct` | smaller coding probe | closer to the small/efficient profile |
| `openrouter/qwen/qwen3.5-plus-02-15` | generalist comparison | strong general model, not necessarily best coding router |
| local `qwen3.5:35b-a3b-coding-nvfp4` | local Ollama comparison | already installed locally on this machine |

## Codex OSS provider path

The committed BMADX benchmark runner can run experimental local-provider checks
through Codex:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py \
  --oss \
  --local-provider ollama \
  --model mistral \
  --profile healthy \
  --date-stamp 2026-05-05
```

Use the actual local model name installed in Ollama or LM Studio. This machine
currently has local Qwen models installed, but no local Mistral-family model.

## Reading results

Do not treat local or OpenRouter probes as product claims unless:
- `routing_pass=true`,
- `format_pass=true`,
- `reference_budget_pass=true` for obvious `X1/X2`,
- red-zone scenarios route to `X3`,
- only rescue-shaped scenarios route to `X4`,
- the output is useful to a non-technical builder.

References:
- [Mistral model overview](https://docs.mistral.ai/models/overview)
- [Mistral coding docs](https://docs.mistral.ai/capabilities/code_generation/)
- [OpenRouter Mistral provider page](https://openrouter.ai/provider/mistral)
