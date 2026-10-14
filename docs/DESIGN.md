# DESIGN.md — Social Security Lab Design System

## Purpose and authority
This document governs the frontend experience for the CSC 489 Instagram-inspired social media MVP. Follow the root `AGENTS.md` and `docs/PRODUCT.md` for project-wide and functional requirements. Keep intentional security flaw definitions in `docs/VULNERABILITIES.md`; do not introduce vulnerabilities as a styling shortcut.

## Impeccable-first design workflow
The Impeccable plugin/skill installed in Codex is the primary design reference for every design aspect: layout, typography, spacing, color, visual hierarchy, components, interactions, responsiveness, accessibility, and design review.

Before designing or significantly changing a screen or reusable component:
1. Discover and read the actual installed Impeccable instructions and applicable references. Do not invent skill commands or assume an API.
2. Apply its relevant design guidance, then reconcile with the explicit project requirements below. If guidance conflicts, flag the conflict and follow root `AGENTS.md` and product requirements.
3. Build using shared tokens and reusable components; review mobile and desktop screenshots and interaction states.
4. When Impeccable is unavailable, disclose this and use the documented project design system rather than claiming it was consulted.

## Product aesthetic
Create a clean, polished, modern photo-first social app. Prioritize content, legibility, clear hierarchy, and recognizable interaction patterns without copying Instagram branding, logos, or proprietary assets. Choose a coherent visual identity with Impeccable before implementing screens. Keep decorative elements restrained and make important actions obvious.

## Technology
- Next.js App Router, JavaScript/JSX (no TypeScript), Tailwind CSS.
- Prefer CSS custom properties in the frontend's global stylesheet (normally `frontend/src/app/globals.css` for App Router; `index.css` only if that is the actual project entry stylesheet).
- Prefer Tailwind utilities mapped to CSS variables. Avoid hard-coded one-off values in components unless there is a justified exception.
- Use semantic HTML, accessible form labels, and proper button/link roles.

## Centralized design tokens
Establish and maintain tokens for:
- Color: page, surface, elevated surface, text, muted text, border, primary action, destructive action, success, warning, and error, including hover/disabled variants.
- Typography: font family, weight, line height, and a named scale (`--text-xs`, `--text-sm`, `--text-base`, `--text-lg`, `--text-xl`, `--text-2xl`, `--text-3xl`).
- Spacing: consistent small-to-large spacing increments.
- Layout: content maximum widths, sidebar width, header height, mobile navigation height, and safe-area insets.
- Shape and effects: radii, borders, shadows, transition durations, and easing.

Example starting point, subject to Impeccable design review:
```css
:root {
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.75rem;
  --feed-max: 40rem;
  --page-max: 80rem;
  --tap-min: 2.75rem;
  --motion-fast: 140ms;
  --motion-normal: 220ms;
}
@media (min-width: 48rem) {
  :root { --text-2xl: 1.75rem; --text-3xl: 2rem; }
}
@media (min-width: 64rem) {
  :root { --text-2xl: 2rem; --text-3xl: 2.25rem; }
}
```
Treat values as an initial scale, not immutable final styling. Change tokens centrally rather than adding component-specific media-query overrides. Prefer incremental fixed steps at deliberate breakpoints for typography; use `min()`, `max()`, `clamp()`, `%`, and flexible layout units for container behavior where appropriate. Avoid viewport-driven text sizes that become unexpectedly small or large.

## Responsive layout and navigation
- Mobile-first: support narrow screens starting around 320px without horizontal scrolling.
- Mobile: compact top bar, persistent bottom navigation where appropriate, single-column feed, full-width content with comfortable gutters, safe-area padding.
- Tablet: adaptive gutters and navigation; do not stretch the feed indefinitely.
- Desktop: persistent sidebar navigation and a centered, constrained feed; use available space for optional secondary content only when valuable.
- Prefer responsive grid/flexbox and container constraints over fixed positioning or arbitrary pixel widths.
- Preserve image aspect ratios and avoid layout shifts by reserving media space.
- Test at approximately 320, 375, 768, 1024, and 1440px, plus intermediate widths.

