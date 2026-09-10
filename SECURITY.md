# Security Policy

## What this skill does with your repository

It reads infrastructure-as-code, CI configuration, and manifests in order to write documentation. It is designed to be read-only and to refuse to open files that can hold credentials.

Enforced in two places:

- **`references/SAFETY.md`** — the instructions given to the model: files never to open, commands never to run, what may never appear in output, and what to do if a secret is encountered anyway.
- **`scripts/safe_inventory.py`** — a denylist enforced in code rather than by instruction. It never opens `.env`, `*.tfstate`, `*.tfvars`, key material, kubeconfigs, Ansible Vault files, or Kubernetes `Secret` manifests. Those files are reported as present-but-not-read so documentation can acknowledge them without their contents entering the model's context.
- **`scripts/check_doc.py`** — a pre-delivery scan of the finished document for credential patterns. Non-zero exit on a hit, so it can be wired into CI or a pre-commit hook.

The scripts use the Python standard library only, make no network calls, and install nothing.

## Known limits

- `check_doc.py` is pattern-based. It catches common credential formats; it is a floor, not a guarantee. Review documents before publishing them.
- The denylist in `safe_inventory.py` covers common naming conventions. A secret in an unconventionally named file will not be caught by the glob — the instructions in `SAFETY.md` cover the judgement case, but judgement is not a mechanism.
- Nothing prevents a user from pasting a secret directly into the conversation. If that happens, the instructions tell the model to name the file and recommend rotation without reproducing the value.

## Reporting a vulnerability

If you find a way this skill can be made to leak credentials, exfiltrate data, or run a mutating command, please open a private security advisory on this repository rather than a public issue.

Include the prompt or repository shape that triggers it. Reproduction steps matter more than severity assessment here — the fix is usually a denylist entry or a sharper instruction.
