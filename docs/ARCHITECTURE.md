# ARCHITECTURE.md — CSC 489 Social Media Security Lab

## 1. Purpose and authority

This document defines the architecture for an Instagram-inspired educational social-media MVP. It is implementation guidance for Codex, not a request to add vulnerabilities. Read `/AGENTS.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, and this document before substantial implementation. Consult `docs/VULNERABILITIES.md` before implementing, modifying, or fixing an intentional security flaw.

**Chosen stack:** Next.js App Router with **JavaScript/JSX** (no TypeScript), Tailwind CSS; **Flask** REST API in Python; **SQLite** via Python's built-in `sqlite3`; React Context and local component state; direct browser-to-Flask requests; image BLOBs stored in SQLite; JWT access and rotating refresh tokens; bcrypt password hashes.

The instructor's vulnerability guide uses Flask examples and identifies SQL injection, XSS, CSRF, IDOR, broken access control, authentication/session flaws, and file-upload flaws. These are conceptual references, not code to copy blindly. Specific vulnerable routes, exploit behavior, and exceptions belong exclusively in `docs/VULNERABILITIES.md`.

## 2. Repository structure

```text
social-security-lab/
├── AGENTS.md
├── docs/
│   ├── PRODUCT.md
│   ├── DESIGN.md
│   ├── ARCHITECTURE.md
│   ├── VULNERABILITIES.md         # to be authored separately
│   └── TESTING.md                 # to be authored separately
├── frontend/
│   ├── AGENTS.md                  # frontend-specific instructions, later
│   ├── package.json
│   ├── next.config.mjs
│   ├── .env.local.example
│   ├── public/
│   └── src/
│       ├── app/                   # Next.js App Router ONLY
│       │   ├── layout.jsx
│       │   ├── globals.css        # centralized CSS tokens + Tailwind
│       │   ├── page.jsx           # global feed
│       │   ├── login/page.jsx
│       │   ├── register/page.jsx
│       │   ├── upload/page.jsx
│       │   ├── search/page.jsx
│       │   ├── profile/[username]/page.jsx
│       │   ├── settings/page.jsx
│       │   └── admin/page.jsx
│       ├── api/                   # HTTP client, endpoint functions, auth retry
│       ├── context/               # AuthContext, only truly shared state
│       ├── layouts/               # App shell, navigation, feed layout
│       ├── features/              # auth/, posts/, comments/, likes/, follows/,
│       │                          # profiles/, search/, admin/
│       ├── components/            # shared UI: Button, Modal, Avatar, etc.
│       └── lib/                   # pure utilities, constants
└── backend/
    ├── AGENTS.md                  # backend-specific instructions, later
    ├── main.py                    # Flask app entry point / app factory invocation
    ├── requirements.txt
    ├── .env.example
    ├── app/
    │   ├── __init__.py            # create_app(), blueprint registration
    │   ├── routes/                # HTTP endpoints, blueprints
    │   ├── controllers/           # request orchestration / business logic
    │   ├── models/                # SQL statements and row-to-domain mapping
    │   ├── config/                # database, settings, CORS allowlist, roles
    │   ├── auth/                  # JWT issuance/verification, refresh, roles
    │   ├── schemas/               # lightweight input/output validation helpers
    │   ├── logger/                # structured app logging setup
    │   └── utils/                 # narrowly shared helpers
    ├── migrations/                # versioned SQL migrations (as needed)
    ├── instance/                  # local SQLite DB, gitignored
    └── tests/                     # API, auth, database, vulnerability tests
