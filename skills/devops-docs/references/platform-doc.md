# Unified platform documentation

When one system spans CI/CD, IaC, config management, and container orchestration — Jenkins plus Terraform plus Ansible plus Kubernetes — produce **one document**, not four. The whole value is in the seams. Four documents describe four tools; one document describes a platform, and the questions that actually get asked ("I changed a variable, why didn't it take effect?") live in the handoffs between tools.

**Read `SAFETY.md` first.** A document spanning this many systems touches every kind of credential store there is.

## Structure

```
1. What this platform is          5 lines
2. Tool map                       who owns what, and the boundaries
3. The big picture                one diagram, all layers
4. Layer by layer                 per tool: purpose, scope, cost
5. The seams                      handoffs between tools ← the reason this doc exists
6. End-to-end walkthrough         one commit, followed all the way to production
7. Operating it                   per-layer, cross-cutting
8. Cost                           whole-platform view
9. Risks and gotchas
```

### 2. Tool map

The orientation table. A new engineer reads this and knows where to look.

| Concern | Tool | Owns | Does NOT own |
|---|---|---|---|
| Cloud resources | Terraform | VPC, EKS, RDS, IAM | anything inside the cluster |
| Cluster workloads | Helm + Argo CD | Deployments, Services, HPA | node provisioning |
| VM config | Ansible | bastion, legacy app servers | anything containerised |
| Build & release | Jenkins | build, test, image push | applying Terraform |
| Runtime | Kubernetes (EKS 1.30) | scheduling, service discovery | |

The **does not own** column prevents the most expensive class of mistake on multi-tool platforms: two tools believing they own the same resource, fighting over it, and reverting each other on every run.

### 3. The big picture

One diagram showing all layers, with the boundary between "what Terraform creates" and "what runs inside it" made visually explicit — nested groups, not colour alone. Number the edges; the walkthrough in section 6 refers to them.

If one diagram genuinely cannot hold it, use two: a **provisioning view** (what creates what) and a **runtime view** (what calls what). Do not go past two — three diagrams means nobody holds the whole thing in their head, which is the problem this document exists to solve.

### 4. Layer by layer

Per tool, kept short because the detail lives in the seams: purpose, what it manages, where its config lives, how it's invoked, and its cost. Two to four lines each. If a layer needs a full page, it deserves its own document and a link from here — use `infrastructure-doc.md` or `pipeline-doc.md` for that.

### 5. The seams

**This is the section that justifies a single document.** Everything else is available elsewhere; this is not written down anywhere in any of the four tools.

For each handoff, document what passes across, in which format, and what happens when it's wrong:

- **Terraform → Kubernetes.** How do cluster credentials get to the deploy tool? Does Terraform write a kubeconfig, or does CI assume a role? What happens to running workloads when Terraform replaces a node group?
- **Terraform → Ansible.** Does the inventory come from a dynamic plugin, from Terraform outputs, from a static file someone edits by hand? A stale static inventory after a Terraform-driven instance replacement is a classic multi-hour outage.
- **CI → Terraform.** Does Jenkins run `apply`? With which role? Is there a plan-review gate, and does anyone read it?
- **CI → Kubernetes.** Push (CI applies) or pull (Argo syncs)? If pull, CI's job ends at the image push and the deploy is asynchronous — say so, because "the pipeline went green but nothing deployed" is otherwise baffling.
- **Ansible ↔ Kubernetes.** If both can touch a host, define the boundary explicitly.
- **Secrets across the seam.** Where each layer gets its credentials, and which layer is authoritative. Name the stores, never the values.

For each seam also state **what happens when it breaks**, because seam failures present as "nothing is wrong" in every individual tool. Argo showing Synced while the image tag never changed is not visible from Jenkins, and Jenkins going green is not visible from Argo.

### 6. End-to-end walkthrough

Follow one commit from `git push` to serving production traffic, naming every tool, every artefact, and every wait. Ten to twenty numbered steps. Include the boring parts — the two-minute image scan, the Argo sync interval, the manual approval — because the boring parts are where people lose track of where their change is.

This section is what a new engineer reads on day one, and it's the fastest way to find out that your own mental model of the platform is wrong.

### 7. Operating it

Cross-cutting, not per-tool. The questions that span layers:

- **Where do I look first?** A decision tree from symptom to layer. "Deploy went green but the change isn't live" → check Argo sync status, not Jenkins.
- **How do I roll back**, at each layer, and which layer to roll back at for a given symptom.
- **What is safe to run concurrently?** Terraform apply during a deploy, Ansible during a rolling update — name the combinations that are unsafe.
- **Change freeze / break-glass procedure**, if one exists.

### 8. Cost

Whole-platform view, per `cost.md`. Include the layers people forget: CI compute and storage, container registry, log ingestion and retention, NAT gateways, and non-production environments — which frequently cost more than production because nothing turns them off at night.

### 9. Risks and gotchas

Platform-level, and mostly seam-level: overlapping ownership, manual steps that survive between two automated ones, a tool version pinned to something unsupported, an environment that drifted and was never reconciled, a single person who is the only one who can run one of the layers.

## Length

This document will want to be long. Hold it to roughly 600 lines by pushing depth into linked documents and keeping the seams section detailed. If the seams section is short and the per-tool sections are long, the document has been written the wrong way round — invert it.
