# Notes Backend API (Basic)

Base URL prefix: `/api/v1`

This API is built with FastAPI and uses JWT Bearer auth for protected routes.

## Authentication

- Public endpoints:
	- `POST /api/v1/users/` (register)
	- `POST /api/v1/users/login` (login)
	- Secret endpoints under `/api/v1/secrets/*` currently do not require Bearer auth.
- Protected endpoints:
	- Most `/users` and all `/notes` operations except route roots.
- Auth header format:

```http
Authorization: Bearer <token>
```

JWT details:
- `sub` claim holds user ID.
- Token expiry is set to about 1 hour.

## Response Shape

Successful responses are wrapped like:

```json
{
	"code": "SUCCESS",
	"message": "Human-readable message",
	"pagination": null,
	"<result_key>": {}
}
```

Error responses are usually:

```json
{
	"code": "ERROR_CODE",
	"info": "Error details"
}
```

For query endpoints (`/search`), `pagination` is filled and the result list is returned under `note_query` or `user_query`.

## Main Endpoints

## Users API

Route root: `GET /api/v1/users/`

### Public

1. `POST /api/v1/users/`
	 - Creates a new user.
	 - Body:
	 ```json
	 {
		 "username": "john_doe",
		 "password": "StrongPass1!",
		 "email": "john@example.com"
	 }
	 ```
	 - Username rules: 3-20 chars, alnum + underscore.
	 - Password rules: min 8, upper, lower, digit, special char required.
	 - Returns created user data plus JWT token.

2. `POST /api/v1/users/login`
	 - Authenticates by `username` or `email` with `password`.
	 - Body:
	 ```json
	 {
		 "username": "john_doe",
		 "password": "StrongPass1!"
	 }
	 ```
	 - Returns token on success.

### Protected

1. `POST /api/v1/users/search?offset=0&limit=100`
	 - Search/filter users.
	 - Body fields: `username`, `email`, `username_contains`.
	 - Non-admin views mask email.

2. `GET /api/v1/users/{user_id}`
	 - Gets a user by ID.
	 - Special value: `me` resolves to authenticated user ID.

3. `GET /api/v1/users/{user_id}/username`
	 - Gets only username for the target user.
	 - Supports `me`.

4. `PATCH /api/v1/users/`
	 - Modifies user fields.
	 - Body:
	 ```json
	 {
		 "user_id": 1,
		 "modifications": {
			 "username": "new_name"
		 }
	 }
	 ```
	 - Allowed keys are controlled by core schema mutable set.

5. `DELETE /api/v1/users/{user_id}`
	 - Deletes a user if policy allows.

6. Role management
	 - `POST /api/v1/users/roles` add roles
	 - `DELETE /api/v1/users/roles` remove roles
	 - `PUT /api/v1/users/roles` replace all roles
	 - Example body:
	 ```json
	 {
		 "user_id": 1,
		 "roles": ["moderator"]
	 }
	 ```
	 or
	 ```json
	 {
		 "user_id": 1,
		 "new_roles": ["user", "moderator"]
	 }
	 ```

## Notes API

Route root: `GET /api/v1/notes/`

All note operations below require Bearer token.

1. `POST /api/v1/notes/`
	 - Creates a note.
	 - Body:
	 ```json
	 {
		 "author_id": 1,
		 "title": "My first note",
		 "content": "Hello world",
		 "flags": ["private"]
	 }
	 ```
	 - `author_id` must match authenticated user ID.
	 - Valid flags: `private`, `admin_only`, `archived`.

2. `GET /api/v1/notes/{note_id}`
	 - Gets one note if readable by policy.

3. `PATCH /api/v1/notes/`
	 - Modifies note fields.
	 - Body:
	 ```json
	 {
		 "note_id": 10,
		 "modifications": {
			 "title": "Updated title",
			 "content": "Updated content"
		 }
	 }
	 ```
	 - Mutable keys: title and content.

4. `DELETE /api/v1/notes/{note_id}`
	 - Deletes note if editable by policy.

5. `POST /api/v1/notes/search?offset=0&limit=100`
	 - Query notes with fields:
		 - `note_id`, `author_id`, `title`, `title_contains`, `content_contains`, `flags`

6. Flag management
	 - `POST /api/v1/notes/flags` add flags
	 - `DELETE /api/v1/notes/flags` remove flags
	 - `PATCH /api/v1/notes/flags` replace flags (`new_flags`)
	 - Add/remove body:
	 ```json
	 {
		 "note_id": 10,
		 "flags": ["private"]
	 }
	 ```
	 - Replace body:
	 ```json
	 {
		 "note_id": 10,
		 "new_flags": ["private", "archived"]
	 }
	 ```

## Secret Endpoints

Route group: `/api/v1/secrets`

1. `GET /api/v1/secrets/homer?secret_key=beer`
	 - Returns an MP3 file response.

2. `GET /api/v1/secrets/homer?secret_key=donut`
	 - Returns plain text: `Mmm... Donuts!`

3. `GET /api/v1/secrets/homer?secret_key=quotes`
	 - Returns one random quote from Homer quotes JSON.

4. `GET /api/v1/secrets/homer?secret_key=<anything_else>`
	 - Returns 403 with `INVALID_KEY` JSON.

5. `GET /api/v1/secrets/coffee`
	 - Returns 418 teapot JSON:
	 ```json
	 {
		 "code": "I_AM_A_TEAPOT",
		 "info": "I'm a teapot, I cannot brew coffee."
	 }
	 ```

## Important Objects

## User

What a user represents:
- An authenticated account that owns notes and has role-based permissions.

What a user holds:
- Database fields:
	- `id` (int)
	- `email` (unique string)
	- `username` (unique string)
	- `created_at` (datetime)
	- `password_hash` (stored hash, never exposed by API serializer)
	- `roles` (comma-separated string in DB; returned as list in API responses)

How a user behaves:
- Auth:
	- Can register and login to receive JWT.
- Visibility:
	- Can fetch own data.
	- Search results may hide email for non-admin views.
- Role effects:
	- Roles map to permissions (examples: create notes, edit any note, manage users).
	- Valid roles: `user`, `moderator`, `admin`, `owner`, `banned`.
- Management rules:
	- Owners can manage everyone.
	- Non-owner admins/moderators cannot manage owner/admin targets.

## Note

What a note represents:
- A user-authored text record with optional visibility/processing flags.

What a note holds:
- Database fields:
	- `id` (int)
	- `author_id` (user foreign key)
	- `title` (string)
	- `content` (string)
	- `posted_at` (datetime)
	- `flags` (comma-separated string in DB; serialized as list in API responses)

How a note behaves:
- Ownership:
	- Author can always edit own note.
- Read policy:
	- `private` notes need owner or private-read permission.
	- `admin_only` notes need manage-user-level permission.
- Write policy:
	- Create requires create-note permission.
	- `author_id` in create request must equal token user ID.
	- Non-owner edits require elevated permission.
- Flag rules:
	- Valid flags: `private`, `admin_only`, `archived`.
	- Owners can only add/remove/set `private` on their own notes.

## Useful Quick Start

1. Register user: `POST /api/v1/users/`
2. Login: `POST /api/v1/users/login`
3. Use returned token as Bearer token.
4. Create note: `POST /api/v1/notes/`
5. Query notes: `POST /api/v1/notes/search`
