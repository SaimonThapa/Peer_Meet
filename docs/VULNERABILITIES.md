# Vulnerability Specification — CSC 489 Social Media Security Lab

**Status:** Approved lab-only design. **Stack:** Next.js (JavaScript), Flask, Python `sqlite3`, SQLite image BLOBs, bcrypt, JWT access/refresh rotation. **Deployment:** isolated local environment only until a separate deployment security review. **Visibility:** no public-facing vulnerability labels.

## Authority and scope

This document is the allowlist for deliberate security weaknesses. Codex must not add other vulnerabilities or broaden the impact of the listed ones. The source is the course's *Vulnerability Implementation Guide* (CSC 489 Fall 2026), which describes SQL injection, stored/reflected XSS, CSRF, IDOR, broken access control, authentication/session flaws, file upload flaws, and validation/documentation expectations. The specific endpoint names, JWT adaptation, and BLOB upload behavior below are project design choices, not verbatim requirements of that guide.

**Safety boundary:** Synthetic accounts and content only; disposable SQLite database; no external identity provider, real secrets, public network exposure, shell execution, or real user data. Bind development services to loopback, use test credentials, and reset seeded state between security tests. No external exfiltration destinations. Do not commit live secrets or upload untrusted content to third-party services. Maintain functional behavior outside the exact approved flaw locations.

## Vulnerability register

| ID | Category | Approved location | Expected demonstrable flaw |
|---|---|---|---|
| V-01 | SQL injection | `POST /api/auth/login` | Crafted username input changes login query semantics and authenticates as a seeded account without knowing its password |
| V-02A | Stored XSS | Post comments, `POST /api/posts/<post_id>/comments` and comment rendering | Persisted attacker-authored HTML executes when a seeded test user views the comment |
| V-02B | Reflected XSS | Search query display, `GET /search?q=...` | URL-controlled HTML executes in the rendered search page without being stored |
| V-03A | Broken authorization | `GET /api/admin/users` | Authenticated non-admin can read admin-only user listing |
| V-03B | Broken authorization | `DELETE /api/admin/posts/<post_id>` | Authenticated non-admin can delete a seeded post using an admin-only endpoint |
| V-04 | Predictable session identifiers | Lab session identifier associated with JWT login sessions | Identifier is predictable and permits a demonstrable session mix-up or takeover in the isolated lab |
| V-05 | IDOR | `PATCH /api/users/<user_id>/profile` | Authenticated user can edit another seeded user's public profile fields by changing the ID |
| V-06 | CSRF | `POST /api/follows` | A cross-site form submission can cause a logged-in seeded user to follow an account without their intent |
| V-07A | Unrestricted file type | `POST /api/posts` | Post upload accepts non-image bytes as an image BLOB without content validation |
| V-07B | Unrestricted upload size | `POST /api/posts` | Oversized BLOB uploads are accepted without an application-level limit in the lab's bounded test environment |

The seven approved categories contain ten individually verifiable demonstrations. All endpoint paths are proposed contracts and should be made consistent with the final API router; any changes must be reflected in this document and tests before implementation.

## Baseline architecture and invariants

- Preserve bcrypt password hashes for registered users. V-01 is a narrowly scoped SQL query-construction exception, **not** approval for plaintext password storage. A login bypass must be validated against a deliberately seeded fixture while normal credentials still work.
- Preserve short-lived access JWTs, refresh JWT rotation, revocation/reuse tracking, HttpOnly cookies, and the shared frontend API client's single-refresh-and-retry behavior. The predictable session identifier is a separate, explicitly scoped lab weakness; do not make JWT signatures guessable, expose signing keys, or disable refresh rotation.
- Normal API endpoints authenticate and authorize properly. Only V-03 and V-05 omit the specified checks. Never return password hashes, JWTs, refresh tokens, encryption keys, or private user details in the admin listing.
- Store post images in SQLite BLOB columns with MIME metadata. For V-07, non-image content must be stored inertly and delivered only as a download (`Content-Disposition: attachment`, `application/octet-stream`, `X-Content-Type-Options: nosniff`) when not recognized as an image; never execute or interpret uploaded files.
- Other rendering surfaces use normal React escaping. Only the explicitly designated XSS sinks may render untrusted HTML.
- Normal state-changing endpoints retain appropriate CSRF defenses; only the follow endpoint is exempted for V-06. Do not globally weaken CORS or cookie configuration to force an exploit.
- Log lab events without credentials or token values. Avoid exposing debugger consoles, arbitrary file paths, and traceback details.

