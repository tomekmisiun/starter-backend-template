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

## Commits

- Run relevant tests before commit.
- Do not commit failing tests.
- Commit only related files.
- Do not commit secrets, `.env`, caches, virtual environments, local database
  files, or generated junk.
- Do not commit automatically unless explicitly requested.
- Use clear commit messages. Conventional Commit style is preferred when the
  user has not specified another format.

## Push And Merge

- Do not push without explicit approval.
- Do not merge without explicit approval.
- Never force push unless explicitly requested and the risk is explained.
- Never delete branches without explicit approval.
- Before merge, show changed files, test results, and a short summary.
