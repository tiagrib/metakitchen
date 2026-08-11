# Coding Standards

- All code must pass linting and tests before committing.
- Never import directly from another repo's source code. Use shared contracts in `metak-shared/api-contracts/`.
- When in doubt about system boundaries, consult `metak-shared/architecture.md`.
- **No emojis in code, commits, docs, or user-facing strings.** Use text alternatives like `[OK]`, `[FAIL]`, `[WARN]` when status indicators are needed — they stay greppable, terminal-safe, and CI-safe.
- **Rule of three before genericizing.** Do not refactor N implementations into a generic abstraction until N >= 3. Two instances is not a pattern; the third tells you which axis actually varies.
- **Safety rails run before the remote call.** Any command that mutates a remote or shared system validates its inputs against the hard rules **locally, before opening the connection**. Encode the rails in code, not just in docs — a rule that only exists in a markdown file will be violated.
- **Document deviations.** If a module must break a stated convention, document the exception inline at the site *and* in the repo's `CUSTOM.md`, with the reason. An undocumented deviation reads as a bug to the next worker.

## CLI and Tooling Output

- CLI output is designed to be grepped and pasted into tickets. Success prints one `[OK] ...` line to stdout; failure prints `[FAIL] ...` to stderr and exits non-zero.
- Multi-line status uses aligned columns — no box drawing, no ANSI colour by default.
- **`status` vs `health` are different commands.** `status` reports the supervisor's view (is the unit running). `health` performs a real round-trip against the service and exits 0 = healthy / non-zero = unhealthy, so it is scriptable. A process can be "active" and still wedged — never report health from status.
- Release and deploy commands refuse a dirty working tree by default so the artifact is reproducible from a committed SHA. Require an explicit `--allow-dirty` to override, and note it in the report.

## Deliverables

- A single-file deliverable meant to be opened from disk must inline its data (e.g. a
  `window.DATA` global). `fetch()` and module imports are blocked on `file://`, so a
  file that loads its data at runtime works on your dev server and is blank for the
  person who opens it.

## Cross-Platform Text Output

- Never regenerate a text file with PowerShell's `>` or `Out-File` / `Set-Content` without `-Encoding utf8`. Windows PowerShell 5.1 writes UTF-16 LE with BOM, which many linters and parsers reject while bundlers silently accept. Use a bash redirect, or `Out-File -Encoding utf8`.
- Symptom to recognize: `Parsing error: File appears to be binary` on a file you know is text.

## Commit Messages

Follow Conventional Commits: `type(scope): description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

- One commit per logical unit — per file or per coherent change. No monolithic landings at the end of a task.

## Code Review

- All changes go through PRs.
- At least one human approval required before merge.
- CI must pass.

## Testing

- All code must have tests that pass before committing.
- Integration test conventions are project-specific — define them in the `tests/CUSTOM.md` file.

## Documentation

- Do not document every change you made — docs should reflect the current state of the project, not its history
- Before writing documentation, check if the information already exists elsewhere
- Check STRUCT.md to understand where documentation files are located
