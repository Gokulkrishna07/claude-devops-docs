#!/usr/bin/env python3
"""
gen_diagram.py - render an architecture spec into a diagram.

Two backends:

  --backend diagrams  (default)  Provider-icon PNG/SVG, the style used by AWS
                                 solution reference architectures. Requires the
                                 `diagrams` Python package and the Graphviz
                                 `dot` binary.

  --backend mermaid              Mermaid flowchart text. Standard library only,
                                 no dependencies, renders in GitHub/GitLab.

This script NEVER installs anything and NEVER touches the network. If a
dependency is missing it prints the command for the human to run and exits.

Usage:
    python3 gen_diagram.py architecture.yaml
    python3 gen_diagram.py architecture.yaml --backend mermaid -o docs/arch.mmd
    python3 gen_diagram.py architecture.yaml --format svg -o docs/architecture

Spec format: see assets/templates/architecture.example.yaml
"""

import argparse
import importlib
import os
import sys

MISSING_DEPS = """
Cannot render with the 'diagrams' backend - {what} is missing.

This script will not install anything on your machine. Run one of these
yourself, then re-run the command:

    pip install diagrams
    # Graphviz is a system package, not a Python one:
    #   macOS          brew install graphviz
    #   Debian/Ubuntu  sudo apt-get install graphviz
    #   Fedora         sudo dnf install graphviz
    #   Windows        winget install graphviz

Or render without any dependencies:

    python3 gen_diagram.py {spec} --backend mermaid
"""


# --------------------------------------------------------------------------
# Spec loading
# --------------------------------------------------------------------------

def load_spec(path):
    try:
        import yaml
    except ImportError:
        sys.exit(
            "PyYAML is required to read the spec file.\n"
            "Install it yourself with:  pip install pyyaml\n"
            "This script does not install packages."
        )
    with open(path) as fh:
        spec = yaml.safe_load(fh)
    if not isinstance(spec, dict):
        sys.exit(f"{path}: expected a YAML mapping at the top level.")
    return spec


def walk_groups(container):
    """Yield every group dict in the spec, depth first."""
    for group in container.get("groups", []) or []:
        yield group
        yield from walk_groups(group)


def collect_nodes(spec):
    """Return {node_id: node_dict} across the whole spec."""
    found = {}

    def take(container):
        for node in container.get("nodes", []) or []:
            nid = node.get("id")
            if not nid:
                sys.exit(f"Every node needs an 'id'. Offending node: {node}")
            if nid in found:
                sys.exit(f"Duplicate node id: {nid}")
            found[nid] = node

    take(spec)
    for group in walk_groups(spec):
        take(group)
    return found


def validate(spec):
    """Fail loudly on a malformed spec rather than emitting a wrong diagram."""
    nodes = collect_nodes(spec)
    if not nodes:
        sys.exit("Spec contains no nodes.")
    for edge in spec.get("edges", []) or []:
        for end in ("from", "to"):
            if end not in edge:
                sys.exit(f"Edge missing '{end}': {edge}")
            if edge[end] not in nodes:
                sys.exit(
                    f"Edge references unknown node id '{edge[end]}'.\n"
                    f"Known ids: {', '.join(sorted(nodes))}"
                )
    return nodes


# --------------------------------------------------------------------------
# Backend: diagrams (provider icons)
# --------------------------------------------------------------------------

def resolve_icon(type_path):
    """
    Turn 'aws.network.CloudFront' into the diagrams class.

    Dynamic import rather than a hardcoded map, so any node the installed
    version of `diagrams` supports works without changing this script.
    """
    if not type_path:
        from diagrams.generic.blank import Blank
        return Blank
    parts = type_path.split(".")
    if len(parts) < 2:
        sys.exit(
            f"Node type '{type_path}' is not a valid path.\n"
            "Use provider.category.ClassName, e.g. aws.compute.Lambda"
        )
    module_name = "diagrams." + ".".join(parts[:-1])
    class_name = parts[-1]
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        sys.exit(
            f"Unknown node type '{type_path}' - no module {module_name}.\n"
            "Browse valid node types at https://diagrams.mingrammer.com/docs/nodes/aws"
        )
    try:
        return getattr(module, class_name)
    except AttributeError:
        sys.exit(f"Module {module_name} has no node class '{class_name}'.")


