# Configuration

## `AGENTS.md` — the canonical source

All agent instructions live in `AGENTS.md` files (root level for shared rules, per-repo for repo-specific rules). Any AI agent should read these.

Customize the root `AGENTS.md` to reflect your project's structure, coding standards, and agent rules. Sub-repos should have their own `AGENTS.md` for anything specific to that repo.

## `CUSTOM.md` — user instructions for the orchestrator and sub-agents

The `CUSTOM.md` files are for user instructions that the orchestrator and sub-agents read. The orchestrator reads the root `CUSTOM.md` to understand user goals and constraints, and writes `CUSTOM.md` files in each sub-repo to direct the worker agents.

The orchestrator is the only agent that writes `CUSTOM.md` files. Users/Developers may also edit them for additional instructions. Worker agents treat them as read-only instructions. This separation allows the orchestrator to dynamically configure worker behavior based on the current goals and tasks.

The reason to separate `AGENTS.md` and `CUSTOM.md` is to distinguish between:
- **Agent rules and shared knowledge** (in `AGENTS.md`) that all agents should follow and reference, such as coding standards, architecture docs, API contracts, and the agent role definitions.
- **User instructions and task-specific directives** (in `CUSTOM.md`) that the orchestrator writes to guide the worker agents on what to do for the current tasks. This allows the orchestrator to adapt worker behavior on the fly without changing the underlying agent rules and shared knowledge.
- **Community-driven improvements** to the scaffold code and agent rules can be made in `AGENTS.md` and pulled into existing projects without overwriting any project-specific instructions in `CUSTOM.md`.


## Agent pointer files

Each AI agent has its own config file convention. MetaKitchen includes a minimal pointer in each so the agent discovers it natively and gets directed to `AGENTS.md`:

| Agent | Pointer file | Sub-agent orchestration |
|---|---|---|
| Claude Code | `.claude/CLAUDE.md` | Yes |
| Cursor | `.cursor/rules/README.mdc` | Yes |
| GitHub Copilot | `.github/copilot-instructions.md` | Yes (CLI `/fleet`) |
| OpenAI Codex CLI | `AGENTS.md` (native) | Yes |
| Cline | `.clinerules` | Yes |
| Roo Code | `.roo/rules/README.md` | Yes (Boomerang Tasks) |
| JetBrains Junie | `.junie/guidelines.md` | Yes (via Air) |
| Windsurf | `.windsurfrules` | Partial (user-initiated only) |
| Gemini CLI | `GEMINI.md` | Experimental |

Every pointer file contains **role-routing logic** — it directs the agent to `AGENTS.md`, determines whether the agent acts as orchestrator or worker based on the scope of the request, and lists the shared knowledge files. Per-repo `.claude/CLAUDE.md` files (created by `metak add`) declare the worker identity for that sub-repo.

You don't need to touch the pointer files — just keep `AGENTS.md` up to date. The role selection logic is pre-configured in all of them.

## `<project>.code-workspace`

Add sub-repos to the `folders` array so VS Code includes them in the multi-root workspace. Each entry is a relative path matching the submodule folder name:

```json
{
  "folders": [
    { "path": "." },
    { "path": "repo-a" },
    { "path": "repo-b" }
  ]
}
```

Sub-repos can be added as git submodules or plain folders (monorepo) — see [Adding a Sub-Repo](usage.md#adding-a-sub-repo) in the usage guide. The `metak add` command handles this for you.

Workspace-level settings, extension recommendations, and launch configs live here too.
