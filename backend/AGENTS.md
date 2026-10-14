# Backend AGENTS.md — CSC 489 Social Media Security Lab

## Scope and authority

These instructions apply to everything under `backend/`. Read the repository's root `AGENTS.md` and `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, and `docs/VULNERABILITIES.md` before substantive work. `docs/VULNERABILITIES.md` is the **exclusive allowlist** for intentional weaknesses. Follow `docs/TESTING.md` when it exists. If instructions conflict, preserve ordinary secure behavior and ask about the specific conflict; never silently broaden an exception.

**Stack is fixed:** Python, Flask, built-in `sqlite3`, SQLite, bcrypt, signed JWT access and rotating refresh tokens. Next.js JavaScript frontend calls Flask directly. Do not switch to FastAPI, SQLAlchemy, another database, or a new auth architecture without approval.

**Environment:** local/isolated disposable security lab with synthetic users and content. Bind to loopback by default. Do not publish the vulnerable build, use real personal data, commit secrets, enable a publicly accessible interactive debugger, or introduce unapproved flaws.

## Directory responsibilities

```text
backend/
├── AGENTS.md
├── main.py                  # small startup entrypoint
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py          # create_app(), extension setup, blueprint registration
│   ├── routes/              # Flask blueprints: HTTP methods, request parsing, response status
│   ├── controllers/         # use-case orchestration and business rules
│   ├── models/              # sqlite3 SQL queries and row mapping (not ORM classes)
│   ├── schemas/             # explicit input and response validation/serialization
│   ├── config/              # environment settings, db connection, CORS origins, roles
│   ├── auth/                # JWT creation/verification, cookie/session lifecycle, decorators
│   ├── logger/              # logging configuration and safe event logging
│   └── utils/               # small shared helpers only when justified
├── migrations/              # ordered, reviewable .sql migrations
├── instance/                # disposable SQLite files, ignored by Git
└── tests/                   # pytest, Flask test client, fixture factories, lab tests
```

Prefer one blueprint per domain (`auth`, `posts`, `comments`, `likes`, `follows`, `users`, `search`, `images`, `admin`). Routes should be thin: validate inputs, resolve identity, call controllers, and return consistent JSON/status. Controllers coordinate actions and transactions. Models own SQL. Avoid redundant service/repository layers and avoid circular imports. Use an app factory and blueprint registration. Do not put business logic in `main.py`.

## API contracts

- Canonical base prefix is **`/api/v1`**, as defined by `docs/ARCHITECTURE.md`. Vulnerability spec examples omit `/v1` in some places; treat those as conceptual route suffixes and document/test the actual versioned endpoints. Do **not** silently create duplicate `/api` aliases.
- Use consistent response formats and HTTP semantics. Error shape: `{ "error": { "code": "...", "message": "..." } }`. Never leak tracebacks, SQL internals, hashes, cookies, or signing secrets.
- Validate JSON and form inputs explicitly: types, lengths, permitted fields, existence, and ownership (except for the one approved IDOR). Reject unexpected writable fields rather than mass-assigning.
- Use `401` for absent/invalid/expired authentication, `403` for authenticated users lacking permission, `404` for absent resources, `409` for conflicts, and appropriate `400`/`422` for bad input. Never return a `401` after executing a state change.
- Pagination for feed, comments, search; stable newest-first ordering with ID tie-breaker. Avoid N+1 queries and BLOB loading in feed/list queries.
- Configure exact CORS origin allowlists from environment, `supports_credentials` only for trusted origins, and required methods/headers. No wildcard origins with cookies. CORS does not substitute for CSRF controls.

## Database and persistence

- Use `sqlite3` only. Create short-lived connections via a central helper; use `sqlite3.Row`, enable `PRAGMA foreign_keys=ON` on every connection, set a bounded busy timeout, and close connections reliably.
- Parameterize SQL with `?` placeholders everywhere **except the single V-01 login query explicitly defined in `docs/VULNERABILITIES.md`**. Never generalize the unsafe query builder or make it reusable.
- Use transactions for post creation with image storage, token rotation/revocation, and other multi-step writes. Handle uniqueness/integrity errors without exposing SQL text.
- Maintain migrations for `users`, `posts`, `images`, `comments`, `likes`, `follows`, and `refresh_sessions`, plus the minimal V-04 lab session registry if required. Use indexes/constraints for relationships and pagination. Seed fixture data through a repeatable, documented script; never use real account records.
- Store uploaded image bytes as SQLite BLOBs with MIME, size, owner, and timestamps. Serve images through dedicated endpoints, not inline base64 in feed JSON. Invalid/non-image content accepted under V-07 must remain inert on retrieval (`attachment`, `application/octet-stream`, `nosniff`).
- Use bcrypt hashes for passwords, never reversible encryption or plaintext. Encryption of other sensitive data requires a documented field/key-management decision; do not invent static keys. Do not return hashes or sensitive fields in API responses.

## JWT authentication and authorization