```

`src/app/` is the route hierarchy; do not create a parallel Next.js `pages/` router. `src/layouts/` contains reusable layout *components*, not a second routing system. Keep a feature's specialized UI/hooks within `features/<feature>/`; move a component to `components/` only when it is genuinely reusable. Avoid new service/repository layers unless repeated complexity justifies them.

## 3. Responsibility boundaries

- **Next.js pages/layouts:** routing and composition; use client components only for browser interaction or state. Do not place secret keys or privileged data access in browser code.
- **Frontend `api/`:** one configured fetch wrapper; feature-specific API functions; consistent response parsing and error objects. Components do not hardcode backend URLs or implement refresh flows independently.
- **Frontend Context:** authenticated user and auth lifecycle (`checking`, `authenticated`, `unauthenticated`); expose `login`, `logout`, and `refreshCurrentUser`. Keep post lists, forms, and modal state local to features unless genuinely shared. Derive values rather than duplicating state.
- **Shared UI:** accessible, responsive, token-based; meaningful idle/loading/error/success states where applicable. Follow `docs/DESIGN.md` and the installed Impeccable skill's actual instructions.
- **Flask routes:** URL/method registration, parse/validate input, call controller, serialize response and HTTP status. Register blueprints under `/api/v1`.
- **Controllers:** feature behavior and orchestration; no Flask app setup or duplicated SQL scattered through routes.
- **Models:** `sqlite3` queries and data mapping; use parameter binding by default. The SQL injection exception must be scoped and named in `docs/VULNERABILITIES.md`.
- **Config:** environment-driven settings, connection helper, exact allowed origins, allowed roles, token settings. Never commit real secrets.
- **Auth:** decorators/helpers for identity and role checks; centralize JWT issuance, validation, token rotation, and logout invalidation.
- **Logger:** log operational errors and security-relevant events without access tokens, passwords, refresh tokens, raw cookies, or sensitive personal data.

## 4. Data model and persistence

Start with these conceptual tables; adjust columns through reviewed SQL migrations rather than silently changing live schema:

- `users`: id, unique username, display_name, email (unique if used), password_hash, bio, avatar_image_id, role, created_at, updated_at.
- `posts`: id, author_id, image_id, caption (nullable), created_at, updated_at.
- `images`: id, owner_id, binary_data (BLOB), mime_type, byte_size, created_at. Use this for post images and avatars. Store only metadata in post/user rows; serve image bytes through a dedicated image endpoint.
- `comments`: id, post_id, author_id, body, created_at.
- `likes`: user_id, post_id, created_at; unique `(user_id, post_id)`.
- `follows`: follower_id, following_id, created_at; unique pair, no self-follow.
- `refresh_sessions`: id/jti, user_id, token_hash, expires_at, revoked_at, replaced_by_jti, created_at; support refresh rotation, reuse detection, and logout.

Use SQLite foreign keys (`PRAGMA foreign_keys=ON` per connection), explicit transactions for multi-step mutations, unique constraints, indexes on feed and relationship lookups, and a short connection lifetime per request. Use `sqlite3.Row` for named columns. Set sensible busy timeouts; SQLite is suitable for a modest local classroom MVP, not a high-traffic production service.

**BLOB tradeoff:** image bytes in SQLite simplify the lab's persistence and backup, but increase DB size. Enforce a default upload limit and image MIME/format validation *except* where the approved upload-vulnerability spec deliberately overrides a particular check. Avoid loading full image BLOBs in feed-list queries. Return image URLs/IDs, not base64 data in feed JSON. Serve correct content types, and avoid interpreting uploaded content as executable code.

**Sensitive data:** hash passwords with bcrypt; never encrypt passwords reversibly. Use TLS for any non-local deployment and encrypt backups/storage containing sensitive information where feasible. For application-level encryption, specify the exact data fields and key-management strategy before implementation; do not invent a hardcoded encryption key. A documented security-lab exception can override only the named protection in its named scope.

## 5. Authentication: access JWT + rotating refresh JWT

Default: **HttpOnly cookies** for access and refresh JWTs. Cookies are automatically sent by the browser on requests made with `credentials: 'include'`; frontend JavaScript must not read JWT values or persist them in `localStorage`/`sessionStorage`.

- Access token: short-lived (initial default 15 minutes), signed, includes subject/user ID, token type `access`, expiration, issued-at, and jti as needed.
- Refresh token: longer-lived (initial default 7 days), signed, type `refresh`, unique jti; persist a **hash** of the active token/jti in `refresh_sessions`, never the raw refresh token. Rotate on each successful refresh and revoke the previous one atomically. Detect attempted reuse of revoked refresh tokens and invalidate the affected token family/session according to the chosen policy.
- `POST /api/v1/auth/register`: validate, bcrypt-hash password, create account.
- `POST /api/v1/auth/login`: validate credentials; issue access and refresh cookies.
- `POST /api/v1/auth/refresh`: verify refresh token and stored session; rotate; set new cookies. Never attempt refresh recursively on this endpoint.
- `POST /api/v1/auth/logout`: revoke current refresh session and clear cookies.
- `GET /api/v1/auth/me`: resolve current authenticated user; no secret fields in response.

**Frontend automatic retry contract:**

1. Send API request with `credentials: 'include'` (and any required CSRF mechanism, unless the approved CSRF lab specifically excludes it).
2. If successful, return data. If `401` indicates expired/missing access authentication, call refresh once. Do **not** refresh for `403` authorization denial or ordinary `400`/`404` errors.
3. If refresh succeeds, retry the original request **once**. For concurrent 401 responses, share one in-flight refresh promise so requests do not race token rotation.
4. If refresh fails, or the retried request remains `401`, clear user state, mark unauthenticated, and reject with a typed `AuthenticationError`. UI may redirect to login while preserving intended destination. Do not silently swallow the error or loop.
5. Exclude login, register, refresh, and logout from automatic recursive refresh. Avoid automatically replaying non-idempotent requests unless the original request was definitely rejected before execution; use the API's defined 401 semantics.

Cookie attributes: `HttpOnly`, `Secure` on HTTPS, explicit `SameSite` according to actual origins and CSRF design, narrow `Path` where practical, and expiration/max-age. Local development on separate localhost ports is **cross-origin** but generally same-site; cookie and CORS behavior must be tested in the browser. Cookie authentication does **not** itself prevent CSRF. Keep CSRF protections enabled by default unless a specific endpoint is intentionally exempted in `docs/VULNERABILITIES.md`.

**Role authorization:** define `user` and `admin`; perform checks in Flask on every privileged request. UI hiding is not authorization. Avoid trusting role values supplied by clients; use validated token claims and/or database role lookups according to the final auth implementation. An intentional broken-access-control endpoint must be explicitly documented as an exception.

## 6. API conventions and communication

- Flask is the sole application-data API and database owner. Next.js must not open SQLite directly.
- Frontend calls a configured base URL such as `NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api/v1` directly from the browser.
- Backend default origin allowlist includes only the exact local frontend origin (e.g. `http://localhost:3000`); do not use `*` with credentialed requests. Configure Flask CORS to return the requesting allowed origin, allow credentials, and support required methods/headers.
- Use predictable JSON responses and status codes: `200/201` success, `204` deletion, `400` malformed input, `401` unauthenticated, `403` forbidden, `404` missing, `409` conflict, `422` validation failure as appropriate, `500` unexpected server errors.
- Standard error envelope: `{ "error": { "code": "...", "message": "..." } }`; keep detailed stack traces in server logs, not API responses, unless explicitly approved as a lab exception.
- Paginate feed, search, and comments using a stable ordering (newest first, deterministic ID tie-breaker). Avoid fetching all rows.
- Prefer clear REST resources: `/posts`, `/posts/{id}`, `/posts/{id}/comments`, `/posts/{id}/likes`, `/users/{username}`, `/users/{id}/follow`, `/search`, `/images/{id}`, `/admin/users`, `/admin/posts` (under `/api/v1`). Finalize request/response contracts as features are implemented.
- Use the same-origin/deployment decision to revisit cookies, HTTPS, CORS, and CSRF before any remote hosting.

