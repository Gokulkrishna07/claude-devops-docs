# Architecture diagrams

A wrong diagram is worse than no diagram, because people plan against it. So: generate diagrams from a checked-in spec, never hand-place boxes in a tool nobody else can open.

## Workflow

1. Write `docs/architecture.yaml` — see `assets/templates/architecture.example.yaml`.
2. Render: `python3 scripts/gen_diagram.py docs/architecture.yaml -o docs/architecture`
3. Commit both the spec and the image. The spec is reviewable in a pull request; the image is what people look at.

The spec being in version control is the point. When the infrastructure changes, the diagram changes in the same PR, and a reviewer can see the delta.

## Two backends

**`--backend diagrams`** (default) produces the provider-icon PNG/SVG style used by AWS, GCP, and Azure reference architectures: official service icons, nested dashed boundaries for VPCs and accounts, numbered edges. Use this for infrastructure. Needs the `diagrams` package and Graphviz — if either is missing the script prints the install command and stops. **Never install them yourself**; ask the user.

**`--backend mermaid`** produces Mermaid flowchart text with no dependencies at all. Renders natively in GitHub, GitLab, and most wikis. Use it for pipelines and sequence-style flows, or whenever the dependencies aren't available.

Node types are paths into the `diagrams` package — `aws.compute.Lambda`, `gcp.database.SQL`, `azure.web.AppServices`, `k8s.compute.Deployment`, `onprem.ci.Jenkins`. The full catalogue is at diagrams.mingrammer.com/docs/nodes/aws. Omit `type` for a plain labelled box.

## What makes a diagram readable

**Number the edges.** Numbered callouts are how every good cloud reference architecture works: the diagram carries the topology, the prose beneath explains each numbered hop. Without numbers, prose has to re-describe the topology in words, which is where architecture documents become unreadable.

**Show boundaries as nesting, not colour.** VPC inside account inside cloud. Boundaries are the thing a reader cannot infer from a resource list, and they are the first thing a security reviewer looks for.

**One diagram, one question.** A diagram answering "how does a request flow" and "how is this provisioned" simultaneously answers neither. Split by question, not by size.

**Cap it at roughly 15 nodes.** Past that, comprehension drops sharply. Group and abstract: "3 × app node" is one node. If you cannot get under 15, you are drawing the wrong level.

**Left-to-right for flows, top-to-bottom for hierarchies.** `direction: LR` for request paths and pipelines; `TB` for org or dependency structure.

**Skip what doesn't carry risk.** Every subnet, route table, and security group on one canvas produces something nobody reads. Draw what fails, what costs money, and what holds state.

## Rendering elsewhere

If neither backend fits — the user has an existing draw.io library, or a Structurizr/C4 model — use their tool. The rules above are about the diagram, not the renderer. What matters is that the source is text, in the repo, and regenerable.

## Keeping it true

Put the regeneration command in the doc, right under the image:

```markdown
<!-- Regenerate: python3 scripts/gen_diagram.py docs/architecture.yaml -o docs/architecture -->
![Architecture](architecture.png)
```

A diagram nobody knows how to regenerate is a diagram that will be wrong within two months.