## Detailed lab contracts

### V-01 — SQL injection in login

**Location:** Flask `POST /api/auth/login`, authentication controller and its single SQL lookup.

**Expected:** A controlled input in the username field alters SQL query semantics and causes login as a predefined fixture account without the account password. Ordinary login still uses bcrypt verification where applicable. This lab-specific exception must not change search, profile lookup, or any other SQL query.

**Boundary:** Query must be read-only; use a test database with least-privilege filesystem permissions and fixture-only accounts. Do not permit stacked queries, arbitrary writes, or access to non-fixture data.

**Verify:** Correct credentials work; incorrect credentials fail; a documented local injection fixture succeeds; unrelated endpoints remain parameterized. Reset the database after the test.

**Remediate:** Parameterize SQL inputs, separate user lookup from bcrypt verification, and remove the exceptional query path.

### V-02A — Stored XSS in comments

**Location:** Comment submission/retrieval API and the specific comment-body renderer in Next.js.

**Expected:** A benign, self-contained test HTML event handler entered as a comment executes when the fixture viewer loads that comment. It persists across a reload.

**Boundary:** Do not introduce raw HTML rendering into post captions, profiles, admin pages, or other components. Test only harmless in-page indicators; never transmit cookies or session information.

**Verify:** The indicator runs on a second fixture account's view and after reload; ordinary text comments still render; safe surfaces escape the same text.

**Remediate:** Render comments as text nodes and remove unsafe HTML sinks, or apply a carefully configured sanitizer when rich text is explicitly needed.

### V-02B — Reflected XSS in search

**Location:** Next.js `/search` query heading or result summary. The Flask search API can safely return the query as JSON; reflection in JSON alone is not XSS.

**Expected:** A harmless HTML event-handler fixture passed in `q` executes when the search page renders it. It does not persist to the database.

**Boundary:** Only the search query display is intentionally unsafe; search result cards and user names remain escaped.

**Verify:** Test link triggers indicator, normal search still works, and the same value rendered in a safe component is inert.

**Remediate:** Render query using ordinary JSX text interpolation, never `dangerouslySetInnerHTML` for URL data.

### V-03A / V-03B — Broken admin authorization

**Locations:** `GET /api/admin/users` and `DELETE /api/admin/posts/<post_id>`.

**Expected:** Logged-in non-admin can list safe account metadata and delete a seeded post by calling the backend directly despite admin-only UI navigation. Anonymous users are still rejected.

**Boundary:** Limit the listing to `id`, `username`, `display_name`, and `role`; no email, hashes, tokens, or sensitive fields. Delete only seeded content in the isolated lab; keep account deletion out of scope.

**Verify:** Admin and ordinary user can invoke the two endpoints; anonymous request is denied; ordinary users cannot access unrelated privileged endpoints.

**Remediate:** Enforce a server-side admin role dependency/decorator for both endpoints, not merely a hidden frontend link.

### V-04 — Predictable session identifier

**Location:** An explicit lab-only session registry associated with the normal JWT login lifecycle.

**Expected:** A sequential or otherwise guessable lab session ID is exposed to the authenticated client and can be used in a specifically designated lab session lookup to demonstrate unauthorized session association with another fixture account. **Do not use the predictable value as a JWT signing secret or refresh token.**

**Design dependency:** JWTs are normally self-contained and signed; a predictable auxiliary ID by itself does not cause takeover. Codex must define and document the server-side mapping and the one intentionally missing ownership check that makes this demonstration real. If this cannot be done without introducing an additional, broader authorization weakness, stop and request a design decision rather than claiming V-04 works.

**Boundary:** Lab registry only, fixture accounts only, no access to real JWTs or refresh token values. Normal JWT verification and rotation remain intact.

**Verify:** Consecutive session IDs are predictable; a controlled cross-account lab action succeeds using a guessed ID; normal JWT-protected endpoints still reject unauthenticated requests.

**Remediate:** Use cryptographically random session identifiers and bind each session lookup to its authenticated owner, or remove the redundant session registry entirely.

### V-05 — IDOR in profile editing

**Location:** `PATCH /api/users/<user_id>/profile`.

**Expected:** An authenticated fixture user changes another fixture user's **public** display name or bio by altering the route ID. The profile owner sees the change afterward.

