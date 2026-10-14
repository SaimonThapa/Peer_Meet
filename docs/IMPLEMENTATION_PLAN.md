# Implementation Plan

## Current Status

- Repository instructions, product, architecture, design, vulnerability, testing, frontend, and backend guidance have been read.
- Impeccable v4.3.1 instructions were loaded for UI/design workflow.
- Playwright MCP tools are available for browser QA.
- The repository is not currently a Git repository.

## Milestones

### 1. Project Initialization

- Backend Flask app factory, config, logging, CORS, SQLite helpers, migrations, seed data, and pytest setup.
- Frontend Next.js App Router, Tailwind, API client, AuthContext, app shell, reusable primitives, and environment examples.
- Acceptance: both services start locally and `GET /api/v1/health` is reachable from the frontend.

### 2. Authentication

- Register, login, logout, current user, rotating refresh cookies, and frontend one-refresh retry.
- Acceptance: synthetic users can sign in/out, auth survives navigation, failed refresh returns unauthenticated state.

### 3. Social MVP

- Global newest-first feed, single-image posts as SQLite BLOBs, comments, likes, profiles, follow/unfollow, and search.
- Acceptance: Alice/Bob seeded journeys work end to end with persisted data.

### 4. Administration

- Admin dashboard for user/post listing and post moderation with explicit confirmation.
- Acceptance: admin can view accounts and remove seeded posts; ordinary UI hides admin controls.

### 5. Approved Security Labs

- Implement only V-01 through V-07B at the documented locations with `LAB-VULN` source markers.
- Acceptance: each lab case has a safe local verification entry in `docs/SECURITY_TESTS.md`.

### 6. QA and Polish

- Browser QA with Playwright MCP at mobile and desktop widths, backend tests, build/lint checks, and Impeccable detector for changed UI targets.
- Acceptance: `docs/QA_REPORT.md` and `docs/SECURITY_TESTS.md` record executed evidence, skipped cases, and remaining risks.

## Dependencies

- Authentication gates post creation, likes, comments, follows, profile editing, and admin actions.
- Image BLOB storage gates posts, avatars, feed rendering, and upload vulnerability verification.
- Seed data gates security labs and repeatable QA.
- Browser QA requires both Flask and Next.js running on their configured localhost ports.

## Progress Checklist

- [x] Read instruction system
- [x] Discover Impeccable guidance
- [x] Discover Playwright MCP availability
- [x] Create implementation plan
- [x] Initialize backend
- [x] Initialize frontend
- [x] Verify local startup
- [x] Implement authentication
- [x] Implement feed/posts
- [x] Implement profiles/follows
- [x] Implement comments/likes
- [x] Implement search
- [x] Implement admin
- [ ] Verify approved vulnerabilities
- [x] Complete initial QA report
