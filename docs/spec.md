# Ties — Product Spec

> **Role:** Product Manager
> **Status:** v0.1 (Loop 1 baseline)
> **Last updated:** 2026-09-07

## Vision

A **personal CRM** that helps a single user remember the people they meet, the companies those people belong to, and the touchpoints they have over time — without the bloat of a sales platform.

## Target User

A solo professional (founder, consultant, community organizer) who meets a lot of people and wants a low-friction way to keep relationships warm.

## Non-Goals

- Multi-user / team collaboration (this is a single-user tool).
- Email integration, calendar sync, or social scraping (out of scope for v1).
- Mobile app (responsive web is sufficient for v1).
- Sales pipeline forecasting (this is not a sales tool).

## User Stories & Acceptance Criteria

### Feature 1 — Add a Person
**As a** user, **I want to** save a contact's name, email, phone, and free-form notes **so that** I can recall who they are later.

**Acceptance:**
- A form accepts name (required), email, phone, notes (all optional except name).
- Tags can be entered as a comma-separated list (e.g., `mentor, investor`).
- After submit, the person appears on the people list at `/`.
- Visiting a person's detail page shows all their tags and any company memberships + recent interactions.

### Feature 2 — Add a Company
**As a** user, **I want to** save an organization with name, website, and industry **so that** I can group people by where they work.

**Acceptance:**
- A form accepts name (required), website, industry (optional).
- After submit, the company appears on the companies list at `/companies/`.
- A company's detail page lists all people who are members.

### Feature 3 — Log an Interaction
**As a** user, **I want to** record a meeting / call / email between me, a person, and optionally a company **so that** I can recall when I last spoke with them.

**Acceptance:**
- A form accepts person (required), company (optional), date (required, default today), channel (choices: meeting, call, email, other), notes (optional).
- After submit, the interaction shows up on the related person's detail page (most recent first).
- The interaction's date is included in the "recent" filter.

### Feature 4 — Search & Filter (graph traversal)
**As a** user, **I want to** filter the people list by tag, company, or "touched in the last 30 days" **so that** I can quickly find who to follow up with.

**Acceptance:**
- `/search/?tag=investor` returns all people tagged `investor`.
- `/search/?company=<id>` returns all members of that company.
- `/search/?recent=30` returns all people with at least one interaction in the last 30 days.
- The page renders three filter sections (tag / company / recent) with counts.

## Success Metrics

- A new user can add a person, tag them, link them to a company, and log an interaction in under 2 minutes.
- All four features are reachable from the home page in ≤ 2 clicks.

## Open Questions (to revisit)

- Should `Membership` have an end date for people who left a company? (Defer to v2.)
- Should tags be globally unique (case-insensitive) or per-person? (Decision: globally unique, case-insensitive — simpler for filtering.)
