# Frontend Agent Instructions — CSC 489 Social Security Lab

## Scope and precedence
These instructions apply to everything under `frontend/`. Read the repository root `AGENTS.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/ARCHITECTURE.md`, and `docs/VULNERABILITIES.md` before changing a feature. This file governs frontend implementation, not the definitions of intentional vulnerabilities. If instructions conflict, stop and identify the conflict rather than silently weakening protections. Follow approved lab exceptions only at the exact locations specified in `docs/VULNERABILITIES.md`.

## Stack and boundaries
- Next.js **App Router** using JavaScript/JSX only; no TypeScript, Pages Router, or unnecessary framework additions.
- Tailwind CSS with centralized CSS custom properties in `src/app/globals.css`. Do not create an `index.css` just to imitate Vite conventions.
- Flask REST backend with Python `sqlite3`, reachable via direct browser requests. Frontend must never access SQLite or store image BLOBs itself.
- React Context for genuinely global state (principally authentication). Local state and feature hooks for UI, forms, feed pagination, and mutations. Do not introduce Redux, Zustand, or TanStack Query without a demonstrated need and explicit architecture update.
- Keep dependencies small. Use JavaScript modules, clear naming, and simple composition.

## Expected structure
```
frontend/
  AGENTS.md
  src/
    app/                 # route tree: page.jsx, layout.jsx, loading.jsx, error.jsx
      globals.css
      page.jsx           # global chronological feed
      login/page.jsx
      register/page.jsx
      upload/page.jsx
      search/page.jsx
      profile/[username]/page.jsx
      settings/page.jsx
      admin/page.jsx
    api/                 # fetch client, endpoint-specific request functions
    context/             # AuthContext and its provider
    layouts/             # shared shell, mobile nav, desktop sidebar
    features/            # auth, posts, comments, likes, follows, profiles, search, admin
    components/          # reusable UI primitives and feedback components
    lib/                 # pure helpers and constants
```
The `app/` directory owns **routing**, not feature logic. Do not create a parallel `pages/` route hierarchy. Group closely related feature components, hooks, and helpers together; move components to `components/` only when genuinely shared. Use Server Components by default where feasible; add `'use client'` only for browser interaction, hooks, Context, and explicitly approved client-side security lab sinks. Avoid calling a browser-only auth API from a Server Component without an appropriate architecture decision.

## Impeccable-first design workflow
- For **every** design task (new screen, visual component, layout, typography, spacing, color, interaction, responsive change, or design review), discover and read the installed **Impeccable** plugin/skill instructions in Codex and follow its actual workflow. Do not invent commands or claim it ran when unavailable.
- Use `docs/DESIGN.md` as the project design contract. Maintain a coherent, photo-first visual identity without copying Instagram trademarks or proprietary assets.
- Apply Impeccable recommendations consistently through shared tokens and components, not isolated one-off overrides. If Impeccable is unavailable, state that limitation and continue using the documented design system.

## CSS tokens, typography, and responsiveness
- Centralize semantic color, typography, spacing, radii, shadows, motion, and container tokens in `src/app/globals.css`; map Tailwind classes to tokens where supported by the project's Tailwind configuration.
- Use a named typography scale such as `--text-xs`, `--text-sm`, `--text-base`, `--text-lg`, `--text-xl`, `--text-2xl`, `--text-3xl`, with deliberate **fixed increments at breakpoints**. Do not use unbounded viewport-dependent font sizing.
- Define shared layout tokens such as `--feed-max`, `--page-max`, `--sidebar-width`, `--mobile-nav-height`, `--page-gutter`, and minimum touch-target size. Prefer flexible widths with max-width constraints, CSS Grid/Flexbox, and safe-area insets.
- Design mobile-first from ~320px upward. Mobile: single-column feed, compact top bar, accessible bottom navigation. Desktop: sidebar navigation and centered feed with bounded width. Tablet: adaptive navigation and gutters.
- Test at approximately 320, 375, 768, 1024, and 1440px plus intermediate widths. Avoid horizontal overflow, clipped controls, and unstable image layouts. Reserve image space using dimensions/aspect ratios.
- Maintain clear hierarchy, readable contrast, visible focus, 44px-ish touch targets, and reduced-motion support.

## Components and UI state contracts
- Shared primitives may include `Button`, `IconButton`, `Input`, `Textarea`, `Avatar`, `Dialog`, `Toast`, `Spinner`, `Skeleton`, `EmptyState`, and `ErrorMessage`. Feature components may include `PostCard`, `PostComposer`, `CommentList`, `CommentForm`, `FollowButton`, `ProfileHeader`, `SearchResults`, and `ImageUploader`.
- Do not build an abstraction solely for theoretical reuse. Keep interfaces small and responsibilities clear. Use composition instead of prop-heavy universal components.
- Every asynchronous or mutation-driven feature must define the **applicable** states: idle, loading, success, error, and where meaningful empty/disabled. Static presentational elements do not need fake loading/success props.
- State must drive actual behavior: disable duplicate submissions, show loading feedback, preserve/recover input on failure, expose retry actions where appropriate, announce errors and confirmations accessibly, and reset transient success messages when appropriate.
- Prefer a local state machine or a clear status enum (`idle | loading | success | error`) per operation; avoid contradictory boolean flags. Keep server-derived state distinct from form drafts and transient UI state.
- Interactive controls should feel alive through subtle hover/press/focus/selection feedback and purposeful transitions, not constant motion. Support keyboard and touch; honor `prefers-reduced-motion`.
- Avoid unnecessary optimistic updates. If used for likes/follows, reconcile with the server and roll back on failure.

