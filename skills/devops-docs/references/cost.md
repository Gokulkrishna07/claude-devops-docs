# Costing infrastructure in documentation

Cost is the section most likely to contain confident fabrication, because plausible-looking prices are easy to generate and hard for a reader to check. A wrong figure here gets pasted into a budget request or a client proposal. Treat every number as needing a source.

## The rule

**Never state a price from memory.** Cloud pricing changes, varies by region by 20-40%, and depends on commitment terms. A remembered figure is a guess wearing a suit.

Get numbers from, in order of preference:

1. **The account's own billing data** — Cost Explorer, GCP Billing export, Azure Cost Analysis. This is real, and it includes the things estimates miss.
2. **`infracost`** run against the plan. Purpose-built, understands Terraform, produces a diff per PR. Ask the user to run it — don't install it yourself.
3. **The provider's pricing calculator or pricing page**, fetched at the time of writing.
4. **A clearly-labelled TODO.** Always better than a number you invented.

If you cannot get a real figure, write:

> **Cost:** `TODO(owner)` — run `infracost breakdown --path .` and paste the output.

## Always state the assumptions

A price without assumptions is not information. Every cost figure needs:

- **Region** — `us-east-1` is often the cheapest; `ap-south-1` or `sa-east-1` can be materially different
- **Date** — `as of 2026-03-14`
- **Pricing model** — on-demand, reserved, savings plan, spot
- **Usage assumption** — "at 730 hrs/mo", "at 2TB egress/mo", "at current staging traffic"
- **Currency**
- **What is excluded** — support plans, data transfer, taxes

Header for the cost section:

```markdown
> All figures: <REGION>, on-demand, USD, as of <DATE>, from <SOURCE>.
> Excludes data transfer between regions, support plan, and taxes.
> Estimates only — reconcile against Cost Explorer before using in a budget.
```

## Rank the drivers

A table of thirty line items is not useful. Three ranked drivers plus a total is.

| Driver | ≈$/mo | % | Note |
|---|---|---|---|
| RDS Multi-AZ `db.r6g.large` | 430 | 38% | standby doubles the instance cost |
| EKS node group (3 × `m6i.large`) | 260 | 23% | fixed size, no autoscaling configured |
| NAT Gateway (2 AZ) | 95 | 8% | $0.045/hr each + $0.045/GB processed |
| Everything else | 340 | 31% | |
| **Total** | **≈1,125** | | |

Then one line on **what would move the number most** — usually rightsizing, a savings plan, or turning off non-production overnight. That's the sentence the person who commissioned the document is looking for.

## Call out the surprises

These consistently blindside teams and rarely appear in an estimate. Check whether each applies and say so:

- **NAT Gateway** — hourly per AZ *plus* per-GB processed. A chatty service pulling images through NAT can cost more in NAT than in compute.
- **Data transfer out** to the internet, and **cross-AZ** traffic, which is billed in both directions.
- **CloudWatch / log ingestion** — priced per GB ingested. A debug-level logger left on in production is a genuine budget event.
- **EBS snapshots** accumulating without a lifecycle policy.
- **Idle load balancers and unattached EIPs** — small individually, endless collectively.
- **Provisioned IOPS and `gp3` throughput** bought and never used.
- **Non-production environments** running 24/7. Frequently the largest single saving available.
- **Managed control planes** — EKS charges per cluster-hour before a single pod runs.
- **CI minutes and artifact storage**, which sit in a different bill and get forgotten entirely.

## Per-component cost lines

In the Components section, one line, with the breakdown that makes it checkable:

> **≈$430/mo** — instance $310 + 200GB gp3 $46 + Multi-AZ standby. `us-east-1`, on-demand, as of 2026-03-14.

## Reference anchors

`assets/data/cost-anchors.csv` holds a small set of list prices with region, source URL, and an as-of date, for sanity-checking an order of magnitude. It is a smell test, not a source: it goes stale, it covers a fraction of the catalogue, and it must never be presented to a user as current pricing. If a figure from a real source disagrees with it, the real source wins and the anchor file is out of date.
