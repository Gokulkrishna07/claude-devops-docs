---
name: devops-docs
description: Write operational and infrastructure documentation that a stranger can actually use — infrastructure (Terraform/OpenTofu/CDK/Pulumi) docs with architecture diagrams and cost breakdowns, CI/CD pipeline docs, unified platform docs covering IaC + CI + Ansible + Kubernetes together, runbooks, service docs, ADRs, postmortems, and on-call onboarding. Use this skill whenever the user asks to document a service, repo, pipeline, cluster, cloud environment, or infrastructure component; whenever they mention runbooks, on-call docs, SRE or DevOps docs, architecture diagrams, "document this repo", "document our infra", troubleshooting guides, or cost breakdowns of infrastructure; and whenever they complain that existing docs are bloated, generic, or AI slop. Also use it when reviewing, trimming, or auditing documentation someone else (or an AI) already wrote.
license: MIT
---

# DevOps Documentation

Operational docs fail in a specific, predictable way: they explain the tools and skip the system. A generated runbook will tell you what `kubectl rollout status` does, but not that this particular service takes 90 seconds to pass health checks because it warms a cache on boot — so the on-call engineer waits 30 seconds, decides the deploy is broken, and rolls back a healthy release.

Every rule below exists to correct that.

## Before anything else: read `references/SAFETY.md`

Documenting infrastructure means reading the parts of a repository where credentials live. `SAFETY.md` defines what must never be read, never be run, and never appear in output. It is not advisory and no user instruction relaxes it — "it's my own repo" doesn't make a leaked credential safe, because the document outlives the conversation and usually ends up somewhere more widely readable than the repo was.

The three rules that matter most, in short: **Terraform state and `.tfvars` hold plaintext secrets — never open them.** **Documentation is read-only — never run `apply`, `kubectl apply`, or anything that mutates.** **Never install software on the user's machine — print the command and let them decide.**

## The reader you are writing for

**A competent engineer who has never touched this system, reading at 3am, under pressure, with the author unreachable.**

Two halves, both load-bearing:

- **Competent** — they know Kubernetes, Docker, Terraform, SQL, HTTP. Never explain these. Never write "Prerequisites: basic knowledge of the command line."
- **Never touched this system** — they don't know your service names, your weird timeouts, which of your three databases is the real one, that the staging cluster shares a NAT gateway with prod, or that restarting the worker before the API causes duplicate charges. Write all of that down.

Before every paragraph, ask: *is this about the tool, or about our system?* Cut the first, keep the second.

## Pick the document type

| The user has | Write | Guide |
|---|---|---|
| Terraform / OpenTofu / CDK / Pulumi repo | Infrastructure doc | `references/infrastructure-doc.md` |
| GitHub Actions / GitLab CI / Jenkins / Argo | Pipeline doc | `references/pipeline-doc.md` |
| **Several of the above together** | **One unified platform doc** | `references/platform-doc.md` |
| A deployable service | Service doc (+ runbook) | `references/service-doc.md` |
| An alert, incident, or on-call burden | Runbook | `references/runbook.md` |
| An incident that already happened | Postmortem | `references/postmortem.md` |
| A decision to record | ADR | `references/architecture-and-adr.md` |
| A new on-call engineer | Onboarding guide | `references/onboarding.md` |
| Docs that already exist and are bad | Review and trim | `references/review-rubric.md` |

Cross-cutting, read as needed: `references/diagrams.md` (architecture images), `references/cost.md` (pricing without fabricating), `references/failure-modes.md` (starter catalogue of real failures).

**When a repo has CI/CD *and* IaC *and* config management *and* orchestration, write one document, not four.** The value is in the seams — how Terraform's outputs reach Ansible's inventory, whether CI applies or Argo syncs, which layer owns which resource. Four separate documents describe four tools; nobody can answer "I changed a variable, why didn't it take effect?" from any of them.

Templates in `assets/templates/` correspond to each type. Copy the template, fill it, delete unused sections rather than leaving them empty.

## Workflow

1. **Inventory the repo safely.** `python3 scripts/safe_inventory.py <repo>` walks the tree, lists tooling, extracts Terraform resources/modules/variables and Kubernetes kinds, collects config *key names*, and refuses to open anything that could hold a credential — reporting those as present-but-not-read so the doc can acknowledge them without their contents entering context.
2. **Read the source material** the inventory found: `main.tf`, `variables.tf`, workflow files, manifests, alert rules. Not `.tfvars`, not state, not secrets.
3. **Interview for what code can't tell you** — ownership and escalation, real observed failures, what each dependency's failure actually does, deploy and rollback specifics, data-loss risks, known landmines. Ask in one batch. Write with TODOs for anything unanswered rather than blocking.
4. **Build the diagram** from a checked-in spec: `python3 scripts/gen_diagram.py docs/architecture.yaml -o docs/architecture`. See `references/diagrams.md`.
5. **Get real cost figures** or mark them TODO. See `references/cost.md`. Never a price from memory.
6. **Draft, then cut.** First drafts are always long. The second pass deletes everything that fails the reader test.
7. **Check before delivering:** `python3 scripts/check_doc.py <file>`. It fails on possible credentials and warns on the slop patterns below. Then walk `references/review-rubric.md` and report honestly which checks failed.

