# PRODUCT.md — Social Media Security Lab

## 1. Product overview

Build an Instagram-inspired social media minimum viable product (MVP) for the CSC 489 Fall 2026 web security capstone. The application must work as a recognizable social network while providing a controlled educational environment for demonstrating separately specified intentional vulnerabilities.

**Technology constraints:** Next.js with JavaScript/JSX (not TypeScript), Tailwind CSS, Flask REST API, and SQLite.

**Product principle:** Build coherent, usable social features first. Intentional security behavior belongs in `docs/VULNERABILITIES.md`; do not infer insecure implementation requirements from this product document.

## 2. Goals

- Allow multiple demo users to register, sign in, publish image posts, and interact with one another.
- Provide a global, newest-first feed of public posts.
- Support public profiles, follows, comments, likes, and search.
- Provide basic administrative content and account management.
- Keep the scope small enough to build, test, and demonstrate during the capstone.

## 3. Roles and permissions (intended product behavior)

### Visitor (signed out)
- Can view public posts and public profiles, including public search results.
- Must sign in to create or modify content, like, comment, or follow.

### Registered user
- Can create and manage their own posts, profile, and comments.
- Can like/unlike posts and follow/unfollow other users.
- Can browse public profiles, posts, and search results.

### Administrator
- Has normal user capabilities.
- Can view users and posts, remove posts, and manage accounts using an admin dashboard.

These are the **intended product permissions**. Any deliberate deviation must be explicitly defined in `docs/VULNERABILITIES.md` and tested in the isolated lab.

## 4. Core features and acceptance criteria

### 4.1 Registration, login, and logout

- Registration requires a unique username and password; collect only data necessary for the MVP.
- Existing users can log in and log out.
- Authentication state persists across normal page navigation.
- Signed-out users are prompted to sign in when attempting authenticated actions.
- Show understandable feedback for invalid credentials, duplicate usernames, and failed requests.

**Acceptance:** A new user can register, log in, navigate the app, and log out; authenticated actions are unavailable through the ordinary UI after logout.

### 4.2 Global feed

- Home displays posts from **all public users**, not only followed accounts.
- Order posts by creation time, newest first; use a deterministic tie-breaker for equal timestamps.
- Each feed card shows the image, author, caption if present, timestamp, like count, comment count, and interaction controls.
- Clicking an author opens their profile; clicking a post opens its detail view.
- Include loading, empty, and error states.
- Use simple pagination or incremental loading to avoid fetching an unlimited number of posts.

**Acceptance:** Posts from two different users appear together, with the most recently created post first.

### 4.3 Posts

- A signed-in user can create a post with **exactly one image** and an optional caption.
- Users can view a post's dedicated detail page.
- A post author can edit its caption and delete their post.
- Deleting a post removes it from normal feed and profile views and handles associated likes/comments consistently.
- Show upload progress or pending state, success feedback, and actionable errors.
- Image format and size rules will be defined by architecture and security-lab specifications; do not assume any intentionally unsafe upload behavior here.

**Acceptance:** A user uploads one image, publishes a post without a caption, later edits its caption, and can delete the post.

### 4.4 Likes

- Signed-in users can like or unlike any public post.
- Each user can have at most one active like per post.
- The UI displays whether the current user has liked a post and the total count.
- The count remains consistent between feed, post detail, and profile views.

**Acceptance:** Repeated clicks toggle the current user's like without creating duplicate likes.

### 4.5 Comments

- Signed-in users can add text comments to public posts.
- Show comments with author, content, and timestamp.
- Users can delete their own comments.
- Comment editing, threaded replies, and reactions are outside the MVP.
- Provide empty, submitting, and error states.

**Acceptance:** A comment appears on the correct post; its author can delete it; another normal user cannot delete it under intended product permissions.

### 4.6 Public profiles

- Every user has a public profile page identified by username.
- Display profile image, username, display name if provided, bio, post grid, post count, follower count, and following count.
- Profile owners can edit their profile details and profile image.
- Provide lists of accounts following the user and accounts the user follows.
- Display a clear empty state for accounts with no posts.
- Provide basic account settings for editing profile information and logging out; do not add complex preferences unless needed.

**Acceptance:** A profile shows its owner's posts and accurate relationship counts; editing a profile updates its public display.

### 4.7 Follow relationships

- Signed-in users can follow or unfollow any other public account.
- Following does not require approval.
- Users cannot follow themselves.
- Prevent duplicate follow relationships.
- Follower/following counts and lists update consistently.
- Following does **not** change the global feed's inclusion rule in this MVP.

**Acceptance:** User A follows User B; both profiles reflect the relationship, and User A can unfollow User B.

### 4.8 Search

