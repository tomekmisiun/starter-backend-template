# Security Rules

Use a production-ready mindset for backend changes.

## Secrets

- Never hardcode secrets.
- Never commit real credentials, API keys, private certificates, SSH keys,
  database dumps, `.env` files, or local database files.
- Use environment variables for secrets and deployment-specific config.
- Keep `.env.example` limited to safe placeholders.
- If secrets are detected, stop and warn immediately.

## Auth And Sessions

- Keep authentication logic explicit and reviewable.
- Do not mix auth/session logic with unrelated business logic.
- Check authorization at route/dependency boundaries.
- Add regression tests for auth, session, role, and permission changes.
- Deny unsafe behavior by default.

## API Safety

- Validate input through schemas and FastAPI validation.
- Avoid leaking internal stack traces or implementation details in responses.
- Use proper HTTP status codes.
- Keep rate limiting and Redis-backed protections testable.

## Dependencies

- Do not add security-sensitive libraries without approval.
- Prefer maintained, well-known libraries already present in the project.
