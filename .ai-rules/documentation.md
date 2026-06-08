# Documentation Rules

`.ai-rules` is the source of truth for AI agent behavior. Project-facing
documentation lives in `README.md`.

## README Requirements

`README.md` must be updated for every larger feature.

`README.md` must describe:

- project purpose
- technology stack
- requirements
- local setup
- Docker setup
- environment variables
- migrations
- tests
- API overview
- auth flow
- roles and permissions
- rate limiting
- known production gaps

## When To Update README

Update `README.md` when a change:

- adds a new endpoint
- changes authentication
- changes Docker or configuration
- adds a migration
- adds Redis, rate limiting, or session logic
- changes the test workflow

Do not update `README.md` for small refactors that do not change behavior,
setup, API, configuration, migrations, or workflows.

## Writing Rules

- Do not invent features.
- Keep wording clear, technical, and concise.
- Avoid hype, marketing language, excessive badges, and emojis.
- Prefer commands and examples that match the repository.
- Keep known production gaps honest and current.
