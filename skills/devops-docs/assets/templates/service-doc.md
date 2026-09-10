# <SERVICE_NAME>

> **Owner:** <TEAM> · **Channel:** <#CHANNEL> · **Runbook:** <link>
> **Last updated:** <YYYY-MM-DD>

## What it does

<One paragraph, business terms. Who depends on it and what breaks if it's down.>

## Where it runs

| | Production | Staging |
|---|---|---|
| URL | <url> | <url> |
| Namespace | <ns> | <ns> |
| Image | <image> | <image> |

Repo: <link> · Dashboard: <link> · Alerts: <link>

## Depends on

| Depends on | For | If it's down |
|---|---|---|
| <dep> | <what> | <hard down / degraded how / no user impact> |

## Depended on by

| Consumer | Uses | Breaks how if this service stops |
|---|---|---|
| <service> | <endpoint or queue> | <consequence> |

## Configuration worth knowing

<Only the non-obvious. For each: what it does, its value, and why — especially if it looks wrong.>

| Setting | Value | Why |
|---|---|---|
| <KEY> | <value> | <reason / history> |

## Data

- **Owns:** <what data, in which store>
- **Safe to lose:** <what>
- **Not safe to lose:** <what>
- **Backups:** <where, frequency, retention> · **Last restore test:** <date>

## Failure characteristics

- **Startup time:** <N>s <and why, if unusual>
- **Safe to restart under load?** <yes/no, and what happens>
- **Idempotent / retry-safe?** <yes/no, which operations>
- **Ordering constraints:** <e.g. restart API before workers, or jobs double-process>

## Known weak points

<Honest list. Every system has them.>

## Escalation

<Rota, channel, escalation path.>
