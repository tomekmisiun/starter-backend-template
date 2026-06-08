# Docker Rules

Docker is part of the supported development workflow for this project.

## Stack

- API container runs the FastAPI app.
- PostgreSQL is the primary application database.
- A separate PostgreSQL test database is used for pytest.
- Redis is used for rate limiting and future session-related infrastructure.

## Rules

- Keep Docker and Compose configuration aligned with application config.
- Do not hardcode production secrets in Docker files or Compose files.
- Use safe placeholder values only in examples.
- If Docker, Compose, ports, service names, or env variables change, update
  README documentation.
- If test workflow changes, update README documentation.
- Do not introduce new services without explaining why and getting approval.
- Prefer reproducible commands that match CI and Makefile usage.