## 7. Feature behavior

The product contract lives in `docs/PRODUCT.md`. Architecture must support: global newest-first feed; one image and optional caption per post; public user profiles with avatar, bio, post grid, followers/following counts and lists, profile editing/settings; user and caption search; like/unlike; create/delete comments; edit/delete own posts; follow/unfollow; and an admin dashboard to view/manage users and content. Never implement a feature only as static UI when the product requires persisted behavior.

## 8. Security-lab boundaries

Approved categories, **not blanket permission to weaken the app**:

1. SQL injection
2. Stored/reflected XSS as specified
3. Broken function-level authorization
4. Session management flaw
5. IDOR
6. CSRF
7. File-upload vulnerability

The exact vulnerability variant, affected route/component, intended exploit outcome, test accounts/payloads, and secure comparison/fix must be recorded in `docs/VULNERABILITIES.md` before implementation. If that file is absent or a category is unspecified, implement the secure default and continue with unrelated work; ask only when the decision blocks the requested security-lab work. Preserve documented vulnerabilities when refactoring and test them explicitly. Do not introduce additional unapproved weaknesses, leak real secrets, disable protections globally, or place exploitable lab services on the public internet. Use synthetic data and isolated disposable environments. If a vulnerability requires a dangerous host-level operation, use a constrained simulator instead of unrestricted system access.

