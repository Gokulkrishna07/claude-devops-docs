# <PROJECT> CI/CD Pipeline

> **Owner:** <TEAM> · **Config:** <path> · **Runbook:** <link>
> **Last verified:** <YYYY-MM-DD> by <@handle>

## What this pipeline does

<4-5 lines: which repo, what artefacts, which environments it can reach,
full-run duration, deploy frequency.>

## Stack

| Stage | Tool | Runs on | Config |
|---|---|---|---|
| <stage> | <tool> | <hosted/self-hosted> | <path> |

## Pipeline

<!-- Regenerate: python3 scripts/gen_diagram.py docs/pipeline.yaml --backend mermaid -->
![Pipeline](pipeline.png)

## Stages

### `<stage-name>`
<What it does — 1 line.>
<Anything non-obvious: why this runner, what's cached, what it depends on — 1-2 lines.>
**~<N> min · ≈$<N>/run · ~<N> runs/mo**

<!-- Repeat per stage. -->

## Triggers and gates

| Trigger | Result | Gate |
|---|---|---|
| PR opened | <> | <> |
| Merge to `<branch>` | <> | <> |
| Tag `<pattern>` | <> | <> |

**Branch protection:** <required checks, who can bypass>
**Known bypass paths:** <hotfix branches, admin merge, manual dispatch — write these down>

## Secrets and permissions

| Name | Used by | Source | Rotation |
|---|---|---|---|
| `<NAME>` | <stage> | <OIDC / repo secret / vault path> | <cadence, owner> |

**Pipeline identity permissions:** <what the deploy role can actually do>

## Operating it

**Rerun a failed job:** <how> · Safe to rerun? <yes/no, why>
**Cancel a run mid-deploy:** <how> · **Leaves behind:** <partial state, and how to clean it>
**Roll back:** <exact command or UI path> · **Not safe if** <migration ran / other condition>
**Debug:** logs at <where>, retained <N> days · <how to get a shell, if possible>
**Emergency skip:** <possible? who may?>

## Failure modes

See <runbook link>. Pipeline-specific entries:
- <flaky test / registry rate limit / runner disk> → <runbook anchor>
