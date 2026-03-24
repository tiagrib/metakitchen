#!/usr/bin/env python3
"""
metak - MetaKitchen sub-repo initializer

Usage:
    python metak.py <folder-name>

Adds an existing submodule folder to meta.code-workspace and scaffolds
the MetaKitchen agent structure (AGENTS.md) if not already present.

Prerequisites:
    - Python 3.7+
    - No additional packages required

Example:
    git submodule add https://github.com/your-org/frontend frontend
    python metak.py frontend
"""

import argparse
import json
import sys
from pathlib import Path


AGENTS_MD_TEMPLATE = """\
# {name} Agent Guide

Repo-specific agent instructions for `{name}`.
Read the root `AGENTS.md` first for global rules, project structure, and coding standards.

## Repo Overview

<!-- Describe what this repo does and its role in the system. -->

## Agent Rules

1. Follow all rules in the root `AGENTS.md`.
2. **Do not modify `shared/`.** Propose changes via the orchestrator for user review.
3. <!-- Add any repo-specific rules here. -->

## Coding Standards

- <!-- Language, framework, and linting conventions specific to this repo. -->
"""


def find_workspace_file(root):
    # type: (Path) -> Path
    matches = sorted(root.glob("*.code-workspace"))
    if not matches:
        raise FileNotFoundError(
            "No .code-workspace file found. Run this script from the meta-repo root."
        )
    if len(matches) > 1:
        names = ", ".join(m.name for m in matches)
        raise ValueError(
            "Multiple .code-workspace files found: {}. "
            "Remove duplicates or rename to a single file.".format(names)
        )
    return matches[0]


def add_to_workspace(workspace_path, folder_name):
    # type: (Path, str) -> bool
    """Add folder to the workspace. Returns True if added, False if already present."""
    text = workspace_path.read_text(encoding="utf-8")
    workspace = json.loads(text)

    folders = workspace.setdefault("folders", [])
    existing = {f.get("path") for f in folders}

    if folder_name in existing:
        return False

    folders.append({"path": folder_name})
    workspace_path.write_text(
        json.dumps(workspace, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return True


def scaffold_agents_md(folder_path, folder_name):
    # type: (Path, str) -> bool
    """Create AGENTS.md in the sub-repo. Returns True if created, False if already existed."""
    target = folder_path / "AGENTS.md"
    if target.exists():
        return False
    target.write_text(
        AGENTS_MD_TEMPLATE.format(name=folder_name),
        encoding="utf-8",
    )
    return True


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Initialize a MetaKitchen sub-repo: "
            "register it in the VS Code workspace and scaffold AGENTS.md."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  git submodule add https://github.com/your-org/frontend frontend\n"
            "  python metak.py frontend\n"
        ),
    )
    parser.add_argument(
        "folder",
        help="Submodule folder name (relative to meta-repo root)",
    )
    args = parser.parse_args()

    folder_name = args.folder.strip("/\\")
    root = Path(__file__).resolve().parent
    folder_path = root / folder_name

    if not folder_path.exists():
        print("Error: '{}' does not exist.".format(folder_name))
        print("Add the git submodule first:")
        print("  git submodule add <url> {}".format(folder_name))
        sys.exit(1)

    if not folder_path.is_dir():
        print("Error: '{}' is not a directory.".format(folder_name))
        sys.exit(1)

    print("Initializing '{}'...".format(folder_name))

    try:
        workspace_path = find_workspace_file(root)
    except (FileNotFoundError, ValueError) as e:
        print("Error: {}".format(e))
        sys.exit(1)

    if add_to_workspace(workspace_path, folder_name):
        print("  [+] Added '{}' to {}".format(folder_name, workspace_path.name))
    else:
        print("  [=] '{}' already in {}".format(folder_name, workspace_path.name))

    if scaffold_agents_md(folder_path, folder_name):
        print("  [+] Created {}/AGENTS.md".format(folder_name))
    else:
        print("  [=] {}/AGENTS.md already exists, skipping".format(folder_name))

    print("\nDone. Open {} in VS Code.".format(workspace_path.name))


if __name__ == "__main__":
    main()