## AuthContext and API client
- `AuthContext` owns authenticated user, auth status (`checking`, `authenticated`, `unauthenticated`), and actions such as login, logout, and refresh-current-user. Do **not** put all feed data or all forms into Context.
- Use a centralized `src/api/client.js` (or equivalent) for the Flask base URL, JSON/form-data handling, consistent error shapes, and cookie-aware requests. Configure exact allowed origins on Flask; never assume wildcard credentialed CORS.
- Use `credentials: 'include'` on requests requiring cookie auth. Access/refresh JWTs live in HttpOnly cookies; do not read tokens from JavaScript, expose them in components, or store them in `localStorage`/`sessionStorage`.
- On an access-token-related `401`, attempt **one** refresh via the approved endpoint; if successful, retry the original request **once**. Deduplicate concurrent refreshes with a shared in-flight promise. Never recursively refresh the refresh endpoint, never loop retries, and do not refresh on `403`.
- On refresh failure, transition to unauthenticated, clear sensitive in-memory user state, and propagate a typed authentication error for the UI to handle. Do not swallow non-authentication errors.
- Handle `FormData` uploads without manually setting a multipart boundary. Treat server response and error bodies as untrusted data.
- For normal state-changing operations, follow the backend's CSRF contract. The **single** approved follow-action CSRF exception is specified in `docs/VULNERABILITIES.md`; do not remove protection globally.

## Features and navigation
Implement only the product requirements in `docs/PRODUCT.md`:
- Global feed ordered newest-first; post cards with one image and optional caption.
- Register, login, logout, session restoration, and protected actions.
- Create/edit/delete own posts, like/unlike, add/delete own comments.
- Public profiles with editable own details, photo, bio, post grid, follower/following counts and lists.
- Follow/unfollow, user search, caption search, and a basic admin dashboard.
- Keep route navigation semantic (`Link` for navigation, `button` for actions). Show loading, empty, error, and unauthorized states as appropriate. Do not invent stories, reels, DMs, or other scope expansions.

## Approved vulnerability-specific frontend boundaries
`docs/VULNERABILITIES.md` is the **only** authorization for intentionally unsafe frontend behavior:
- **V-02A stored XSS:** the designated comment rendering sink only. All other user content must be rendered as text, not HTML.
- **V-02B reflected XSS:** the designated `/search?q=...` query display only. Other query strings and search results remain normally escaped.
- **V-03 broken authorization:** UI may hide admin links from ordinary users for normal UX, but frontend visibility is not an authorization control. The approved backend admin exceptions govern the lab behavior.
- **V-05 IDOR:** profile editing requests may contain the targeted user ID as defined in the lab specification; do not add unauthorized editing affordances throughout the UI.
- **V-06 CSRF:** the follow endpoint has a narrowly scoped backend exception; do not weaken the entire frontend API client or unrelated mutations.
- **V-01, V-04, V-07:** SQL login, predictable lab session ID, and upload validation weaknesses are backend-owned. Do not create extra frontend security defects to make them work.
- Do not display vulnerability labels, exploit hints, or challenge badges in the ordinary application UI. Keep testing fixtures and exploit demonstrations outside user-facing components. Use synthetic data and local-only environments.
- Do not globally disable escaping, CSP, authorization handling, CSRF defenses, or browser security checks. Do not introduce additional flaws under the pretext of realism.

## Accessibility and quality gates
- Use semantic landmarks, labels, descriptive alt text, accessible dialogs, keyboard operation, and visible focus states. Announce asynchronous status changes when useful.
- Validate required fields in the UI for usability, but never assume client validation is a security boundary. Preserve error details suitable for users without exposing sensitive backend internals.
- Add focused component/interaction tests for forms, state transitions, feed behavior, responsive navigation, and auth retry handling. Add explicit regression checks ensuring approved XSS sinks remain isolated and unrelated content is escaped.
- Run the project's lint/build/tests after meaningful changes. Fix regressions without silently removing an approved vulnerability. When a vulnerability conflicts with normal accessibility or UX expectations, document the exact exception and its scope.

## Codex autonomy and completion checklist
Work autonomously on approved product features and routine refactors. Before substantial work, inspect relevant project documents and existing patterns; make a concise implementation plan, implement the smallest coherent slice, test it, and summarize changed files and results. Ask only when requirements conflict or a new security exception would be necessary.

Before declaring a frontend task complete, verify: (1) product behavior, (2) Impeccable/design-token compliance, (3) mobile and desktop layout, (4) keyboard/accessibility behavior, (5) appropriate idle/loading/success/error transitions, (6) auth/CORS/cookie behavior where relevant, (7) no unapproved vulnerabilities, and (8) tests/build status.
