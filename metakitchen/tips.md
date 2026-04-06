# Tips

- **Always open the `.code-workspace` file**, not individual folders.
- **One agent per terminal, one repo per agent.** Use the orchestrator for cross-repo coordination.
- **Treat `metak-shared/` as a contract boundary.** Changes there are deliberate decisions, not side effects.
- **Use `CUSTOM.md` for project-specific and worker configuration.** The user and orchestrator write these to configure workers for each task. They persist across sessions.
- **`TASKS.md`, `STATUS.md`, `EPICS.md`, and `DECISIONS.md` are plain markdown.** Keep them simple.
- **Git remains per-repo.** The project structure is a local dev convenience — it doesn't affect CI/CD.
- **Delete what you don't need.** If you're only using one AI agent, remove the other pointer files. If you don't need the orchestrator pattern, remove that folder.
- **Re-run `metak install --force` to update templates** after pulling new changes to the MetaKitchen repo. Your `CUSTOM.md` files are always preserved.
- **`metakitchen/` is documentation only** and lives in the MetaKitchen repo, not in your project. Agents don't need to read it — point them at `AGENTS.md`.