- A single search experience supports **users and posts**.
- User search matches usernames and display names.
- Post search matches caption text.
- Clearly separate user and post results, either through tabs or labeled sections.
- Support an empty query, no results, loading, and request failures.
- Selecting a result navigates to the appropriate public profile or post.

**Acceptance:** Searching for a known username finds that user, and searching for a word in a caption finds the corresponding post.

### 4.9 Basic admin dashboard

- An administrator can open an admin dashboard.
- Dashboard provides a list of users and posts.
- Administrator can remove posts and manage user accounts (at minimum, view accounts and disable or delete a selected demo account).
- Destructive actions require clear confirmation in the UI.
- Admin actions should produce clear success/error feedback.
- Ordinary users should not be offered admin controls in the normal UI.

**Acceptance:** An administrator can inspect users/posts and remove a selected demo post; ordinary users do not see admin navigation.

## 5. Suggested screens and navigation

- `/` — Global feed
- `/login` — Login
- `/register` — Registration
- `/explore` — Search users and posts
- `/posts/new` — Create post
- `/posts/[id]` — Post detail and comments
- `/[username]` — Public profile and post grid
- `/settings` — Edit own profile and basic account settings
- `/admin` — Admin dashboard

These are proposed frontend routes; finalize them in `docs/ARCHITECTURE.md`. Do not couple product behavior to a particular Flask endpoint naming convention here.

## 6. User journeys

1. **New member:** Register → log in → edit profile → publish an image → see it at the top of the global feed.
2. **Social interaction:** Find a user → open profile → follow → open a post → like → comment → optionally unlike/unfollow.
3. **Content management:** Open own post → edit caption → delete post → verify it disappears from feed and profile.
4. **Discovery:** Search a username → open profile; search caption text → open matching post.
5. **Administration:** Log in as admin → inspect users/posts → remove a demo post or manage a demo account.

## 7. UX expectations

- Mobile-first responsive layout, also usable on desktop.
- Familiar social-feed layout without requiring an exact copy of Instagram's branding or visual assets.
- Consistent navigation, readable typography, accessible labels, keyboard-operable controls, and visible focus states.
- Meaningful loading, empty, error, and confirmation states for major flows.
- Avoid unnecessary animations, recommendation algorithms, and complex real-time systems.
- Visual specifications and reusable component conventions belong in `docs/DESIGN.md` and `frontend/AGENTS.md`.

## 8. MVP exclusions

Do **not** implement these unless the user explicitly expands scope:

- Stories, reels, video uploads, or livestreaming.
- Direct messages or group chats.
- Private accounts or follow approval requests.
- Notifications or push notifications.
- Algorithmic recommendations or personalized feed ranking.
- Multiple-image/carousel posts.
- Hashtags, mentions, saved posts, or comment editing.
- Third-party OAuth, email verification, password recovery, or real email delivery.
- Production-scale media processing, CDN integration, or cloud storage.

## 9. Security lab boundary

The following seven vulnerability categories are approved for later specification:

1. SQL injection.
2. Cross-site scripting (XSS).
3. Authorization flaw (broken function-level access control).
4. Session management flaw.
5. Insecure direct object reference (IDOR).
6. Cross-site request forgery (CSRF).
7. File upload vulnerability.

**Do not implement a vulnerability solely because it appears above.** Consult `docs/VULNERABILITIES.md` for each approved location, behavior, test, and limitation. Do not silently add extra weaknesses or silently repair a deliberately approved one. Keep security demonstrations limited to isolated, disposable environments with synthetic data; deployment remains undecided.

## 10. Delivery criteria

The MVP is complete when:

- All core user journeys above work end to end with Flask and SQLite.
- Screens are responsive and have reasonable loading, empty, and error handling.
- Seed/demo data supports multiple users, posts, likes, comments, and follow relationships.
- Basic admin management works as defined by the product specification, apart from explicitly documented intentional flaws.
- The development setup is reproducible from repository instructions.
- Any deliberate security exceptions are traceable to `docs/VULNERABILITIES.md`, not hidden in general product requirements.

## 11. Guidance for Codex

- Treat this document as the **source of truth for feature scope and expected UX behavior**.
- Implement the smallest coherent version of each feature before adding extras.
- Make routine implementation decisions autonomously within these requirements.
- Do not add unrequested features, dependencies, or complexity.
- If architecture or design choices are unspecified, consult `docs/ARCHITECTURE.md`, `docs/DESIGN.md`, and scoped `AGENTS.md` files; if they do not exist, choose simple, reversible defaults.
- If a product requirement conflicts with an intentional vulnerability, preserve the approved lab behavior **only at the documented location** and keep the rest of the product functional.