The professor's guide is written for Flask and includes some intentionally simplified demonstrations; verify real browser/API exploitability rather than assuming that a code pattern alone proves a flaw.

## 9. UI architecture and design

Follow `docs/DESIGN.md`: consult the installed Impeccable plugin/skill for design decisions, use centralized CSS variables in `src/app/globals.css`, Tailwind utilities that reference tokens, breakpoint-stepped responsive typography, max-width feed containers, mobile bottom navigation, desktop sidebar, accessible focus/keyboard behavior, reduced-motion support, and purposeful feedback animations. For async interactions, implement the relevant idle/loading/success/error states with real state transitions, retries, and recoverable messages. Avoid gratuitous global state or overgeneralized components.

## 10. Testing and development workflow

- **Backend:** `pytest` and Flask test client for route contracts, authentication/refresh rotation, roles, database constraints, and image retrieval.
- **Frontend:** component tests where useful and at least manual browser verification of key flows, responsive layouts, and auth expiry/retry.
- **Security lab:** separately labeled tests for each approved vulnerability; tests must demonstrate intended behavior in a disposable environment and should not be mistaken for ordinary regression failures.
- **Fixtures:** seed synthetic admin and ordinary users, posts, comments, and relationships. Never commit production credentials, DB files, token signing keys, or real user data.
- **Environment:** provide `.env.example` and `.env.local.example`; gitignore `.env*` secrets, SQLite files, caches, and generated artifacts. Include concise startup instructions for both services.
- **Codex autonomy:** implement normal features without repeated approval; make sensible small decisions, document consequential assumptions, and run relevant checks. Stop for unresolved architectural/security-scope decisions, public deployment, or any vulnerability not specified in `docs/VULNERABILITIES.md`.

## 11. Open decisions / implementation checkpoints

These do not block creating the architecture file:

- Choose exact JWT library and cookie paths/domains, signing algorithm, and refresh-family reuse policy.
- Decide whether access/refresh JWTs both use cookies (recommended) and define the CSRF demonstration's precise endpoint and browser conditions.
- Set final upload size, supported image formats, and image-serving cache headers.
- Decide migrations tooling: numbered SQL migration scripts are sufficient initially.
- Confirm whether deployment remains localhost-only or moves to an isolated VM/container lab; reassess cookie flags, HTTPS, CORS, DB persistence, and exploit isolation before changing it.
- Specify exactly which sensitive fields, if any, require application-level encryption beyond password hashing and encrypted transport/storage.

**Rule for Codex:** Build the simplest architecture that satisfies the current feature and the documented lab. Never substitute FastAPI, TypeScript, an ORM, a Next.js BFF, cloud image storage, or a new state-management framework without explicit approval.
