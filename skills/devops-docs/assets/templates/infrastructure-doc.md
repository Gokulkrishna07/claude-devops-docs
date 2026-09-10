# <PROJECT> Infrastructure

> **Owner:** <TEAM> · **Repo:** <link> · **Runbook:** <link>
> **Last verified:** <YYYY-MM-DD> by <@handle>

## What this is

<4-5 lines. What it serves, which environments, who owns it, roughly what it costs
per month. A reader who stops here should know whether this repo is relevant to them.>

## Stack

| Layer | Tool | Version | Notes |
|---|---|---|---|
| IaC | <Terraform/OpenTofu/CDK> | <version> | pinned in <file> |
| Provider | <AWS/GCP/Azure> | <constraint> | |
| State | <backend> | | <bucket/lock table> |
| Secrets | <store> | | injected at runtime |
| Orchestration | <EKS/ECS/VMs> | <version> | |

## Architecture

<!-- Regenerate: python3 scripts/gen_diagram.py docs/architecture.yaml -o docs/architecture -->
![Architecture](architecture.png)

| # | Flow |
|---|---|
| 1 | <what happens at this edge> |
| 2 | <...> |

## Components

### <Component name> (<type, size, key config>)
<What it does *in this system* — 1 line.>
<How it's configured in a way that matters, and why — 1-2 lines.>
**≈$<N>/mo** — <breakdown>. <REGION>, <pricing model>, as of <DATE>.

<!-- Repeat per component that costs money, holds state, or can take the system down. -->

## How it connects

**Request path:** <①→② …, end to end>

**Auth between components:**
| From | To | Mechanism | Identity |
|---|---|---|---|
| <svc> | <svc> | <IRSA / IAM role / mTLS> | <role name> |

**Public entry points:** <every internet-facing thing, listed>

**Non-request flows:** <replication, backups, log shipping, scheduled jobs, cross-region copies>

**External dependencies not in this repo:** <shared VPC, DNS zone, manual cert — and who owns each>

## Operating it

**State:** <where, how locked, who can write, how environments are separated>

**How a change reaches production:** <CI or laptop, gates, approvers>

**Blast radius — resources that force replacement:**
| Change | Effect |
|---|---|
| <attribute> on <resource> | **destroys and recreates** — <consequence> |

**Drift:** <what's managed outside IaC, whether detection runs, what to do>

**Access required:** plan `<role>` · apply `<role>` · read state `<role>`

**Disaster recovery:** RTO <N> · RPO <N> · backups cover <what> · last restore test <date>

## Cost summary

> All figures: <REGION>, <pricing model>, <CURRENCY>, as of <DATE>, from <SOURCE>.
> Excludes <data transfer / support / tax>. Estimates — reconcile against billing data.

| Driver | ≈$/mo | % | Note |
|---|---|---|---|
| <driver> | | | |
| **Total** | | | |

**Biggest lever:** <the one change that would move this most>

## Risks and gotchas

- <manual resources not in code, deprecated versions, SPOFs, quotas, pinned forks>
