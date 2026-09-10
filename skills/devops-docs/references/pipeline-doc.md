# CI/CD pipeline documentation

For GitHub Actions, GitLab CI, Jenkins, CircleCI, Argo CD, or any combination. The reader needs to answer three questions fast: how does my code reach production, why did my build fail, and how do I stop or undo a deploy.

**Read `SAFETY.md` first.** Pipeline definitions reference secrets by name — document the names, never resolve the values, and never read a Jenkins `credentials.xml`.

## Fixed structure

```
1. What this pipeline does     4-5 lines
2. Stack                       table: stage, tool, where it runs
3. Pipeline diagram            trigger to production, with gates
4. Stages                      2-3 lines each + duration + cost
5. Triggers and gates          what starts it, what stops it
6. Secrets and permissions     names and sources only
7. Operating it                rerun, cancel, rollback, debug
8. Failure modes               link to the runbook entries
```

### 1. What this pipeline does

Which repo, which artefacts it produces, which environments it can reach, and how long a full run takes. Include the deploy frequency if known — a pipeline that runs 40 times a day and one that runs monthly need different things from their documentation, and the reader calibrates on this.

### 2. Stack

| Stage | Tool | Runs on | Config |
|---|---|---|---|
| Build | GitHub Actions | `ubuntu-latest` hosted | `.github/workflows/build.yml` |
| Image | Kaniko | self-hosted runner | `build/Dockerfile` |
| Deploy | Argo CD | in-cluster | `argocd/apps/api.yaml` |
| Config | Ansible | bastion | `ansible/site.yml` |

Where each stage runs matters more than it looks: hosted versus self-hosted runners have different network access, different secrets, and different cost models, and "works locally, fails in CI" is nearly always this.

### 3. Pipeline diagram

Left to right, trigger to production. Show every stage, every environment, every approval gate, and every branch of the graph — including the paths that skip stages. If a hotfix branch can bypass staging, the diagram must show it, because that path is where incidents come from.

Mark gates distinctly from stages. A reader needs to see at a glance where a human is required.

Render with `scripts/gen_diagram.py`; the Mermaid backend is usually right here since pipelines are flowcharts rather than infrastructure topology.

### 4. Stages

Two to three lines each, plus **typical duration** and **cost**.

> **`build-and-test`** — installs deps, runs unit and contract tests, produces the container image.
> Runs on a self-hosted runner because the integration tests need VPC access to the staging database.
> Cache: `~/.m2` keyed on `pom.xml` hash; a cache miss adds roughly 4 minutes.
> **~7 min · ≈$0.03/run** (self-hosted `c6i.large`, amortised) · ~180 runs/mo

Duration is documentation. It tells a waiting engineer whether 9 minutes is normal or a symptom, and it is the first thing anyone asks during an incident.

CI cost is genuinely worth including and almost always omitted: GitHub-hosted minutes, self-hosted instance time, artifact and cache storage, and container registry egress. Teams routinely discover they spend more on CI than on the production environment it deploys to.

### 5. Triggers and gates

State precisely what starts a run and what can stop one. Ambiguity here causes accidental production deploys.

| Trigger | Result | Gate |
|---|---|---|
| PR opened | build + test, no deploy | none |
| Merge to `main` | deploy to staging | none |
| Tag `v*` | deploy to production | manual approval by `@platform` |
| Manual dispatch | any environment | approval for prod only |

Then, in prose: which branches are protected, what checks are required, who can bypass, whether a failed test actually blocks a merge or merely annotates it. Write down the bypasses — undocumented bypass paths are how the process everyone believes exists differs from the one that runs.

### 6. Secrets and permissions

Names and sources, never values.

| Name | Used by | Source | Rotation |
|---|---|---|---|
| `AWS_DEPLOY_ROLE` | deploy stage | OIDC, no stored key | n/a |
| `REGISTRY_TOKEN` | image push | repo secret | manual, <owner> |

Also document what the pipeline's identity is allowed to do. A deploy role with `AdministratorAccess` is a finding worth writing down; so is a self-hosted runner that can reach production from a fork's pull request.

### 7. Operating it

- **Rerun** a failed job, and whether rerunning is safe (is the deploy idempotent?)
- **Cancel** a run mid-deploy, and what state that leaves behind — this is the dangerous one and it is almost never documented
- **Roll back** a deployment: the exact command or UI path, and whether it's safe with respect to migrations
- **Debug** a failure: where logs live, how long they're retained, how to get a shell on a runner if that's possible
- **Skip** the pipeline in an emergency, if that's possible at all — and who is allowed to

### 8. Failure modes

Pipelines fail in the same handful of ways. Document yours in the runbook format from `runbook.md` and link them here rather than duplicating. `failure-modes.md` has a starter entry for builds that break with no code change; add the ones specific to this pipeline — a flaky integration test, a registry rate limit, a runner that runs out of disk every few weeks.
