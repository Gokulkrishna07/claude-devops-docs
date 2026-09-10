# Tests

Standard library only — no test framework dependency, matching the scripts they cover.

```bash
python3 -m unittest discover -s tests -v
```

- `test_safe_inventory.py` — asserts that `.env`, `.tfvars`, and Kubernetes `Secret`
  manifests are listed as present-but-not-read and that none of their contents
  ever reach the scan report, and that Terraform/Kubernetes/CI parsing is correct.
- `test_check_doc.py` — asserts the pre-delivery gate blocks on planted
  credentials and warns on the AI-slop patterns the skill exists to prevent,
  and stays quiet on a clean document.

`tests/fixtures/` contains a small synthetic repo and two sample docs used only
by these tests. All credential-shaped values in them are the well-known AWS
documentation placeholders (`AKIAIOSFODNN7EXAMPLE` etc.) or otherwise inert —
none are real.
