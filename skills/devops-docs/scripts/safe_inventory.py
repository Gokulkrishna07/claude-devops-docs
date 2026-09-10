#!/usr/bin/env python3
"""
safe_inventory.py - inventory an infrastructure repo without touching secrets.

Walks a repository, classifies the files that matter for documentation, and
extracts a static summary. Files that can hold credentials are NEVER opened -
they are reported as "present, not read" so the document can acknowledge they
exist without their contents entering context.

Standard library only. No network. Reads nothing outside the given path.
Writes nothing anywhere.

Usage:
    python3 safe_inventory.py /path/to/repo
    python3 safe_inventory.py /path/to/repo --json
"""

import argparse
import fnmatch
import json
import os
import re
import sys
from collections import defaultdict

# Files that may contain credentials. Never opened. See references/SAFETY.md.
DENY = [
    ".env", ".env.*", "*.env",
    "*.tfstate", "*.tfstate.*", "*.tfvars", "*.auto.tfvars", "*.tfvars.json",
    "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore", "*.keytab",
    "id_rsa*", "id_ed25519*", "id_dsa*",
    ".netrc", ".pgpass", ".npmrc", ".pypirc", ".git-credentials",
    "credentials", "credentials.xml", "kubeconfig", "*.kubeconfig",
    "vault.yml", "vault.yaml", "*vault*.yml", "*vault*.yaml",
    "secret*.yml", "secret*.yaml", "*secrets.yml", "*secrets.yaml",
    "*.dec.yaml", "*.sops.yaml", "*.sops.yml",
]

DENY_DIRS = [".terraform", ".git", "node_modules", ".venv", "venv", "__pycache__", "secrets"]

# Order matters: specific patterns first, the generic YAML catch-all last,
# or CI and Helm files get swallowed by the Kubernetes matcher.
CLASSIFY = [
    ("ci-github",  [".github/workflows/*.y*ml"]),
    ("ci-gitlab",  [".gitlab-ci.yml", ".gitlab-ci.*.yml"]),
    ("ci-jenkins", ["Jenkinsfile", "Jenkinsfile.*", "*.jenkinsfile"]),
    ("ci-circle",  [".circleci/config.yml"]),
    ("docker",     ["Dockerfile", "Dockerfile.*", "docker-compose*.y*ml"]),
    ("helm",       ["Chart.yaml", "values*.y*ml"]),
    ("terraform",  ["*.tf", "*.tf.json"]),
    ("terragrunt", ["terragrunt.hcl"]),
    ("cdk",        ["cdk.json", "*-stack.ts", "*_stack.py"]),
    ("pulumi",     ["Pulumi.yaml", "Pulumi.*.yaml"]),
    ("ansible",    ["playbook*.y*ml", "site.y*ml", "*/roles/*/tasks/*.y*ml", "ansible.cfg", "inventory*"]),
    ("argocd",     ["application*.y*ml", "applicationset*.y*ml"]),
    ("makefile",   ["Makefile", "Taskfile.y*ml", "justfile"]),
    ("kubernetes", ["*.yaml", "*.yml"]),   # catch-all, confirmed by a `kind:` sniff
]

TF_RESOURCE = re.compile(r'^\s*resource\s+"([^"]+)"\s+"([^"]+)"', re.M)
TF_MODULE = re.compile(r'^\s*module\s+"([^"]+)"', re.M)
TF_VARIABLE = re.compile(r'^\s*variable\s+"([^"]+)"', re.M)
TF_OUTPUT = re.compile(r'^\s*output\s+"([^"]+)"', re.M)
TF_BACKEND = re.compile(r'backend\s+"([^"]+)"')
TF_REQUIRED = re.compile(r'required_version\s*=\s*"([^"]+)"')
K8S_KIND = re.compile(r'^kind:\s*([A-Za-z]+)', re.M)
ENV_REF = re.compile(r'^\s*-?\s*(?:name:\s*)?([A-Z][A-Z0-9_]{3,})\s*[:=]', re.M)


def is_denied(name):
    return any(fnmatch.fnmatch(name, pat) for pat in DENY)


def classify(relpath, name):
    for label, patterns in CLASSIFY:
        for pat in patterns:
            if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(relpath, pat) or fnmatch.fnmatch(relpath, "*/" + pat):
                return label
    return None


def read(path, limit=400_000):
    try:
        with open(path, "r", errors="replace") as fh:
            return fh.read(limit)
    except (OSError, UnicodeDecodeError):
        return ""


