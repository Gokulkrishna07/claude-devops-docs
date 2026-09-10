#!/usr/bin/env python3
"""
Tests for scripts/check_doc.py.

Verifies the pre-delivery gate actually blocks on credentials and warns on
the slop patterns the skill exists to prevent, on a clean doc it stays quiet.
Run with:

    python3 -m unittest discover -s tests -v
"""

import contextlib
import io
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "devops-docs", "scripts")
FIXTURE_DOCS = os.path.join(ROOT, "tests", "fixtures", "docs")

sys.path.insert(0, SCRIPTS)
import check_doc  # noqa: E402


def run_check(path, strict=False):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = check_doc.check(path, strict=strict)
    return code, buf.getvalue()


class CheckDocTests(unittest.TestCase):
    def test_good_doc_passes_clean(self):
        code, output = run_check(os.path.join(FIXTURE_DOCS, "good_doc.md"))
        self.assertEqual(code, 0)
        self.assertIn("clean", output)

    def test_good_doc_passes_strict(self):
        code, _ = run_check(os.path.join(FIXTURE_DOCS, "good_doc.md"), strict=True)
        self.assertEqual(code, 0)

    def test_bad_doc_blocks_on_credentials(self):
        code, output = run_check(os.path.join(FIXTURE_DOCS, "bad_doc.md"))
        self.assertEqual(code, 2)
        self.assertIn("BLOCKING", output)
        self.assertIn("AWS access key id", output)
        self.assertIn("AWS secret access key", output)

    def test_blocking_findings_never_print_secret_values(self):
        # check_doc.py must not do the thing it exists to prevent: putting a
        # credential value in its own output, even partially.
        _, output = run_check(os.path.join(FIXTURE_DOCS, "bad_doc.md"))
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", output)
        self.assertNotIn("wJalrXUtnFEMI", output)
        self.assertIn("values withheld", output)

    def test_bad_doc_warns_on_slop_patterns(self):
        _, output = run_check(os.path.join(FIXTURE_DOCS, "bad_doc.md"))
        for label in (
            "Tool tutorial",
            "Empty prerequisites",
            "Generic best practices heading",
            "Conclusion section",
            "Filler opener",
            "Undated cost figure",
        ):
            self.assertIn(label, output)

    def test_dated_cost_table_is_not_flagged(self):
        # A date stated once above a table of prices should cover every row,
        # not just the one line it's adjacent to.
        code, output = run_check(os.path.join(FIXTURE_DOCS, "dated_cost_header.md"))
        self.assertEqual(code, 0)
        self.assertNotIn("Undated cost figure", output)

    def test_missing_file_reports_error_without_crash(self):
        code, output = run_check(os.path.join(FIXTURE_DOCS, "does_not_exist.md"))
        self.assertEqual(code, 1)
        self.assertIn("cannot read", output)


if __name__ == "__main__":
    unittest.main()
