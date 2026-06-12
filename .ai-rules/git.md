# Git Rules

Feature branch workflow with explicit user approval for remote changes.

## Branching

- MUST NOT do feature work directly on `main` unless the user explicitly
  requested it.
- Create or use a dedicated branch before meaningful changes.

## Commits

- MUST NOT commit failing tests, secrets, `.env`, caches, virtual environments,
  local database files, or generated junk.
- MUST NOT commit automatically unless the user explicitly requested it.
- Use Conventional Commits with a short, focused subject.
- MUST NOT add AI authorship trailers (`Co-authored-by`, `Authored-by`, or
  similar) for Cursor, Codex, Claude, or other agents. Pre-commit blocks these
  when the commit-msg hook is installed.

## Push And Merge

- MUST NOT push, merge, or force-push without explicit user approval.
- MUST NOT delete branches without explicit user approval.
- Before merge, show changed files, validation results, and a short summary.