- Use a maintained JWT library selected and documented during implementation. Access JWT: short-lived (initial default 15 min), signed, with subject, token type, expiry and appropriate unique identifier. Refresh JWT: longer-lived (initial default 7 days), signed, unique ID and rotation family metadata.
- Prefer `HttpOnly` access and refresh cookies. Configure `Secure` for HTTPS, suitable `SameSite`, narrow paths where feasible, and appropriate expiration. Frontend requests use `credentials: 'include'`. Never require frontend JavaScript to read JWT cookies.
- `register`: validate inputs, bcrypt-hash password. `login`: authenticate and set cookies. `me`: resolve identity without secrets. `refresh`: verify token and server-side session, rotate/revoke atomically, detect reuse, set replacement cookies. `logout`: revoke active refresh session and clear cookies.
- Store only hashes of refresh token identifiers/material as appropriate, not raw refresh tokens. On a successful refresh, previous refresh credentials become invalid. Keep auth failures predictable and safe; do not disclose whether a username exists unnecessarily.
- Decorators/helpers in `app/auth/` centralize current-user lookup, `login_required`, and role checks. Default privileged operations to server-side authorization; UI visibility is not access control. Define `user` and `admin` roles in configuration, not trusted client input.
- A failed access token yields `401`; frontend is responsible for one refresh attempt and one retry, and for logging out on failed refresh. Backend refresh endpoints must not depend on an unexpired access token.
- **Approved exceptions only:** V-01 is a narrowly scoped login SQL injection; V-03A/B omit admin-role checks only on their two endpoints; V-04 adds a lab-only predictable auxiliary session identifier with a demonstrable but bounded session association weakness; V-05 omits profile ownership only for whitelisted public fields; V-06 omits CSRF protection only for the follow action. Preserve JWT signing, bcrypt, and refresh rotation elsewhere.

## Explicit vulnerability boundaries

Use the exact identifiers and expected outcomes in `docs/VULNERABILITIES.md`. Annotate each deliberate exception with `LAB-VULN: V-XX` and reference its specification. Do not label vulnerabilities in the public-facing product UI.

| ID | Scoped backend behavior | Required boundary |
|---|---|---|
| V-01 | Login username query intentionally injectable | Read-only fixture lookup only; bcrypt for normal users; all other SQL parameterized |
| V-02A | Persist comment text for intentionally unsafe *frontend* comment renderer | Other surfaces escape text; no exfiltration payloads |
| V-02B | Search query can be reflected by intentionally unsafe *frontend* search heading | JSON reflection alone is not XSS; keep other renderers safe |
| V-03A | Admin user listing accessible to authenticated non-admin | Return only ID, username, display name, role; no secrets |
| V-03B | Admin post deletion accessible to authenticated non-admin | Seeded/disposable posts only; anonymous denied |
| V-04 | Predictable auxiliary lab session identifier plus narrowly scoped missing ownership check | Not a JWT secret or refresh token; do not bypass JWT validation globally; stop if design cannot be isolated |
| V-05 | Profile edit accepts another user's ID | Only `display_name` and `bio`; no role/email/password/session changes |
| V-06 | Follow endpoint susceptible to cross-site form submission | Real browser-compatible form and cookie behavior; no other CSRF exceptions |
| V-07A/B | Post upload accepts non-image bytes and exceeds normal application size limit | SQLite BLOB only; infrastructure hard ceiling, bounded fixtures, no active content or execution |

**Implementation sequence:** Build and test the intended secure feature first, then add the smallest specified lab exception with its own regression test. Never weaken shared SQL helpers, auth middleware, CORS, CSRF protection, image serving, or role checks globally. A passing vulnerability test means the **documented lab behavior** occurred, not that the behavior is safe.

## CSRF and upload integration details

- Normal cookie-authenticated state-changing routes must have appropriate CSRF protections (token and/or strict Origin verification), except V-06. The vulnerable follow route must actually accept the form encoding used in its isolated browser test; a JSON-only endpoint without a valid cross-site request is not an exploitable CSRF demonstration. Verify SameSite behavior and actual origins; don't assume CORS prevents form submission.
- Default product upload expectations: one image per post, with normal format/size validation outside V-07. For the vulnerable upload path, omit the approved application-level type/size checks but retain an independent hard request/storage ceiling to prevent denial of service. Do not accept user-provided filenames as filesystem paths. Do not render uploaded SVG/HTML or execute uploaded content.
- Do not add command injection, arbitrary file writes, exposed signing keys, plaintext password storage, unsafe debug mode, or new unapproved vulnerabilities.

## Logging, errors, and observability

- Configure structured, readable logs with timestamp, severity, route/method, request correlation ID where useful, and exception context in server logs only.
- Never log passwords, authorization headers, cookies, raw JWTs, refresh-token hashes, personal email values, or uploaded BLOBs. Use fixture-safe audit events for lab tests.
- Centralize error handlers; keep client errors actionable but not revealing. Distinguish expected auth failures, validation errors, database integrity conflicts, and unexpected server failures.

## Testing and Codex workflow

- Use `pytest` and Flask's test client. Cover registration/login, bcrypt, JWT expiry, refresh rotation/reuse rejection, logout, role checks, feed CRUD, follows, comments, likes, image BLOB retrieval, pagination, and validation.
- Create isolated tests for each approved vulnerability ID, with fixture preconditions, benign proof of effect, expected status/data change, and remediation note. For XSS and CSRF, use real-browser integration checks where needed; Flask test client alone cannot prove JavaScript execution or browser cookie behavior.
- Use bounded upload fixtures; never stress disk/memory without limits. Reset test DB state between cases. Record evidence in `docs/SECURITY_TESTS.md` when that file is created.
- Codex may autonomously implement normal backend features, tests, migrations, and small refactors. Run relevant checks and report results. Stop and ask only for unresolved security-scope contradictions, technically unworkable approved exploits, changes to auth architecture, or any deployment beyond the isolated lab.
- Do not claim a test passed unless it was actually run. Do not silently remove `LAB-VULN` exceptions during cleanup; flag proposed remediation separately.

## Definition of done for a backend feature

A feature is complete when its routes are registered, request validation and response schemas are consistent, controller/model responsibilities are separated, persistence and authorization behave as intended (including explicitly approved lab exceptions), success/error paths are tested, logs avoid secrets, and frontend integration contracts are documented. Keep the implementation as simple as the requirement allows.
