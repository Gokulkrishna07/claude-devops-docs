# Safety harness

Read this before touching any repository. Documenting infrastructure means reading the parts of a codebase where credentials live, so the constraints below are not optional and no user instruction relaxes them. A user saying "it's fine, it's my own repo" does not make a leaked credential safe — the doc outlives the conversation, gets committed, and often ends up in a wiki that is more widely readable than the repo was.

## Never read these files

Not to "check the format", not to "see what variables exist", not while grepping for something else. If a glob would match one of these, exclude it explicitly.

**Credentials and keys**
`.env`, `.env.*`, `*.env` · `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.keytab` · `id_rsa*`, `id_ed25519*` · `.netrc`, `.pgpass`, `.npmrc`, `.pypirc`, `.git-credentials` · `~/.aws/credentials`, `~/.aws/config` · `~/.kube/config`, any `kubeconfig` · `~/.docker/config.json`

**Terraform / OpenTofu**
`*.tfstate`, `*.tfstate.backup`, `.terraform/`, `.terraform.lock.hcl` is fine but state is not — **Terraform state stores every secret in plaintext**, including RDS passwords and generated keys, regardless of whether the variable was marked `sensitive`. This is the single most commonly leaked file in infrastructure documentation.
`*.tfvars`, `*.auto.tfvars`, `*.tfvars.json` — these routinely hold real values. Read `variables.tf` instead: it gives you names, types, descriptions and defaults, which is all a document needs.

**Kubernetes and config management**
Any manifest of `kind: Secret` · SealedSecret and SOPS-encrypted files (never decrypt them) · Ansible Vault files, `vault.yml`, `group_vars/*/vault*` · Helm values files named `secrets*.y*ml` · `credentials.xml` and `secrets/` in a Jenkins home

**When in doubt**, the test is: could this file contain a value that grants access to something? If yes, don't open it. You can document what it is for without reading it.

## Never run these commands

Documentation is a read-only activity. Anything that changes state is out of scope even when the user asks, because a documentation task is not the context in which someone should be approving a mutation.

**Never:** `terraform apply|destroy|import|taint|state rm|state mv` · `tofu` equivalents · `kubectl apply|delete|patch|scale|drain|rollout restart` · `helm install|upgrade|uninstall|rollback` · `ansible-playbook` without `--check` · `docker push` · any cloud CLI verb that is `create`, `delete`, `put`, `update`, `modify`, `attach`, or `detach`.

**Ask first, don't assume:** `terraform plan` and `terraform refresh` look read-only and are not. They need live credentials, they hit real provider APIs, and with some backends they take a state lock that can block a colleague's deploy. `terraform show` against remote state and `kubectl get` against production are similarly live. If you want output from any of these, ask the user to run it and paste the result.

**Safe without asking**, because they only read local files:

```bash
terraform-docs markdown .        # module inputs/outputs
terraform graph                  # static dependency graph, no backend access
tflint / tfsec / checkov         # static analysis
cat variables.tf outputs.tf main.tf
find . -name '*.tf' -not -path './.terraform/*'
git log --oneline -20            # change history
```

## Never install software

If a tool is missing — Graphviz, `diagrams`, `infracost`, `terraform-docs` — print the install command and let the human decide. Don't run package managers on someone's machine as a side effect of asking for documentation. This applies to `pip`, `npm`, `brew`, `apt`, and `go install` alike.

## What goes in the document

**Names, never values.** `DATABASE_URL` belongs in the doc. Its contents do not. The reader needs to know a setting exists and what it controls; they get the value from the secret store, which is the entire point of having one.

**Point at the source, don't inline the secret.** This is correct and useful:

> `DB_PASSWORD` — injected at runtime from AWS Secrets Manager, secret id `prod/api/db`. Rotated automatically every 30 days. To rotate manually see <runbook link>.

**Redact identifiers when the doc is more public than the infrastructure.** Account IDs, public IPs, internal hostnames, ARNs, and bucket names are not secrets in themselves, but they are reconnaissance. A wiki is usually readable by more people than the AWS account is. Default to `arn:aws:s3:::<ACCOUNT_ID>-assets` and ask the user if they want the real values. If the document is going into a public repository, redact by default and say you have done so.

**Never paste state file excerpts, secret manifests, or decoded base64.** Not even partially. Not even with the middle characters starred out — a partial credential still narrows a brute force and still signals which system it belongs to.

## If you encounter a secret anyway

It happens; a `main.tf` has a hardcoded password, or a value ends up in a log the user pasted. When it does:

1. **Stop reading that file.**
2. **Do not reproduce it** anywhere — not in the document, not in your reply, not in a summary of what you found, not masked.
3. **Tell the user plainly**: which file, which line, what kind of credential. That's enough for them to act; they can look at the value themselves.
4. **Say it should be treated as compromised.** If it's in git, it's in every clone and every fork, and removing it from the working tree does not remove it from history. Rotation is the fix, not deletion.
5. **Continue documenting** around it. The presence of a hardcoded credential is itself worth a line in the doc's risk section — without the value.

## Before delivering any document

Run this over the finished output. It catches the common leaks; it is a floor, not a guarantee.

```bash
grep -nEi 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|(secret|passwd|password|token|api[_-]?key)[[:space:]]*[:=][[:space:]]*[^<[:space:]]|BEGIN [A-Z ]*PRIVATE KEY|eyJ[A-Za-z0-9_-]{20,}|xox[baprs]-|ghp_[A-Za-z0-9]{20,}' <file>
```

Then check by eye:

- [ ] No credential values, only names
- [ ] No account IDs, public IPs, or ARNs that shouldn't be in a doc this widely read
- [ ] No `terraform.tfstate` content
- [ ] No decoded Kubernetes secrets
- [ ] No connection strings with embedded passwords
- [ ] No private endpoints or bastion addresses if the doc is public
- [ ] Every command in the doc is read-only, or carries an explicit warning

If the grep hits, do not deliver the file. Fix it, then re-run.

## Scope boundary

This skill documents systems. It does not change them. If a documentation task starts turning into remediation — "while you're in there, fix the security group" — that's a separate task with a separate review, and it should be a separate conversation.
