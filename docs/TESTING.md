# TESTING.md — Autonomous QA and Security Verification

## Purpose and authority

Codex is responsible for independently exercising the CSC 489 Instagram-style social media MVP in a real browser, diagnosing failures, fixing ordinary defects, and verifying repairs. **Playwright MCP is the primary interactive browser-testing interface.** This file complements root `AGENTS.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/ARCHITECTURE.md`, `docs/VULNERABILITIES.md`, and both scoped `AGENTS.md` files. The vulnerability specification is authoritative for intentional exceptions; do not turn expected lab behavior into a bug fix.

## Tool discovery and execution

1. At the beginning of a QA session, inspect the actual Playwright MCP tools installed in Codex and their instructions. Never invent MCP tool names or claim access to a tool that is unavailable.
2. If Playwright MCP is missing, report the missing integration and the setup needed. Do not claim browser testing passed. Use available unit/API tests in the meantime.
3. Start Flask and Next.js with the repository's documented development commands, using separate terminals/processes and **isolated test configuration**. Verify readiness before opening the browser. Do not silently change ports or origins.
4. Prefer Playwright MCP for real interaction: navigate, click, type, keyboard-operate, scroll, select files, resize viewport, inspect accessible page structure, and capture screenshots when the installed MCP supports these actions.
5. Inspect browser console/network failures through supported MCP capabilities; correlate with Flask logs and test database records. Use direct API tests when browser inspection cannot establish the cause.
6. Run autonomously through a bounded **observe → reproduce → diagnose → change → retest → regression-test** loop. If blocked by credentials, infrastructure, contradictory requirements, or a security-lab boundary, report the exact blocker rather than guessing.
7. Never mark a case PASS based only on code inspection, a screenshot without interaction, or a tool call that failed.

## Environment and test data

- Default to localhost or an explicitly approved isolated lab. Never test the vulnerable build against a public site or real accounts.
- Maintain a disposable SQLite test database separate from development data, and seed synthetic accounts: admin, Alice, Bob, and a third regular user. Seed several posts, comments, follows, and images with deterministic identifiers or discoverable fixture IDs.
- Use throwaway credentials, fake emails, harmless image fixtures, and small inert non-image files. No production secrets, personal records, executable uploads, destructive payloads, or external exfiltration destinations.
- Reset fixtures between security cases; preserve only deliberately generated test evidence. Tests should not depend on previous run order.
- Verify the frontend origin, Flask API origin, CORS allowlist, cookie domain/path, and browser SameSite behavior. Distinguish network/CORS failures from application errors.
- Treat upload storage as SQLite BLOBs; apply bounded fixture sizes and database/storage ceilings even when verifying the intentional missing application-level limit.

## Autonomous browser QA protocol

For each completed feature or substantial change:

1. Read the relevant acceptance criteria in `docs/PRODUCT.md` and design rules in `docs/DESIGN.md`.
2. Open the actual page with Playwright MCP; confirm it loads and inspect console/runtime errors.
3. Perform the user's end-to-end action with real clicks and inputs, not just API requests. Observe the rendered result and persistent server state as appropriate.
4. Exercise applicable **idle, loading, success, error, empty, disabled, and unauthenticated** states. To induce errors, use controlled local test conditions (e.g., invalid credentials, missing record, stopped test API) and restore them afterward.
5. Test mouse and keyboard behavior, focus visibility, labels, form validation, dialogs, navigation, and feedback. Respect reduced-motion preferences.
6. Check at least widths 320, 375, 768, 1024, and 1440 CSS pixels (and an intermediate width if a layout looks fragile). Inspect for horizontal overflow, overlapping navigation, broken image aspect ratios, unreadable text, and unusable touch targets. Capture representative mobile and desktop screenshots.
7. If a failure occurs, reproduce it, collect observable evidence, trace the relevant component/API/controller/model, make the smallest appropriate fix, and repeat the failing interaction plus nearby regression cases.
8. Stop retrying after three unsuccessful fix cycles for the same root issue. Record a blocker with evidence and recommended next action instead of looping indefinitely.

## Functional test matrix

| Area | Browser interactions and assertions |
| --- | --- |
| Registration/login | Register a fixture account, reject invalid input, log in/out, confirm authenticated navigation and refresh persistence |
| JWT lifecycle | Verify authorized requests, expired access-token refresh, one retry of original request, failed refresh clearing auth state, and concurrent-request deduplication; corroborate with API tests/logs |
| Global feed | Newest-first order, empty feed, load/error states, image layout, pagination if implemented |
| Posts | Upload one valid image and optional caption, render it, edit/delete own post, reject unauthenticated actions |
| Likes | Like/unlike, accurate counts, disabled/loading feedback, persistence after reload |
| Comments | Add/delete own comment, ordering, loading/error behavior, safe rendering everywhere except approved V-02A sink |
| Profiles | View public profile, edit own fields, photo/bio/post grid, follower/following counts and lists |
| Follows | Follow/unfollow, prevent duplicates, update counts and lists, validate cross-account behavior |
| Search | Find users by name/username and posts by caption; no-results and error states |
| Admin | Admin UI access and ordinary admin actions; verify anonymous rejection and the specifically approved authorization exceptions separately |
| Images | Valid image preview, broken/invalid content handling, persistence in SQLite, upload feedback |
| Navigation/design | Mobile bottom nav, desktop sidebar, responsive typography/container tokens, interactive controls, keyboard access |

