# API Rules

The project exposes a REST-style FastAPI API.

## Endpoints

- Keep route handlers thin and predictable.
- Keep routers separated by domain.
- Use proper HTTP methods and status codes.
- Use clear response models.
- Raise `HTTPException` for API errors.
- Do not expose internal implementation errors to API clients.

## Validation

- Use Pydantic schemas for request and response validation.
- Validate query parameters with FastAPI validation tools such as `Query`.
- Validate path parameters explicitly when needed.
- Keep request and response schemas in `app/schemas`.

## API Design

- Follow existing API naming and routing patterns.
- Prefer simple REST conventions.
- Keep authentication and authorization checks at route/dependency boundaries.
- Add tests for every new endpoint.
- Update README when API behavior changes.
