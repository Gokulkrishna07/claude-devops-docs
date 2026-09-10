#!/usr/bin/env python3
"""
check_doc.py - pre-delivery check on a finished document.

Scans for leaked credentials and for the AI-slop patterns this skill exists to
prevent. Exits non-zero if anything blocking is found, so it can be wired into
CI or a pre-commit hook.

Standard library only. No network. Read-only.

Usage:
    python3 check_doc.py docs/infrastructure.md
    python3 check_doc.py docs/*.md --strict     # style warnings also fail
"""

import argparse
import re
import sys

# Blocking: never ship a document containing these.
SECRETS = [
    ("AWS access key id",       re.compile(r'\b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}\b')),
    ("AWS secret access key",   re.compile(r'(?i)aws_secret_access_key\s*[:=]\s*\S{20,}')),
    ("Private key block",       re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY')),
    ("GitHub token",            re.compile(r'\bgh[pousr]_[A-Za-z0-9]{16,}\b')),
    ("Slack token",             re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b')),
    ("Google API key",          re.compile(r'\bAIza[0-9A-Za-z_-]{35}\b')),
    ("JWT",                     re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.')),
    ("Connection string w/ password",
     re.compile(r'(?i)\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s:@/]+:[^\s@/]+@')),
    ("Assigned secret value",
     re.compile(r'(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\b'
                r'\s*[:=]\s*["\']?(?!<|\$\{|\*{3}|REDACTED|TODO|null|None|""|\'\')[^\s"\',<>{}]{8,}')),
    ("Terraform state fragment", re.compile(r'"terraform_version"\s*:|"lineage"\s*:\s*"')),
    ("Base64 data blob in k8s secret", re.compile(r'(?m)^\s*data:\s*$\n(?:\s+\S+:\s*[A-Za-z0-9+/]{24,}={0,2}\s*$)')),
]

# Warnings: signs of generated filler rather than documentation.
SLOP = [
    ("Tool tutorial",       re.compile(r'(?i)\b(?:Docker|Kubernetes|Terraform|Git|CI/CD|Jenkins) is an? (?:open[- ]source )?(?:platform|tool|system|technology)\b')),
    ("Empty prerequisites", re.compile(r'(?i)prerequisites?:?\s*\n+\s*[-*]?\s*(?:basic|familiarity|a computer|internet connection|access to a terminal)')),
    ("Generic best practices heading", re.compile(r'(?im)^#{1,4}\s*(?:best practices|general (?:tips|guidelines)|security considerations)\s*$')),
    ("Conclusion section",  re.compile(r'(?im)^#{1,4}\s*(?:conclusion|summary|final thoughts|wrapping up)\s*$')),
    ("Filler opener",       re.compile(r"(?i)in today's (?:fast[- ]paced|modern|digital)")),
    ("Vague follow-up",     re.compile(r'(?i)if the (?:issue|problem) persists,? (?:investigate further|contact support|try again)')),
    ("Unfilled placeholder", re.compile(r'(?i)\b(?:your-namespace|your-cluster|example\.com/your|my-app|foo-bar)\b')),
    ("Undated cost figure", re.compile(r'(?m)^(?=.*[≈~$])(?=.*\d)(?!.*(?:as of|20\d\d-\d\d-\d\d)).*\$\s?\d[\d,]*(?:\.\d+)?\s*(?:/\s*(?:mo|month|hr|hour))')),
]

REQUIRED_HINTS = [
    ("no owner named",     re.compile(r'(?i)\bowner\b|\bon-?call\b|\bescalat')),
    ("no verification date", re.compile(r'(?i)last (?:verified|updated)|as of \d{4}')),
]


def check(path, strict=False):
    try:
        with open(path, errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"  cannot read: {exc}")
        return 1

    lines = text.splitlines()
    blocking, warnings = [], []

    for label, pattern in SECRETS:
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            blocking.append((line_no, label, lines[line_no - 1][:80] if line_no <= len(lines) else ""))

    for label, pattern in SLOP:
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            warnings.append((line_no, label, lines[line_no - 1][:80] if line_no <= len(lines) else ""))

    for label, pattern in REQUIRED_HINTS:
        if not pattern.search(text):
            warnings.append((0, label, ""))

    print(f"\n{path}")
    if blocking:
        print(f"  BLOCKING — {len(blocking)} possible credential(s). Do not deliver this file.")
        for line_no, label, snippet in blocking:
            print(f"    line {line_no}: {label}")
            print(f"      {snippet.strip()[:70]}")
    if warnings:
        print(f"  {len(warnings)} warning(s):")
        for line_no, label, snippet in warnings:
            where = f"line {line_no}" if line_no else "document"
            print(f"    {where}: {label}")
    if not blocking and not warnings:
        print("  clean")

    if blocking:
        return 2
    if warnings and strict:
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description="Check a document before delivering it.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--strict", action="store_true", help="fail on style warnings too")
    args = ap.parse_args()

    worst = 0
    for path in args.paths:
        worst = max(worst, check(path, args.strict))

    if worst >= 2:
        print("\nFAILED: possible credentials in output. Fix and re-run before delivering.")
    elif worst == 1:
        print("\nFAILED (strict): style warnings present.")
    else:
        print("\nOK to deliver.")
    return worst


if __name__ == "__main__":
    sys.exit(main())