def render_diagrams(spec, out_path, fmt):
    try:
        from diagrams import Cluster, Diagram, Edge
    except ImportError:
        sys.exit(MISSING_DEPS.format(what="the 'diagrams' package", spec="<spec>"))

    import shutil
    if not shutil.which("dot"):
        sys.exit(MISSING_DEPS.format(what="the Graphviz 'dot' binary", spec="<spec>"))

    built = {}

    graph_attr = {
        "fontsize": "16",
        "bgcolor": "white",
        "pad": "0.6",
        "splines": "ortho",
        "nodesep": "0.7",
        "ranksep": "1.1",
    }
    graph_attr.update(spec.get("graph_attr", {}) or {})

    cluster_attr = {
        "fontsize": "14",
        "style": "dashed",
        "pencolor": "#5a6b7b",
        "labeljust": "c",
    }

    def build_nodes(container):
        for node in container.get("nodes", []) or []:
            icon = resolve_icon(node.get("type"))
            label = node.get("label", node["id"])
            built[node["id"]] = icon(label)

    def build_groups(container):
        for group in container.get("groups", []) or []:
            attrs = dict(cluster_attr)
            attrs.update(group.get("attr", {}) or {})
            with Cluster(group.get("name", ""), graph_attr=attrs):
                build_nodes(group)
                build_groups(group)

    with Diagram(
        spec.get("title", "Architecture"),
        filename=out_path,
        outformat=fmt,
        show=False,
        direction=spec.get("direction", "LR"),
        graph_attr=graph_attr,
    ):
        build_nodes(spec)
        build_groups(spec)

        for edge in spec.get("edges", []) or []:
            style = {}
            if edge.get("label"):
                style["label"] = f"  {edge['label']}  "
            if edge.get("style"):
                style["style"] = edge["style"]
            if edge.get("color"):
                style["color"] = edge["color"]
            if edge.get("bidirectional"):
                style["forward"] = True
                style["reverse"] = True
            built[edge["from"]] >> Edge(**style) >> built[edge["to"]]

    return f"{out_path}.{fmt}"


# --------------------------------------------------------------------------
# Backend: mermaid (no dependencies)
# --------------------------------------------------------------------------

def render_mermaid(spec, out_path):
    direction = {"LR": "LR", "TB": "TB", "RL": "RL", "BT": "BT"}.get(
        spec.get("direction", "LR"), "LR"
    )
    lines = [f"flowchart {direction}"]

    def safe(text):
        return str(text).replace('"', "'")

    def emit_nodes(container, indent):
        for node in container.get("nodes", []) or []:
            lines.append(f'{indent}{node["id"]}["{safe(node.get("label", node["id"]))}"]')

    def emit_groups(container, indent, counter=[0]):
        for group in container.get("groups", []) or []:
            counter[0] += 1
            sid = f"sg{counter[0]}"
            lines.append(f'{indent}subgraph {sid}["{safe(group.get("name", ""))}"]')
            emit_nodes(group, indent + "    ")
            emit_groups(group, indent + "    ", counter)
            lines.append(f"{indent}end")

    emit_nodes(spec, "    ")
    emit_groups(spec, "    ")

    for edge in spec.get("edges", []) or []:
        arrow = "<-->" if edge.get("bidirectional") else "-->"
        if edge.get("label"):
            lines.append(f'    {edge["from"]} {arrow}|"{safe(edge["label"])}"| {edge["to"]}')
        else:
            lines.append(f'    {edge["from"]} {arrow} {edge["to"]}')

    path = out_path if out_path.endswith((".mmd", ".md")) else out_path + ".mmd"
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Render an architecture spec to a diagram.")
    ap.add_argument("spec", help="Path to the architecture YAML spec")
    ap.add_argument("--backend", choices=["diagrams", "mermaid"], default="diagrams")
    ap.add_argument("--format", default="png", choices=["png", "svg", "pdf"])
    ap.add_argument("-o", "--output", help="Output path without extension")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    validate(spec)

    out = args.output or spec.get("output") or "architecture"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    if args.backend == "mermaid":
        written = render_mermaid(spec, out)
    else:
        written = render_diagrams(spec, out, args.format)

    print(f"Wrote {written}")


if __name__ == "__main__":
    main()