Use isolated backend unit/integration tests for cases that require precise timing, database assertions, HTTP status inspection, or JWT rotation internals. Browser testing and backend tests are complementary, not substitutes.

## Intentional vulnerability verification — separate track

Read `docs/VULNERABILITIES.md` before running any security case. Execute only in the disposable, approved lab, with synthetic accounts and harmless proof-of-concept fixtures. Verify **actual behavior**, not merely a missing check. Each case must also have a normal-behavior control and a scope-control demonstrating that the weakness has not spread.

| ID | Required evidence and boundaries |
| --- | --- |
| V-01 SQL injection / login | Normal bcrypt login works, invalid login fails, approved read-only fixture input causes documented fixture login, other SQL endpoints remain parameterized |
| V-02A stored XSS / comments | Harmless in-page indicator executes for fixture viewer and persists after reload; unrelated captions/bios remain escaped |
| V-02B reflected XSS / search | Harmless indicator executes from search URL without persistence; normal search still functions |
| V-03A/B admin authorization | Fixture non-admin can call the two approved admin endpoints directly, anonymous user cannot, unrelated admin operations remain protected; seeded content only |
| V-04 predictable session IDs | Show predictability and the documented isolated lab session association effect; do not confuse auxiliary ID predictability with forged JWTs; preserve normal JWT verification/rotation |
| V-05 IDOR / profile edit | Alice can change Bob's permitted public bio/display name via target ID; protected account fields cannot be altered; anonymous rejected |
| V-06 CSRF / follow | A separate local-origin browser page induces a fixture follow using the authenticated cookie; verify actual browser SameSite/form behavior, anonymous denial, and other actions protected |
| V-07A/B upload | Small inert non-image BLOB and bounded over-product-limit fixture are accepted; normal images still work; no executable serving, host file write, or unbounded stress |

Do not use browser automation to visit real attacker domains, leak cookies, execute destructive database changes, or attempt filesystem/server compromise. The application should not advertise vulnerabilities in normal user-facing UI.

**Security result semantics:** The intentionally exploitable behavior is a PASS for the *lab contract* but a FAIL under ordinary security posture. Report both clearly. If the lab contract fails, do not silently 'repair' it to be secure or broaden it to make an exploit work. Diagnose and apply only the narrowly approved specification, or ask if the design is incompatible.

## Automation strategy

- Playwright MCP is the default for interactive exploratory testing during Codex sessions.
- Maintain repeatable automated regression tests in the repository using the available test stack; MCP interactions alone are not a persistent test suite. Use Playwright Test for browser regressions if configured, pytest/Flask test client for API/security contracts, and focused component tests where useful.
- Separate normal functional tests from expected-vulnerable security tests so CI results are interpretable. Mark intentional lab assertions explicitly by vulnerability ID.
- Re-run lint/build/unit tests after meaningful changes, browser smoke tests for changed flows, and full regression before declaring a milestone complete.
- Avoid brittle selectors; prefer roles, labels, accessible names, and stable test IDs where appropriate. Never add test-only exploit controls to the ordinary UI.

## Evidence and reporting

Write test findings to `docs/QA_REPORT.md` and vulnerability demonstrations to `docs/SECURITY_TESTS.md` (create these when testing begins). For each case record: date/run, commit or version, environment/origins, fixture state, case ID, steps, expected result, actual observed result, PASS/FAIL/BLOCKED, screenshot/log path, code changes, and retest result. Do not fabricate screenshots or claim a browser run that did not happen.

At the end of each autonomous testing pass, summarize:

- Features exercised and viewport sizes actually tested.
- Bugs found, fixes made, and verified retests.
- Intentional vulnerabilities checked and whether their lab contracts still pass.
- Remaining failures, skipped cases, infrastructure blockers, and next actions.

## Completion gate

A feature is not done until its primary user journey has been exercised in a browser, applicable UI states and responsive layouts have been checked, ordinary defects have been fixed or explicitly documented, backend assertions have passed where relevant, and no unapproved vulnerability has been introduced. If the Playwright MCP server is unavailable, say browser verification is incomplete rather than declaring completion.
