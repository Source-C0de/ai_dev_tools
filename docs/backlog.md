# Backlog

> **Roles:** Software Engineer (owns build) + Product Manager (owns priority)
> **Status legend:** `Todo` → `Doing` → `Done` | `Blocked` (with reason)

| # | Task | Owner | Loop | Status | Notes |
|---|------|-------|------|--------|-------|
| 1 | Create `Person`, `Company`, `Tag`, `Interaction`, `Membership` models with M2M relationships | SE | Loop 1 | **Done** | Loop 1 — see `crm/models.py` |
| 2 | Write graph + model unit tests | QA + SE | Loop 1 | **Done** | `crm/tests/test_models.py` |
| 3 | Register `crm` in `INSTALLED_APPS` | SE | Loop 1 | **Done** | `ties_project/settings.py` |
| 4 | Build `PersonForm`, `PersonListView`, `PersonDetailView`, `PersonCreateView` + templates | SE | Loop 2 | **Done** | Loop 2 |
| 5 | Build `CompanyForm`, `CompanyListView`, `CompanyDetailView`, `CompanyCreateView` + templates | SE | Loop 2 | **Done** | Loop 2 |
| 6 | Build `MembershipCreateView` so a person can be linked to a company with a role | SE | Loop 2 | **Done** | Loop 2 |
| 7 | HTTP/view tests for Person + Company CRUD | QA | Loop 2 | **Done** | `crm/tests/test_views.py` |
| 8 | Build `InteractionForm` + `InteractionCreateView` + recent-interactions list | SE | Loop 3 | **Done** | Loop 3 |
| 9 | Build `/search/` view that supports tag / company / recent filters (graph traversal) | SE | Loop 3 | **Done** | Loop 3 |
| 10 | Tests for graph traversal queries (tag, company, recent) | QA | Loop 3 | **Done** | Loop 3 |
| 11 | Build `scripts/loop.py` CLI to drive iterations | SE | Loop 4 | **Done** | Loop 4 |
| 12 | Write `README.md` with answers to `question.md` | SE | Loop 4 | **Done** | Loop 4 |
| 13 | Update `docs/context.md` with loop learnings | SE | Loop 4 | **Done** | Loop 4 |

## Task 1 detail (per `question.md`)

> "What is task 1 in your backlog.md?"

**Task 1:** Create `Person`, `Company`, `Tag`, `Interaction`, `Membership` models with M2M relationships.
