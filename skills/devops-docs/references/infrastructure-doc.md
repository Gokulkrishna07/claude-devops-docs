# Infrastructure documentation (Terraform / OpenTofu / CDK / Pulumi)

For a repository that provisions cloud infrastructure as code. The reader is a DevOps engineer who has just been handed this repo and has to operate, extend, or cost-review it without the author.

**Read `SAFETY.md` first.** Terraform state and `.tfvars` are the two most common sources of leaked credentials in exactly this kind of document.

## Fixed structure

Use this order. It moves from orientation to detail, so a reader can stop as soon as they have what they need.

```
1. What this is          4-5 lines, no more
2. Stack                 table: layer, tool, version
3. Architecture          the diagram, with numbered callouts
4. Components            2-3 lines each + cost
5. How it connects       the flows the diagram can't show
6. Operating it          state, apply, drift, blast radius, access
7. Cost summary          drivers ranked, with assumptions
8. Risks and gotchas     what will bite the next person
```

### 1. What this is

Four to five lines. What the infrastructure serves, which environments it covers, who owns it, and what it costs roughly per month. A reader who stops here should still be able to decide whether this repo is relevant to their problem.

Not: "This repository contains Terraform code for provisioning AWS resources." That describes every Terraform repo ever written.

### 2. Stack

A table, not prose. Include versions — an engineer who runs `terraform` 1.9 against a repo pinned to 1.5 finds out the hard way.

| Layer | Tool | Version | Notes |
|---|---|---|---|
| IaC | OpenTofu | 1.8.x | pinned in `.tool-versions` |
| Provider | AWS | ~> 5.60 | |
| State | S3 + DynamoDB lock | | bucket `<NAME>`, region `<REGION>` |
| Secrets | AWS Secrets Manager | | injected at runtime, never in state |
| Orchestration | EKS | 1.30 | managed node groups |

### 3. Architecture diagram

One image, generated from a checked-in spec so it can be regenerated when the infrastructure changes. See `diagrams.md` for how to produce it and `assets/templates/architecture.example.yaml` for the spec format.

Number the edges. The numbers are what the Components and Connections sections refer back to, and numbered callouts are how every good cloud reference architecture is written — they let prose point at a specific hop without re-describing it.

Show trust boundaries (VPC, subnets, account boundaries) as nested groups. Those boundaries are the part a reader cannot infer from a resource list, and they are what a security reviewer looks for first.

### 4. Components

One entry per significant component, two to three lines each, plus cost. Significant means it costs money, holds state, or can take the system down. A security group is not a component; the RDS instance behind it is.

For each: **what it does here** (not what the service is in general), **how it's configured** in a way that matters, and **what it costs**.

> **Amazon RDS (PostgreSQL 16, `db.r6g.large`, Multi-AZ)**
> Primary datastore for orders and inventory. Multi-AZ because a failover during business hours is cheaper than the alternative; single-AZ in staging.
> Automated backups 7 days, PITR enabled. Not publicly accessible; reached only from the app subnets.
> **≈$430/mo** — instance $310, storage 200GB gp3 $46, Multi-AZ standby doubles the instance line. See Cost summary for assumptions.

That is three lines and a cost, and it tells a stranger more than a page of Terraform would.

Do not restate the resource block. Anyone can read `main.tf`. Document the reasoning and the operational consequence.

### 5. How it connects

The diagram shows topology. This section covers what topology can't:

- **Request path**, end to end, referencing the numbered edges: "①→② user hits CloudFront, cache miss goes to ALB…"
- **Auth between components** — IAM roles, IRSA, service accounts, mTLS. Name the role, not its policy JSON.
- **What is public and what is not.** Every internet-facing entry point, listed. If a reader has to work this out from security group rules, the document has failed.
- **Data flows that aren't request flows** — replication, backups, log shipping, scheduled jobs, cross-region copies. These are invisible in most diagrams and are frequently where cost and compliance surprises live.
- **Hard dependencies on things outside this repo** — a shared VPC, a DNS zone owned by another team, a manually created ACM certificate. These are the things that break for reasons nobody can find.

### 6. Operating it

The section that turns a code walkthrough into something a DevOps engineer can act on.

- **State**: where it lives, how it's locked, who can write it, whether workspaces or separate backends separate the environments. If a mistake here can corrupt shared state, say so loudly.
- **How a change reaches production**: is `apply` run from CI or a laptop, what gates exist, who approves. If it's a laptop, say that — it's a finding, and pretending otherwise helps nobody.
- **Blast radius of a plan**: which resources force replacement when touched. `aws_db_instance` identifier changes, subnet CIDR changes, and anything with `create_before_destroy = false` deserve an explicit warning. This is the single most valuable subsection for a new engineer, because the failure mode is destroying a production database while believing you are renaming a tag.
- **Drift**: whether anything is managed outside Terraform, whether drift detection runs, what to do when found.
- **Access**: which role or SSO group is needed to plan, to apply, to read state.
- **Bootstrap and teardown order**, if there are dependencies between stacks.
- **Disaster recovery**: what the backups actually cover, RTO/RPO if defined, and when a restore was last tested. Untested backups are a hypothesis — say which one it is.

### 7. Cost summary

See `cost.md`. Never quote prices from memory. State region, date, and assumptions; rank the drivers; call out the ones that surprise people.

### 8. Risks and gotchas

Honest and specific. Manual resources not in code, deprecated provider versions, a hardcoded AMI, an unencrypted volume, a single point of failure, a quota you're close to, a module pinned to a fork. Every infrastructure repo has these. Writing them down is what distinguishes a document written by someone who understands the system from one generated from the file listing.

## For CDK and Pulumi

Same structure. Two differences worth handling explicitly: the synthesised CloudFormation stack boundary is the real deployment unit, so document stacks rather than files; and construct-level abstraction hides resources that still cost money, so derive the component list from `cdk synth` output (which you can ask the user to run) rather than from the TypeScript.
