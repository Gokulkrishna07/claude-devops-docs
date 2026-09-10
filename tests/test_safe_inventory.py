#!/usr/bin/env python3
"""
Tests for scripts/safe_inventory.py.

Verifies the safety guarantee the whole skill depends on: files that can hold
credentials are never opened, and their contents never end up in the scan
result. Run with:

    python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "devops-docs", "scripts")
FIXTURE_REPO = os.path.join(ROOT, "tests", "fixtures", "sample_repo")

sys.path.insert(0, SCRIPTS)
import safe_inventory  # noqa: E402


class SafeInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = safe_inventory.scan(FIXTURE_REPO)
        cls.report = safe_inventory.report(cls.result)

    def test_env_file_is_never_read(self):
        skipped = self.result["skipped_sensitive"]
        self.assertTrue(any(p == ".env" for p in skipped))
        self.assertNotIn("AKIAFAKEEXAMPLE1234", self.report)
        self.assertNotIn("hunter2", self.report)

    def test_tfvars_is_never_read(self):
        skipped = self.result["skipped_sensitive"]
        self.assertTrue(any(p == "terraform.tfvars" for p in skipped))
        self.assertNotIn("S3cretPassw0rd", self.report)

    def test_kubernetes_secret_is_never_read(self):
        # Caught by the filename deny-list ("secret*.yaml") before the YAML
        # is ever opened to sniff its `kind:` — belt and suspenders.
        skipped_labels = " ".join(self.result["skipped_sensitive"])
        self.assertIn("secret.yaml", skipped_labels)
        self.assertNotIn("db-credentials", self.report)
        # A Secret manifest must never be counted as an ordinary manifest.
        self.assertNotIn("Secret", self.result["kubernetes_kinds"])

    def test_terraform_resources_are_parsed(self):
        tf = self.result["terraform"]
        self.assertEqual(tf["resources"].get("aws_instance"), 2)
        self.assertEqual(tf["resources"].get("aws_s3_bucket"), 1)
        self.assertIn("environment", tf["variables"])
        self.assertIn("web_ip", tf["outputs"])
        self.assertEqual(tf["backend"], "s3")

    def test_kubernetes_deployment_is_counted(self):
        self.assertEqual(self.result["kubernetes_kinds"].get("Deployment"), 1)

    def test_ci_workflow_is_classified(self):
        self.assertIn("ci-github", self.result["by_type"])
        self.assertTrue(
            any(p.endswith("deploy.yml") for p in self.result["by_type"]["ci-github"])
        )

    def test_no_secret_values_anywhere_in_report_or_json(self):
        import json

        blob = self.report + json.dumps(self.result, default=list)
        for leaked in ("AKIAFAKEEXAMPLE1234", "hunter2", "S3cretPassw0rd"):
            self.assertNotIn(leaked, blob)


if __name__ == "__main__":
    unittest.main()
