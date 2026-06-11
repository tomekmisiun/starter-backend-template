# Git Rules

Use a feature branch workflow.

## Branching

- Do not do feature work directly on `main` unless explicitly requested.
- Create or use a dedicated branch before meaningful changes.
- Use branch names such as:
  - `feature/<short-description>`
  - `fix/<short-description>`
  - `refactor/<short-description>`
  - `docs/<short-description>`
  - `chore/<short-description>`
  - `test/<short-description>`

## Planning

- Show a brief plan before coding substantial changes.
- Keep changes scoped to the requested task.
- Do not make unrelated changes.

## Commit Messages

Prefer Conventional Commits.

Examples:

- feat: add user search
- fix: correct refresh token validation
- refactor: move business logic to service layer
- test: add pagination tests
- docs: update README for Redis setup
- chore: update development dependencies

Keep commit messages short and focused.
One commit should represent one logical change.

Do not add commit trailers or footers that attribute authorship to AI tools.
Forbidden examples:

- `Co-authored-by: Cursor <...>`
- `Co-authored-by: Codex <...>`
- `Co-authored-by: Claude <...>`
- `Authored-by: Cursor`, `Authored-by: Codex`, or `Authored-by: Claude`

Commit messages must contain only the Conventional Commit subject and optional
body written for humans reviewing the repository history.

## Commits

- Run relevant tests before commit.
- Do not commit failing tests.
- Commit only related files.
- Do not commit secrets, `.env`, caches, virtual environments, local database
  files, or generated junk.
- Do not commit automatically unless explicitly requested.
- Use clear commit messages in Conventional Commit format.
- Never append AI authorship trailers (`Co-authored-by`, `Authored-by`, or
  similar) for Cursor, Codex, Claude, or other agents.

## Push And Merge

- Do not push without explicit approval.
- Do not merge without explicit approval.
- Never force push unless explicitly requested and the risk is explained.
- Never delete branches without explicit approval.
- Before merge, show changed files, test results, and a short summary.
