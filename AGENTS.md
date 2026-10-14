# AGENTS.md — CSC 489 Social Media Security Lab

## Mission and scope
Build and maintain a working Instagram-inspired **educational security capstone**. The application must be usable as a social network and must preserve only the deliberate, documented lab vulnerabilities. This is **not a production deployment**. Prefer the smallest coherent implementation over extra frameworks, abstractions, or resume-driven complexity.

## Authoritative project decisions
- **Repository:** two primary directories, `frontend/` and `backend/`, plus `docs/`.
- **Frontend:** Next.js **App Router**, JavaScript/JSX **only** (no TypeScript), Tailwind CSS, React Context for genuinely shared state, direct browser-to-Flask API requests.
- **Backend:** Python **Flask** (not FastAPI), Python `sqlite3` with SQLite; keep HTTP routes, controllers, database models/access, auth, configuration, and logging separated.
- **Uploads:** image bytes stored as **SQLite BLOBs**, with appropriate metadata. Do not silently replace this with cloud storage or filesystem image persistence.
- **Authentication:** bcrypt password hashing; JWT access and refresh tokens; refresh-token rotation/revocation; HttpOnly cookie transport; frontend API client retries an expired-access request **once** after refresh. Failed refresh means unauthenticated state and a surfaced authentication error. Avoid parallel refresh races; do not refresh on `403`.
- **Deployment:** undecided. Default to localhost, synthetic accounts, disposable SQLite data, and no publicly exposed vulnerable service.
- **Style:** mobile-first, accessible, polished, responsive, token-driven, and interactive without unnecessary motion.

## Documentation and instruction routing
Read this file for every task. Before editing a subsystem, read its nearest `AGENTS.md` and relevant reference documents:

| File | Governs |
|---|---|
| `docs/PRODUCT.md` | MVP features, roles, flows, acceptance criteria |
| `docs/DESIGN.md` | Impeccable workflow, visual system, typography, responsiveness, interactive states |
| `docs/ARCHITECTURE.md` | Folder layout, SQLite schema, API conventions, JWT lifecycle, boundaries |
| `docs/VULNERABILITIES.md` | **Exclusive allowlist** for intentional vulnerabilities and their verification/remediation |
| `docs/TESTING.md` | Playwright MCP browser QA, functional and security testing, evidence, completion gates |
| `frontend/AGENTS.md` | Next.js-specific engineering and design instructions |
| `backend/AGENTS.md` | Flask-specific engineering, auth, persistence, and vulnerability boundaries |

Use the **latest specific decision** over stale scaffolding comments. The selected backend is Flask, not FastAPI; the chosen feed is global, not following-only. If documents disagree on endpoint paths or an intentional vulnerability's behavior, reconcile the documentation and tests before coding. Do not silently resolve security-sensitive conflicts. Root isolation constraints cannot be overridden by a lower-level file.

## Product requirements — MVP only
- Public accounts, registration/login/logout, profile avatar/bio/editing, follower/following lists and counts.
- **Global chronological feed** (all users, newest first), not a recommendation feed.
- **Single-image posts** with optional captions; create, view, edit and delete own posts as specified in `PRODUCT.md`.
- Like/unlike; create comments and delete one's own comments.
- Follow/unfollow public accounts without approval requests.
- Search **both** users (username/name) and posts (captions).
- Basic admin dashboard for user/post listing and moderation, subject to the explicit lab exceptions.
- Mobile and desktop layouts. No stories, reels, DMs, algorithmic recommendations, or other major scope expansion without approval.

## Frontend rules
- Use `frontend/src/app/` for Next.js App Router routes (`page.jsx`, `layout.jsx`); **do not invent a separate Pages Router hierarchy**.
- Organize `src/features/` by domain; `src/components/` for reusable UI; `src/context/` for shared state; `src/api/` for HTTP and token-refresh logic; `src/layouts/` for shells/navigation; `src/lib/` for utilities.
- **Impeccable is required for design work.** Discover the actual installed Codex plugin/skill instructions and use them for visual design, UI polish, interaction decisions, and design review; never invent plugin commands or claim to have run unavailable tools.
- Define shared CSS custom properties in `src/app/globals.css` (the Next.js equivalent of `index.css`) for colors, type scale, spacing, radii, and container widths; use Tailwind against those tokens. Favor **incremental breakpoint-based font sizes**, responsive max-width containers, mobile bottom navigation, and desktop navigation appropriate to available space.
- Make buttons, dialogs, sliders (if used), tabs, and other controls feel responsive through subtle hover/press/focus/transition feedback; honor `prefers-reduced-motion`.
- Keep reusable components focused. Implement meaningful **idle, loading, success, error, and empty** states *where applicable*, including behavior, disabled actions, retries, messages, and accessibility—not decorative state props everywhere.
- Outside explicitly authorized XSS sinks, render user content as escaped text. Never assume a hidden UI control enforces backend authorization.

