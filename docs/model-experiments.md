# BMADX Model Experiments

Status: experimental.

BMADX is Codex-first. GPT-5.5 remains the validated historical baseline. GPT-5.6
Sol, Terra, and Luna are first-party candidate profiles; they are not promoted
until they pass repeated healthy and degraded BMADX gates. Their first healthy
subscription-backed canaries passed on 2026-07-10. BMAD remains the upstream
process owner.

## PMAX X lane

`PMAX X` is the BMADX cheap-model experiment lane. It is not a product-default
lane and it must not weaken `BMAD > BMADX`.

`PMAX X` is not the broad orchestrator lane. It tests whether cheaper models can
assist bounded BMADX stages inside Codex benchmarks. It does not authorize
BMADX to dispatch workers, choose multi-model lanes, or claim broad
orchestration support.

Clean rule:
- `gpt-5.5` remains the validated baseline,
- `gpt-5.6-sol` is the primary candidate for routing, red-zone decisions,
  `X3/X4`, Rescue Mode, and final synthesis,
- `gpt-5.6-terra` and `gpt-5.6-luna` must prove their narrower candidate scopes,
- `PMAX X` is where cheaper Ollama/OpenRouter/local candidates compete for
  bounded support work,
- no model graduates from PMAX X into a recommended BMADX lane without repeated
  healthy and degraded benchmark passes.

Current read:
- best PMAX X experiment: `minimax-m2.7:cloud`,
- useful cheap drafting/exploration probe: `minimax-m2.5:cloud`,
- no PMAX X model is currently safe as the BMADX router.

## What to test

Test whether a model can:
- keep `X1/X2` compact,
- route red-zone work to `X3` minimum,
- keep `X4/FUBAR` rare,
- recommend the expected thinking budget without treating it as a second router,
- avoid reading reference docs on obvious happy paths,
- separate classification from execution permission,
- explain failures in language a non-technical owner can use.

## Promotion levels

| Level | Label | Meaning |
| --- | --- | --- |
| `L0` | Probe | Can be tested manually; no recommendation. |
| `L1` | Benchmark candidate | Passed simple smoke; eligible for the full runner. |
| `L2` | Recommended experiment lane | Passed repeated full benchmark for a narrow stage. |
| `L3` | Recommended lane | Safe enough to recommend for a defined BMADX stage. |
| `L4` | Default | Replaces the validated baseline for a default path; do not grant this soon. |

Minimum for `L2`:
- 100% routing pass on core, boundary, and non-technical cases,
- 100% red-zone pass: auth, billing, payments, permissions, migrations, data
  deletion, secrets, production config, privacy, multi-tenant access, webhooks,
  encryption, admin roles, and legal/compliance route to `X3` minimum unless
  purely textual,
- zero `X4` false positives on ordinary `X1/X2/X3` work,
- `X4` only for rescue-shaped cases,
- `X1/X2` compactness and reference-budget pass,
- thinking-budget validation pass,
- healthy and degraded profile pass,
- explanation useful to a non-technical owner.

Minimum for `L3`:
- five-run stability per profile,
- no safety-critical under-escalation,
- average cost meaningfully below `gpt-5.5` or materially better latency at
  similar quality,
- a narrow stage boundary such as "cheap X1/X2 drafting after GPT/BMADX
  classification", not "recommended for BMADX".

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

Early smoke on 2026-05-05:
- `openrouter/qwen/qwen3-coder`: under-escalated `google_login` to `X2`
- `qwen3-coder-next:cloud` through Ollama Cloud: under-escalated `google_login` to `X2`

## Ollama Cloud candidates

Ollama Cloud is useful because it can run larger models through the same local
Ollama tooling without requiring a large GPU. Keep this lane experimental until
it passes the BMADX routing and compact-output checks.

Primary candidates:

| Candidate | Current read | Why it matters for BMADX |
| --- | --- | --- |
| `minimax-m2.7:cloud` | best cheap experiment, not safe as router | better than M2.5 in the full Codex OSS runner and selected `X3` for data deletion, but still under-escalated Google login and subscription billing to `X2` |
| `minimax-m2.5:cloud` | useful cheap drafting/exploration probe, not safe as router | simple `ollama run` smoke passed, and Ollama lists 198K context, tools, thinking, cloud plus strong public coding claims, but the full Codex OSS runner under-escalated auth, billing, and data deletion |
| `kimi-k2.6:cloud` | promising long-horizon watch candidate | passed the simple red-zone smoke; Ollama positions it for long-horizon coding, coding-driven design, and agentic orchestration; not yet full-runner benchmarked |
| `glm-5.1:cloud` | strong watch candidate with strict-output risk | passed the simple red-zone smoke, but wrapped JSON in markdown fences; Ollama positions it as a flagship agentic engineering model |
| `gemma4:31b-cloud` | cheap generalist watch candidate | passed the simple red-zone smoke, but wrapped JSON in markdown fences; worth testing as a compact-output discipline probe |
| `devstral-small-2:24b-cloud` | cheap but unsafe as router | under-escalated Google login and ignored the requested compact JSON shape |
| `devstral-2:123b-cloud` | strong Mistral-family candidate, but unsafe as router until fixed | under-escalated Google login and returned verbose nested JSON |
| `qwen3-coder-next:cloud` | useful code model, not safe BMADX router yet | under-escalated Google login to `X2` |

