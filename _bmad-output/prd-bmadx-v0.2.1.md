# PRD — BMADX v0.2.1

## Goal

Improve routing ergonomics after `v0.2.0` by making the skill lighter for
obvious work and more measurable in benchmark runs.

## Scope

- true fast path for `X1/X2`
- compact gate output from `sync_bmadx.py`
- benchmark runner with explicit `healthy` and `degraded` profiles

## Outcome

The release established the routing/gate infrastructure, but it did not yet
make `X1/X2` compact enough on the answer side.