## Components and reuse
Create shared primitives when a pattern is reused or has substantial behavior: Button, IconButton, Input, Textarea, Avatar, Modal/Dialog, Toast, Spinner, Skeleton, EmptyState, ErrorMessage, and navigation items. Create feature components such as PostCard, PostComposer, CommentList, CommentForm, ProfileHeader, FollowButton, SearchResults, and ImageUploader. Avoid abstracting a component before its reuse or behavior is clear. Keep page components focused on composition; keep API/state logic in feature hooks or modules when complexity warrants it.

## Interactive behavior
- Every clickable control must have an observable response. Use subtle hover, active/pressed, focus-visible, disabled, and selected treatments.
- Buttons should feel responsive through short transitions and restrained transforms; no exaggerated motion that shifts surrounding layout.
- Dialogs and menus must manage focus, Escape dismissal, and accessible labels.
- Sliders only where a genuine continuous or stepped value is being adjusted; do not add them decoratively.
- Respect `prefers-reduced-motion: reduce` and avoid animation that blocks interaction.
- Use optimistic updates selectively (e.g., likes/follows), with rollback and visible error feedback on failure.

## Component state contracts
For each meaningful asynchronous UI, define applicable states and their actual behavior:
- `idle`: default usable interface with clear affordances.
- `loading`: progress indication, duplicate-submit prevention where needed, and stable layout; use skeletons for content loads and inline progress for actions.
- `success`: show completed state, update relevant UI/data, and provide concise confirmation only when useful.
- `error`: accessible error text, recovery/retry action, preserved user input where appropriate, and rollback of optimistic state if needed.

Also handle empty, disabled, unauthenticated, and permission-denied states where applicable. Not every presentational component needs all states. Prefer explicit finite status values over contradictory boolean flags; make state ownership clear and avoid duplicating derived state. Do not leave success/error feedback as a purely visual mock: wire it to real action results.

Examples:
- PostComposer: idle draft -> uploading/submitting -> posted/cleared; on failure preserve caption and selected image and allow retry.
- LikeButton: idle/liked -> pending -> updated; on failure restore previous count and selection.
- SearchResults: idle prompt -> loading -> results/empty; on failure show retry.
- ImageUploader: idle -> preview/validation -> uploading -> uploaded/error; expose file-size/type guidance.
- LoginForm: idle -> submitting -> authenticated/validation or server error.

## Key screens
1. Global feed: newest-first posts, post image, author, caption, like/comment controls, loading/empty/error handling.
2. Authentication: registration/login with clear validation and feedback.
3. Create post: one image, optional caption, preview, upload progress or pending state, failure recovery.
4. Public profile: avatar, bio, stats, follow action, post grid, editing for owner, followers/following lists.
5. Search: user and caption-based post search, distinguish result types, empty and error states.
6. Post detail: image, caption, comments, and author-owned editing/deletion actions.
7. Admin: basic user/post management with clear destructive-action confirmation; authorization behavior follows the security lab specification.

## Accessibility and performance
- Keyboard-operable interactions, logical tab order, visible focus states, accessible names, meaningful alt text or decorative alt handling, and live announcements for async status when useful.
- Aim for WCAG AA contrast for normal text and interactive controls.
- Touch targets approximately 44x44px or larger where feasible.
- Optimize images with appropriate dimensions and responsive sizing; avoid unnecessary animation libraries and heavyweight component dependencies.
- Prevent content jumps with reserved image dimensions, stable skeletons, and consistent button widths during loading.

## Acceptance and review checklist
Before calling a screen complete, verify:
- It follows Impeccable guidance (or records why unavailable).
- It works on mobile and desktop, including intermediate viewport sizes.
- It uses global design tokens and shared patterns rather than scattered magic numbers.
- Relevant idle/loading/success/error/empty states are functional and adjustable per use case.
- Buttons, forms, menus, and navigation are keyboard- and touch-friendly.
- Images preserve aspect ratio; loading does not cause excessive layout shift.
- Motion feels responsive and respects reduced-motion settings.
- No unapproved vulnerability was added; approved vulnerabilities are not silently patched by UI changes.

## Scope boundaries
This file specifies appearance, interaction, responsive behavior, and frontend UI state contracts. `docs/PRODUCT.md` owns feature requirements, `docs/ARCHITECTURE.md` owns system design, and `docs/VULNERABILITIES.md` owns intentional vulnerability selection, placement, exploit verification, and isolation.