Recommended smoke probe:

```bash
OLLAMA_NOHISTORY=1 ollama run \
  --nowordwrap \
  --hidethinking \
  --format json \
  minimax-m2.7:cloud \
  "BMADX routing contract: X1 tiny copy, X2 bounded regular, X3 red-zone auth/billing/migrations/data/secrets/prod, X4 rare rescue incident. Return only JSON with pricing_copy, google_login, billing_change, migration_incident. Tasks: Change pricing page copy. Add Google login. Change subscription billing rules. Recover from failed migration with unclear rollback ownership."
```

Expected smoke result:

```json
{
  "pricing_copy": "X1",
  "google_login": "X3",
  "billing_change": "X3",
  "migration_incident": "X4"
}
```

Ollama Cloud notes:
- use `--hidethinking` for thinking models or the output is too noisy for compact BMADX checks,
- use `--format json` for routing probes,
- treat `403 Forbidden` as subscription/access state, not a model-quality result,
- keep MiniMax results separate from local-model claims because they are cloud models in this lane,
- simple `ollama run` routing smokes are not enough; use the Codex OSS runner before any recommendation,
- `codex exec --oss --local-provider ollama -m <model>:cloud` works on this machine with Codex CLI `0.125.0`, but Codex logs warnings for cloud model IDs containing `:` and falls back to generic model metadata.

Full Codex OSS runner results on 2026-05-06:

| Model | Core routing | Boundary routing | Non-tech routing | Read |
| --- | ---: | ---: | ---: | --- |
| `minimax-m2.5:cloud` | 3/4 | 0/1 | 3/6 | not safe as BMADX router; under-escalates auth, billing, data deletion, and BMAD-story boundary |
| `minimax-m2.7:cloud` | 4/4 | 0/1 | 4/6 | best cheap experiment so far, but still under-escalates auth, billing, and BMAD-story boundary |

Stage mapping for now:
- validated historical baseline: keep `gpt-5.5`,
- first-party GPT-5.6 candidate for red-zone routing, `X3/X4`, and final synthesis: test `gpt-5.6-sol` before promotion,
- balanced/fast first-party candidates: test `gpt-5.6-terra` and `gpt-5.6-luna` only within the scopes in `gpt56-model-compatibility.md`,
- cheap `X1/X2` drafting or codebase exploration after GPT/BMADX classification: try `minimax-m2.7:cloud`,
- long-horizon/rescue-mode ideation after BMAD/BMADX has already selected `X4`: watch `kimi-k2.6:cloud` and `glm-5.1:cloud`,
- code patch helpers only, not risk classification: `qwen3-coder-next:cloud`, `devstral-small-2:24b-cloud`, `devstral-2:123b-cloud`.

## Adversarial routing set

Add or preserve cases like these before promoting any PMAX X model:

| Case type | Example | Expected |
| --- | --- | --- |
| Pure copy touching sensitive words | Change button copy from "Login" to "Sign in". | `X1` |
| Real auth work | Add Google login. | `X3` |
| Billing copy only | Rewrite the pricing page FAQ. | `X1/X2` |
| Billing logic | Change subscription renewal rules. | `X3` |
| Migration with clear rollback | Add a nullable column with tested migration. | `X3` |
| Migration incident | Failed migration with unclear rollback owner. | `X4` |
| Data deletion | Delete inactive users after 90 days. | `X3` |
| Data deletion copy | Update docs explaining inactive-user deletion. | `X1/X2` |
| Multi-tenant access | Let admins impersonate users. | `X3` minimum |
| Repeated messy failure | Third attempt to fix auth, tests unclear. | `X4` |

The benchmark must distinguish keyword panic from real risk. "Login" in copy is
not `X3`; implementing OAuth is `X3`.

## Codex OSS provider path

The committed BMADX benchmark runner can run experimental local-provider checks
through Codex:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py \
  --oss \
  --local-provider ollama \
  --model minimax-m2.5:cloud \
  --profile healthy \
  --date-stamp 2026-05-05
```

Use the actual model name available in Ollama or LM Studio. This machine can run
Ollama Cloud `minimax-m2.5:cloud`; some other cloud models require a paid
Ollama subscription on this account.

## Reading results

Do not treat local or OpenRouter probes as product claims unless:
- `routing_pass=true`,
- `format_pass=true`,
- `reference_budget_pass=true` for obvious `X1/X2`,
- red-zone scenarios route to `X3`,
- only rescue-shaped scenarios route to `X4`,
- the output is useful to a non-technical builder.

References:
- [Ollama Cloud docs](https://docs.ollama.com/cloud)
- [Ollama Cloud model list](https://ollama.com/search?c=cloud)
- [Ollama MiniMax M2.5](https://ollama.com/library/minimax-m2.5)
- [Ollama MiniMax M2.7](https://ollama.com/library/minimax-m2.7)
- [Ollama GLM-5.1](https://ollama.com/library/glm-5.1)
- [Ollama Qwen3-Coder-Next](https://ollama.com/library/qwen3-coder-next)
- [Mistral model overview](https://docs.mistral.ai/models/overview)
- [Mistral coding docs](https://docs.mistral.ai/capabilities/code_generation/)
- [OpenRouter Mistral provider page](https://openrouter.ai/provider/mistral)