def scan(root):
    result = {
        "root": os.path.abspath(root),
        "skipped_sensitive": [],
        "by_type": defaultdict(list),
        "terraform": {
            "resources": defaultdict(int),
            "modules": [],
            "variables": [],
            "outputs": [],
            "backend": None,
            "required_version": None,
        },
        "kubernetes_kinds": defaultdict(int),
        "config_names": set(),
        "notes": [],
    }

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in DENY_DIRS]
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)

            if is_denied(name):
                result["skipped_sensitive"].append(rel)
                continue

            kind = classify(rel, name)
            if not kind:
                continue

            if kind == "kubernetes":
                body = read(full)
                kinds = K8S_KIND.findall(body)
                if not kinds:
                    continue
                if "Secret" in kinds:
                    result["skipped_sensitive"].append(rel + "  (kind: Secret)")
                    continue
                for k in kinds:
                    result["kubernetes_kinds"][k] += 1
                result["by_type"][kind].append(rel)
                continue

            result["by_type"][kind].append(rel)

            if kind == "terraform":
                body = read(full)
                tf = result["terraform"]
                for rtype, _ in TF_RESOURCE.findall(body):
                    tf["resources"][rtype] += 1
                tf["modules"] += TF_MODULE.findall(body)
                tf["variables"] += TF_VARIABLE.findall(body)
                tf["outputs"] += TF_OUTPUT.findall(body)
                m = TF_BACKEND.search(body)
                if m and not tf["backend"]:
                    tf["backend"] = m.group(1)
                m = TF_REQUIRED.search(body)
                if m and not tf["required_version"]:
                    tf["required_version"] = m.group(1)

            if kind in ("docker", "ci-github", "ci-gitlab", "ci-jenkins", "helm"):
                for var in ENV_REF.findall(read(full, 60_000)):
                    result["config_names"].add(var)

    result["by_type"] = dict(result["by_type"])
    result["terraform"]["resources"] = dict(result["terraform"]["resources"])
    result["terraform"]["modules"] = sorted(set(result["terraform"]["modules"]))
    result["terraform"]["variables"] = sorted(set(result["terraform"]["variables"]))
    result["terraform"]["outputs"] = sorted(set(result["terraform"]["outputs"]))
    result["kubernetes_kinds"] = dict(result["kubernetes_kinds"])
    result["config_names"] = sorted(result["config_names"])
    return result


def report(r):
    out = []
    add = out.append
    add(f"Inventory: {r['root']}\n")

    if r["by_type"]:
        add("Tooling present")
        for kind, files in sorted(r["by_type"].items()):
            add(f"  {kind:<12} {len(files):>3} file(s)   e.g. {files[0]}")
        add("")

    tf = r["terraform"]
    if tf["resources"]:
        add("Terraform / OpenTofu")
        if tf["required_version"]:
            add(f"  required_version: {tf['required_version']}")
        if tf["backend"]:
            add(f"  backend: {tf['backend']}")
        add(f"  {sum(tf['resources'].values())} resources across {len(tf['resources'])} types:")
        for rtype, n in sorted(tf["resources"].items(), key=lambda x: -x[1])[:25]:
            add(f"    {n:>3}  {rtype}")
        if tf["modules"]:
            add(f"  modules: {', '.join(tf['modules'][:15])}")
        add(f"  {len(tf['variables'])} variables, {len(tf['outputs'])} outputs")
        add("")

    if r["kubernetes_kinds"]:
        add("Kubernetes manifests")
        for kind, n in sorted(r["kubernetes_kinds"].items(), key=lambda x: -x[1]):
            add(f"  {n:>3}  {kind}")
        add("")

    if r["config_names"]:
        add(f"Configuration keys referenced ({len(r['config_names'])}) — names only, no values read")
        add("  " + ", ".join(r["config_names"][:40]))
        if len(r["config_names"]) > 40:
            add(f"  … and {len(r['config_names']) - 40} more")
        add("")

    if r["skipped_sensitive"]:
        add(f"NOT READ — may contain credentials ({len(r['skipped_sensitive'])})")
        for path in r["skipped_sensitive"][:30]:
            add(f"  {path}")
        if len(r["skipped_sensitive"]) > 30:
            add(f"  … and {len(r['skipped_sensitive']) - 30} more")
        add("")
        add("  These exist and may matter to the document. Reference them by name")
        add("  and purpose. Do not open them. See references/SAFETY.md.")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Inventory an infra repo without reading secrets.")
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.path):
        sys.exit(f"Not a directory: {args.path}")

    result = scan(args.path)
    print(json.dumps(result, indent=2) if args.json else report(result))


if __name__ == "__main__":
    main()