## Backend rules
- Flask routes parse HTTP inputs and return responses; controllers coordinate business logic; models/database helpers own SQLite queries; auth helpers handle identity/role verification; config centralizes DB/CORS/roles; logger records diagnostic events without secrets.
- Use explicit validation, consistent JSON errors/status codes, parameterized SQL, bcrypt, and authorization by default **except at the exact approved lab locations**.
- Keep `credentials: 'include'` and configured CORS origins consistent with HttpOnly cookie auth; do not globally relax CORS to demonstrate CSRF.
- Keep refresh rotation and revocation intact except if `docs/VULNERABILITIES.md` explicitly changes a narrowly scoped lab behavior. Protect real signing keys and sensitive values; do not log JWTs, passwords, hashes, or personal secrets.
- Use repeatable schema initialization/migrations and deterministic synthetic seed data. Store no real secrets in git; maintain `.env.example` files.

## Exact approved security-lab scope
Only the following scenarios in `docs/VULNERABILITIES.md` are approved. The seven categories have ten testable subcases:

| ID | Approved behavior |
|---|---|
| V-01 | SQL injection in **login**, with seeded-fixture authentication bypass |
| V-02A | Stored XSS in **post comments** |
| V-02B | Reflected XSS in **search query display** |
| V-03A | Non-admin access to **admin user listing** |
| V-03B | Non-admin access to **admin post deletion** |
| V-04 | **Predictable lab session identifier** with demonstrable isolated session mix-up; preserve JWT cryptography and refresh rotation |
| V-05 | IDOR allowing edit of another seeded user's **public profile fields** |
| V-06 | CSRF on **follow** action |
| V-07A | Upload accepts **non-image file content** as an inert SQLite BLOB |
| V-07B | Upload lacks an **application-level size limit**, tested with bounded disposable data |

- Treat `docs/VULNERABILITIES.md` as the exact contract for routes, preconditions, observable effects, tests, limits, and remediation. Mark affected source with `LAB-VULN: V-XX` and link to the corresponding spec.
- Do not introduce any other intentional weakness, expose sensitive data, weaken all routes, or silently repair an approved vulnerability.
- A predictable auxiliary ID is **not by itself** a session takeover. V-04 must demonstrate the documented lab-specific impact; if it cannot be isolated from normal JWT auth, ask for a decision instead of faking success.
- Keep uploads inert: no executable file hosting, shell execution, host file access, or unbounded resource exhaustion. XSS/CSRF proofs use harmless in-app indicators or fixture state, never exfiltration.
- Anonymous and unrelated sensitive endpoints retain their normal protections. Never use real user data, live credentials, external exfiltration destinations, or public tunnels.
- When an ordinary feature fix might affect an intentional vulnerability, inspect its contract and regression tests before editing; report conflicts instead of silently changing the lab.

## Autonomous Codex workflow
1. **Inspect** the relevant existing code, root and nested instructions, product/architecture/design specifications, and applicable vulnerability entries.
2. **Plan briefly**, then implement routine MVP features, refactors, and bug fixes autonomously. Ask only for major scope/stack/deployment changes or unresolved security-sensitive decisions.
3. **Build vertically:** API + persistence + frontend + appropriate UI states + tests for one coherent feature at a time. Keep components, controllers, and queries appropriately scoped.
4. **Run the app** and verify behavior rather than trusting code inspection alone. Follow `docs/TESTING.md`.
5. **Use installed Playwright MCP** as the primary browser QA interface: discover available commands, navigate the live site, click/type/upload/scroll, test mobile and desktop, inspect observable errors, and retest fixes. Supplement with Flask/SQLite tests and logs when browser inspection is insufficient. Do not claim MCP tests ran if unavailable.
6. **Separate functional QA from vulnerability verification.** An intentionally vulnerable test succeeding is not an ordinary bug. Never make tests green by erasing approved flaws.
7. **Report truthfully** what was changed, tests actually executed, outcomes, affected vulnerability IDs, and unresolved issues. Update `QA_REPORT.md` and `SECURITY_TESTS.md` when specified by `docs/TESTING.md`.

## Completion gate
A feature is complete only when its user journey works, expected loading/error/empty/success behavior is handled, mobile and desktop presentation are checked, relevant API/authorization behavior is tested, and approved vulnerabilities are unchanged unless explicitly being implemented or verified. Never assert browser, security, or integration success without actual evidence.