**Boundary:** Restrict writable fields to `display_name` and `bio`. Never allow changing password, email, role, account status, JWT/session fields, or other private data. Anonymous users remain denied.

**Verify:** Owner update works; cross-account fixture update works; sensitive fields cannot be mass-assigned; unrelated edit endpoints enforce ownership.

**Remediate:** Require authenticated user ID to match the target user ID (or a separately authorized admin), and whitelist update fields.

### V-06 — CSRF in follow action

**Location:** `POST /api/follows`, authenticated using the browser's cookies.

**Expected:** A separate local test page submits a browser-compatible form that causes a logged-in fixture user to follow a seeded target account without an explicit action in the app.

**Design dependency:** The endpoint must accept the form encoding used by the test; a JSON-only endpoint is not automatically vulnerable to ordinary HTML form submission. Cookie SameSite behavior and the test origins must be documented and tested in a real browser. Do not mislabel missing CSRF tokens as exploitable unless the cross-site request actually succeeds.

**Boundary:** Follow/unfollow fixture accounts only; no account takeover, credential changes, or other state-changing CSRF exceptions. Keep CORS restricted; CORS alone is not a CSRF defense.

**Verify:** Cross-site form changes the follower relationship; logged-out browser cannot; a different protected state-changing endpoint rejects equivalent cross-site requests.

**Remediate:** Add CSRF tokens and/or strict Origin verification, and configure appropriate SameSite cookies while retaining authenticated server-side ownership checks.

### V-07A / V-07B — File upload flaws

**Location:** `POST /api/posts`, single-image upload stored as SQLite BLOB.

**Expected:** The endpoint stores arbitrary non-image bytes supplied as a post image, and separately accepts a bounded oversized fixture that exceeds the normal product's intended image limit. The resulting records remain viewable as metadata; invalid content need not render as an image.

**Boundary:** No executable uploads, shell invocation, filesystem writes from uploaded filenames, active HTML/SVG serving, or unbounded stress tests. Enforce an infrastructure-level hard ceiling for test safety even though the application intentionally omits its normal file-size restriction. Cap SQLite database size and use disposable storage.

**Verify:** Normal JPEG/PNG uploads work; a small harmless text fixture is accepted as a BLOB; a moderately oversized fixture above the intended product limit is accepted without crashing the service; non-image retrieval is inert.

**Remediate:** Check actual file signatures and decoded image format, enforce strict MIME/extension policy, reject oversize content at the API and ingress layers, and use bounded storage quotas.

## Test documentation required for each ID

Each vulnerability receives an entry in `docs/SECURITY_TESTS.md` with: identifier and severity, endpoint/component path, code location, fixture preconditions, benign reproduction steps, observed result, impact within the lab, remediation, and a test evidence screenshot or log. Store test fixtures separately from production seed data. Tests must demonstrate the intended behavior rather than merely inspect code for missing controls.

## Codex execution policy

1. Read root `AGENTS.md`, `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, and this file before modifying a listed feature. If they conflict, ask for clarification; this file controls **only** intentional security exceptions.
2. Implement the normal feature and tests first, then introduce the smallest approved flaw and its isolated regression test. Never spread a flaw to shared authentication, authorization, SQL, rendering, or upload helpers.
3. Annotate approved exceptions with `LAB-VULN: V-XX` and a reference to this document. Do not silently fix those exceptions during cleanup; report them separately from ordinary defects.
4. Do not add command injection, exposed secrets, plaintext password storage, insecure debugger access, arbitrary server-side file execution, or any vulnerability outside the register.
5. Preserve usable UI states (idle/loading/success/error), mobile/desktop responsiveness, and functional MVP flows.
6. Stop and ask if the selected flaw is technically incompatible with the agreed architecture or cannot be safely verified. Never fake exploitability or claim a passing test without execution.
7. Do not deploy or expose the vulnerable build publicly. Before any shared deployment, require explicit approval of isolation, network access, test accounts, rate/size ceilings, reset procedure, and shutdown plan.

## Source mapping

The course guide's relevant sections are: §1 SQL Injection; §2 Stored/Reflected XSS; §3 CSRF; §4 IDOR; §5 Broken Access Control; §7 Session Management Flaws; §8 File Upload Vulnerabilities; and its final testing and documentation checklist. Its examples are Flask-oriented; this project's JWT-specific session mapping, image-BLOB treatment, and endpoint choices are adaptations requiring real tests.
