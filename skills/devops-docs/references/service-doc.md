# Service documentation

The document that answers "what is this thing and what happens if I touch it." One per deployable service. If someone inherits this service tomorrow with no handover, this is what they read first.

## What belongs here

**Purpose, in one paragraph.** What it does in business terms, who depends on it, and what breaks if it's down. Not "a microservice built with Node.js" - that's the stack, not the purpose.

**Where it runs.** Environments, namespaces, regions, URLs, repo, image name. Concrete identifiers a stranger can paste into a terminal.

**Dependencies, and what happens when each fails.** This table earns more of its keep than anything else in the document:

| Depends on | For | If it's down |
|---|---|---|
| `postgres-main` | All reads and writes | Hard down, 503s immediately |
| `redis-sessions` | Session cache | Degraded - falls back to DB, ~4x latency |
| `notify-api` | Sending emails | Queues and retries for 24h, no user impact |

The third column is the whole point. Without it the reader can't tell a real outage from a degraded state that will heal itself.

**Dependents.** Who calls this service, so the reader knows what they'll break by restarting it.

**Configuration that isn't obvious.** Not every env var - the ones with non-obvious effects, non-obvious defaults, or a story behind them. Include *why* for anything that looks wrong. `WORKER_CONCURRENCY=2` with the note "higher values exhaust the DB pool; we tried 8 in March and caused an incident" saves the next person a repeat.

**Data and state.** What data it owns, what is safe to lose, what is not, where backups live and when they were last restore-tested. A backup nobody has restored is a hypothesis.

**Failure characteristics.** Startup time, whether it's safe to restart under load, whether it's idempotent, whether requests are safe to retry, ordering constraints between it and its siblings. These are the facts the code will not tell a stranger and the ones they most need.

**Ownership and escalation.** Team, on-call rota, Slack channel, escalation path.

**Links out.** Runbook, dashboards, alerts, repo, ADRs. Don't restate their content.

## What does not belong here

- Framework or language explanations
- API endpoint listings that duplicate an OpenAPI spec - link it instead
- Directory structure listings; anyone can run `ls`
- Function-level description of the code
- Setup instructions longer than the code itself; if local setup is complex, that's a `make dev` problem, not a documentation problem
- Generic sections with nothing specific in them

## Calibration test

Hand the draft to someone on another team. If they can answer these without asking you, it's done:

1. What breaks if I stop this service right now?
2. Which of its dependencies can I safely lose?
3. Is it safe to restart during peak traffic?
4. Who do I call at 2am?
5. Where does its data live and can it be recovered?

If they can't, the missing answers are the only things worth adding.
