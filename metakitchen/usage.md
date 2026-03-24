# Usage

## Prerequisites

- **VS Code** (or VS Code Insiders) with an AI coding agent extension
- **Git** — each sub-repo is its own git repository
- **Python 3.7+** — for the `metak.py` helper script (no extra packages needed)

## Getting Started

1. Fork or clone this repository to start a new project.
2. Open `meta.code-workspace` in VS Code — never open individual folders. This gives you:
   - All repos visible in the Explorer sidebar
   - Independent git tracking per repo
   - Unified search across all codebases
   - Shared settings and launch configs
3. Add sub-repos as git submodules (see [Adding a Sub-Repo](#adding-a-sub-repo) below).
4. Edit `AGENTS.md` and `shared/` to reflect your project's architecture, standards, and glossary.

## Adding a Sub-Repo

Each sub-repo is a git submodule — a separate git repository tracked at a fixed commit inside the meta-repo.

### Add a new submodule

```bash
git submodule add <repo-url> <folder-name>
# e.g.
git submodule add https://github.com/your-org/frontend frontend
```

This creates the folder, clones the repo into it, and registers it in `.gitmodules`. Then run `metak` to finish the setup:

```bash
python metak.py frontend
```

This will:
- Add the folder to `meta.code-workspace` so it appears in the VS Code Explorer sidebar
- Create a starter `AGENTS.md` in the folder if one doesn't already exist

Then commit everything:

```bash
git add .gitmodules frontend meta.code-workspace
git commit -m "chore: add frontend submodule"
```

### Clone the meta-repo with submodules

Anyone cloning the meta-repo needs to initialise submodules too:

```bash
git clone --recurse-submodules <meta-repo-url>
# or, if already cloned:
git submodule update --init --recursive
```

### Update a submodule to its latest commit

```bash
cd <folder-name>
git pull origin main
cd ..
git add <folder-name>
git commit -m "chore: bump <folder-name> to latest"
```

### Remove a submodule

```bash
git submodule deinit -f <folder-name>
git rm <folder-name>
rm -rf .git/modules/<folder-name>
git commit -m "chore: remove <folder-name> submodule"
```

## Workflows

### Orchestrated Multi-Repo Task

Use when a feature spans multiple repositories.

1. **Brief the orchestrator.** Open an agent terminal in `orchestrator/` and describe the goal.
2. **The orchestrator plans.** It reads `shared/` for context and writes a task breakdown to `TASKS.md`.
3. **Execute with worker agents.** Open an agent terminal in each target repo and point it at its task in `TASKS.md`.
4. **The orchestrator verifies.** Return to the orchestrator terminal to review `STATUS.md` and confirm cross-repo consistency.

### Single-Repo Focused Work

For changes isolated to one repo, skip the orchestrator. Open an agent terminal directly in the target repo — it picks up the root `AGENTS.md` standards.

### Updating Shared Context

1. Make changes to `shared/` yourself or have the orchestrator propose them for your review.
2. Notify relevant agents by updating `TASKS.md` or mentioning the change in your next interaction.
3. Never let a worker agent modify `shared/` without explicit approval.
