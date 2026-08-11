# MetaKitchen Agent Guide

This is a multi-repository workspace. Each sub-repo may have its own agent instruction files.

## Structure

```
meta-repo/
├── .claude/CLAUDE.md                ← root instructions (read by ALL agents)
├── AGENTS.md                        ← you are here
├── CUSTOM.md                        ← project-wide rules for all agents
├── metak-shared/                    ← shared docs: architecture, API contracts, glossary
│   ├── overview.md                  ← project goals and current state
│   ├── architecture.md              ← system boundaries and data flow
│   ├── api-contracts/               ← interface specs between components
│   ├── coding-standards.md          ← linting, commits, reviews
│   ├── glossary.md                  ← domain terms
│   └── LEARNED.md                   ← discovered methods and tricks
├── metak-orchestrator/              ← orchestrator workspace (TASKS.md, STATUS.md, EPICS.md)
├── <subfolder..>*/                  ← application sub-repos with subagent
├── <subfolder..>*/                  ← application sub-repos with subagent
├── <...>*/
└── <project>.code-workspace         ← VS Code multi-root workspace
```

## Agent Roles

### Orchestrator

The orchestrator agent coordinates cross-repo work. It:

- **Writes and maintains `metak-shared/` docs** (overview, architecture, API contracts, glossary) for user review.
- **Breaks work into tasks** in `metak-orchestrator/TASKS.md` with acceptance criteria.
- **Configures workers** by writing `CUSTOM.md` files in each target repo.
- **Spawns worker agents** scoped to individual repos and monitors progress.
- **Reviews worker completion reports** against acceptance criteria and product goals, iterating with follow-up tasks until quality is met.
- **Never writes application code** — only shared docs, tasks, and CUSTOM.md files.

See `metak-orchestrator/AGENTS.md` for full orchestrator instructions.

### Worker Agents

Worker agents operate within a single sub-repo.

Before starting, in order:
1. Read `AGENTS.md` in your target directory (repo-specific instructions).
2. Read `CUSTOM.md` in that directory (project-specific overrides from the orchestrator).
3. Read your task assignment (from the orchestrator or `metak-orchestrator/TASKS.md`).
4. Consult `metak-shared/api-contracts/` for interfaces you must conform to.
5. Consult `metak-shared/architecture.md` for system boundaries.

While working, they:

- **Write a completion report** when done. Summarize what was implemented, which tests were run and their pass counts, which paths were exercised live, any deviations from the task spec, any open concerns, and any hints for downstream tasks (gotchas found, interfaces left half-built, follow-ups worth scheduling). Update `metak-orchestrator/STATUS.md` with this report.
- **Treat `metak-shared/` as read-only.** Propose changes via the orchestrator.
- **Document learnings** in `metak-shared/LEARNED.md`.

## Agent Rules

1. **Read `.claude/CLAUDE.md` at the repo root** — it determines your role based on the task scope.
2. **One agent, one subfolder, one repo.** Workers do not work across multiple repos.
3. **API contracts live in `metak-shared/api-contracts/`.** Always reference these for cross-component interfaces.
4. **Consult `metak-shared/architecture.md`** for system boundaries and data flow.
5. **Verify integration contracts.** After modifying an interface, verify the implementation matches the contract in `metak-shared/api-contracts/` exactly.
6. **Check known deviations.** API contract files may list known bugs or deviations in an appendix — check before working against a contract.
7. **Vendored/submodule code is read-only.** Do not modify a git submodule or vendored upstream dependency unless your task explicitly targets it — it has its own change process upstream. Your project-specific code lives in this repo's own directories, not inside the vendored tree. If a change seems to require editing the submodule, flag it and stop.
   - Always run `git submodule update --init --recursive` after pulling — the first checkout does not init nested submodules.
   - Never use `--remote` unless you are deliberately bumping to upstream tip.
   - A submodule SHA bump is its own commit, separate from code changes, and is followed by a smoke test.
8. **Be economical.** Keep your output succinct — report conclusions, not narration. Read the specific region of a file you need rather than the whole file, and do not re-read what is already in your context. This is about avoiding *redundant* reads, not about guessing: never assert something about code you have not actually looked at.
9. **Confirm before production-affecting actions.** Deploys, schema pushes, and anything that changes state real users see require explicit user confirmation, even when the command is in your task spec.

## Coding Standards

Follow `metak-shared/coding-standards.md` for your repo's language.

## Validation — What "Done" Means

"It compiles", "lint is clean", or "the mocked tests pass" is **not** validation. Before reporting work done, state explicitly which paths, flows, or commands you actually exercised, and paste the output.

Every repo should define a validation checklist in its `AGENTS.md` / `CUSTOM.md`, scoped per change type (library change, service change, schema change, deploy). At minimum each checklist has: lint clean, tests clean, build clean, and **one real execution of the changed path**.

**A change that crosses a boundary is not validated by mocked tests.** If your change touches a network call, a process boundary, a runtime you do not control, generated code, or a deployed service, mocked tests only prove your mock matches your assumption — which is exactly where the bug lives. Such a change requires a live end-to-end run against the real thing before it can be called done.

If you genuinely cannot run the live check, do not claim done. Mark the work **"pending live validation"** and include the exact reproduction recipe someone else can run.

## Cost Discipline for External Calls

- Calls to paid or rate-limited services (LLM APIs, search, scraping, cloud services) cost money and cause flaky CI. Default all tests to mocks or fixture/replay.
- Gate any test that makes a real call on the relevant env var (e.g. `*_API_KEY`) and have it **skip itself** when the var is unset — never fail.
- Where a provider offers a dry-run/no-op mode, use it in tests that only assert on request shape.
- **Throttle fan-out.** When fanning out calls to a paid or rate-limited service, use the cheapest model/endpoint that does the job, cap concurrency (4 is a sane default for a burst of 8), and give every call a timeout via an abort signal. An unthrottled `Promise.all` / `gather` burst saturates per-minute and per-concurrency limits and cascades into rate-limit errors.
- **One wrapper per third-party service.** Route all outbound calls through a single wrapper that owns retry, error classification, and alerting. Ad-hoc per-call-site handling means there is no one place to answer "is this a config error or a transient brownout".

## Project Structure

- Maintain a description of the current project structure in `STRUCT.md` within each sub-repo
- The structure should be a tree view with brief descriptions of each file and folder
- If at any point `STRUCT.md` does not exist, pause your current task and create it by analyzing the project
- Update `STRUCT.md` with every change to the project structure

## When Stuck

- Re-read the relevant `CUSTOM.md`, and `STRUCT.md` for context you may have missed
- Check `metak-shared/LEARNED.md` for known pitfalls and solutions
- Verify your assumptions against the running system, not documentation
- If still blocked, update `metak-orchestrator/STATUS.md` with what you tried and what failed
- If the task requires a pattern **not covered** by the shared docs / architecture / contracts, do not invent an ad-hoc approach. Record the gap in `metak-orchestrator/STATUS.md` and let the orchestrator extend the design first.
- If a task appears to require editing another repo, a shared contract, or `metak-shared/`, flag it for the orchestrator rather than reaching across the boundary yourself.

## Custom Instructions

Read and follow `CUSTOM.md` at the project root for project-wide rules that apply to all agents.