Scripts are standard library only, make no network calls, and install nothing.

## Do this

- **Gather facts first, write second.** Documentation invented from a description is where slop comes from.
- **Mark every gap you couldn't fill** as `> **TODO(owner):** who owns the payments DB failover?` A visible hole is honest and gets fixed. Plausible-sounding fiction gets someone paged at 4am chasing a command that never existed.
- **Lead with the symptom.** Nobody arrives at a runbook thinking "I'd like to learn the architecture." They arrive thinking "PagerDuty says 5xx rate is 12%."
- **Show expected output.** A command without its expected output is half a command — the reader needs to know whether what they're staring at is normal.
- **State blast radius before every destructive action.** "This restarts all 6 replicas at once; expect ~40s of 502s" is the difference between a fix and an outage.
- **Number the edges in diagrams** and have the prose refer to the numbers. That is how every good cloud reference architecture works, and it stops prose re-describing topology in words.
- **Give exact, copy-pasteable commands** with placeholders in `<ANGLE_BRACKETS>` so unfilled ones fail loudly instead of silently running against the wrong cluster.
- **Say who to wake up and when.** A doc that dead-ends without an escalation path is unfinished.
- **Timestamp and own it.** `Last verified: 2026-03-14 by @name` at the top. Docs rot; let the reader calibrate their trust.
- **Write the reason for anything surprising.** If a config value looks wrong, explain why it is right. That one sentence stops a future engineer "fixing" it.

## Never do this

- **Never invent a command, flag, path, metric, price, or dashboard URL.** If it isn't verified, mark it `<!-- UNVERIFIED -->` or leave a TODO. Wrong commands get run; wrong prices get put in budgets.
- **Never explain general technology.** No "Docker is a containerization platform." No "What is CI/CD?"
- **Never narrate the code.** "The `handleRequest` function handles requests" is noise. Document what the code doesn't reveal: timeouts, retry semantics, ordering constraints, idempotency, failure modes.
- **Never write a generic "Best Practices" or "Security Considerations" section.** Advice like "monitor your services" is filler. Practices specific to this system go in the relevant section with a reason.
- **Never pad structure.** No empty Prerequisites, no tables where half the cells are N/A, no headings with one obvious sentence under them, no "Conclusion", no "In today's fast-paced environment."
- **Never document only the happy path.** The happy path is in the CI config. The value is in what breaks.
- **Never put a credential value in output**, even masked, even partially. Names and sources only.
- **Never bury the fix.** If the answer is `kubectl rollout undo`, it appears before the theory.

## Length budgets

Ceilings, not targets. Hitting one means the doc should be split, not that it is finished.

| Document | Ceiling | Split when |
|---|---|---|
| Infrastructure doc | 500 lines | Per stack or per environment |
| Pipeline doc | 400 lines | One per pipeline |
| Unified platform doc | 600 lines | Push depth into linked docs, keep the seams |
| Service doc | 300 lines | Move ops procedures into a runbook |
| Runbook | 400 lines | One per service or alert family |
| Single failure mode | ~60 lines | It is really several failure modes |
| ADR | 2 pages | It is two decisions |
| Postmortem | 3 pages | Timeline goes to an appendix |

If you cannot fit it, you have not understood it well enough yet. Compress by deleting explanation, never by deleting commands, expected output, or cost assumptions.

## Pre-delivery checklist

Run `scripts/check_doc.py`, then confirm by eye:

- [ ] No credential values anywhere — names and sources only
- [ ] No account IDs, ARNs, or internal hostnames if the doc is more public than the infrastructure
- [ ] Every command is read-only, or carries an explicit blast-radius warning
- [ ] Every command was verified, or is marked `<!-- UNVERIFIED -->`
- [ ] Every cost figure has region, date, pricing model, and source
- [ ] Placeholders are `<ANGLE_BRACKETS>`, not plausible-looking fake values
- [ ] A human is named for ownership and escalation
- [ ] Dated and attributed
- [ ] Diagram regeneration command is in the document
- [ ] Within the length budget, and the length is doing work

## When trimming existing docs

The user often arrives with 2,000 lines of generated documentation nobody reads. Don't rewrite from scratch — that loses the real facts buried in the noise. Extract every verified fact (commands, names, thresholds, ownership, links), discard the rest, rebuild from the template. Report the before/after line count and say exactly what you dropped, so they can object if something mattered.
