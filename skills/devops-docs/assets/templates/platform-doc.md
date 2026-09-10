# <PLATFORM NAME>

> **Owner:** <TEAM> · **Last verified:** <YYYY-MM-DD> by <@handle>

## What this platform is

<5 lines: what it runs, which tools compose it, which environments, rough total cost.>

## Tool map

| Concern | Tool | Owns | Does NOT own |
|---|---|---|---|
| Cloud resources | <> | <> | <> |
| Cluster workloads | <> | <> | <> |
| VM config | <> | <> | <> |
| Build & release | <> | <> | <> |
| Runtime | <> | <> | <> |

## The big picture

<!-- Regenerate: python3 scripts/gen_diagram.py docs/platform.yaml -o docs/platform -->
![Platform](platform.png)

## Layer by layer

### <Tool>
Purpose: <1 line> · Manages: <what> · Config: <path> · Invoked by: <how>
**≈$<N>/mo** — <what drives it>

<!-- 2-4 lines each. If a layer needs a page, give it its own doc and link it. -->

## The seams

<!-- The reason this document exists. Be most detailed here. -->

### <Tool A> → <Tool B>
**What crosses:** <artefact, credential, inventory, image tag>
**How:** <mechanism>
**When it breaks:** <what the failure looks like from each side — usually "both look green">
**Who owns the fix:** <>

<!-- Repeat per handoff: IaC→K8s, IaC→config mgmt, CI→IaC, CI→K8s, secrets across layers. -->

## End-to-end: one commit to production

| # | Step | Tool | Typical wait |
|---|---|---|---|
| 1 | <> | <> | <> |

<!-- 10-20 steps. Include the boring waits — that's where people lose their change. -->

## Operating it

**Where do I look first?**
| Symptom | Layer | Check |
|---|---|---|
| <"deploy green but change not live"> | <> | <> |

**Rollback by layer:** <which layer to roll back for which symptom>
**Unsafe concurrent operations:** <combinations that must not overlap>
**Break-glass:** <procedure, who is authorised>

## Cost

> <REGION>, <pricing model>, as of <DATE>, from <SOURCE>.

| Layer | ≈$/mo | % |
|---|---|---|
| **Total** | | |

Include: CI compute and storage, registry, log ingestion, NAT, non-production environments.

## Risks and gotchas

- <overlapping ownership, manual steps between automated ones, drift, bus factor>
