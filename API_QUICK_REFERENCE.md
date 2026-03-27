# Notes API Quick Reference

Quick operational reference generated from current router/service behavior.

## Base
- Host: `http://127.0.0.1:8000`
- Versioned prefix: `/api/v1`
- Main route groups:
  - `/api/v1/users`
  - `/api/v1/notes`

## Response Format
If a request reaches service logic, responses use a common shape:

```json
{
  "code": "SUCCESS|ERROR_CODE",
  "message": "Human-readable message",
  "pagination": null,
  "user|note|user_query|note_query": {}
}
```

For query responses, `pagination` is lifted from the first query payload item and contains metadata such as:
- `count`
- `offset`
- `limit`
- `view_type`
- `query`

Error payload shape from service pipeline:

```json
{
  "code": "ERROR_CODE",
  "info": "Error details"
}
```

FastAPI-level errors (before service pipeline) still use default FastAPI `detail` payloads.

## Authentication
- Auth uses Bearer JWT.
- Most non-login mutating/read routes require `Authorization: Bearer <token>`.
- Token subject (`sub`) is used to resolve current user.

## Users Routes
Prefix: `/api/v1/users`

### `GET /`
- Returns plain text root message.

### `POST /login`
- Auth not required.
- Body: login schema (`username` or `email`, and `password`).
- Success: returns token.
- Common errors:
  - `BAD_REQUEST` (400): username/email missing
  - `NOT_FOUND` (404): user not found
  - `UNAUTHORIZED` (401): invalid credentials

### `POST /`
- Auth not required.
- Creates user and returns user payload + token.
- Common errors:
  - `USER_EXISTS` (409)
  - `INTERNAL_ERROR` (500)

### `GET /search`
- Auth required.
- Query params: search schema + `offset`, `limit`.
- Non-admin behavior:
  - email filter is ignored
  - returned user `email` is set to `null`
- Common errors:
  - `UNAUTHORIZED` (401)

### `GET /{user_id}`
- Auth required.
- Supports `me` alias for current user.
- Common errors:
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403) for disallowed view
  - plain text 400 if path segment is neither integer nor `me`

### `DELETE /{user_id}`
- Auth required.
- Permission uses manage-user policy checks.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403)
  - `INTERNAL_ERROR` (500) if delete operation fails unexpectedly

### `PATCH /`
- Auth required.
- Body: modify user schema.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403)
  - `BAD_MODIFY` (422)

### Role Management
- `PUT /roles` (replace roles)
- `POST /roles` (add roles)
- `DELETE /roles` (remove roles)
- Auth required.
- Body uses role list operations.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `FORBIDDEN` (403)
  - `NOT_FOUND` (404)
  - `INVALID_ROLE` / `INVALID_ROLES` (422)

## Notes Routes
Prefix: `/api/v1/notes`

### `GET /`
- Returns plain text root message.

### `GET /search`
- Auth required.
- Query params: search schema + `offset`, `limit`.
- Results are filtered by note read policy.
- Common errors:
  - `UNAUTHORIZED` (401)

### `GET /{note_id}`
- Auth required.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403)

### `POST /`
- Auth required.
- Body: create note schema.
- Current user must match `author_id` in request.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `FORBIDDEN` (403): cannot create notes or author mismatch
  - `BAD_REQUEST` (422): invalid flags

### `PATCH /`
- Auth required.
- Body: modify note schema.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403)
  - `BAD_MODIFY` (422)

### `DELETE /{note_id}`
- Auth required.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403)
  - `INTERNAL_ERROR` (500)

### Flag Management
- `POST /flags` (add)
- `DELETE /flags` (remove)
- `PATCH /flags` (replace)
- Auth required.
- Common errors:
  - `UNAUTHORIZED` (401)
  - `NOT_FOUND` (404)
  - `FORBIDDEN` (403)
  - `BAD_MODIFY` (422)

Special flag rule:
- On own note, authors may only add/remove/update the `private` flag.

## Notes on Security Behavior
- `query_users` intentionally redacts sensitive fields for non-admin users.
- Some permission checks are policy-driven (`can_view_user`, `can_manage_user`, `can_read_note`, `can_edit_note`).
- JWT tokens are returned on both user creation and login.
