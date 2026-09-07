# Context Log

> **Role:** All (rolling engineering journal — decisions, constraints, learnings)

This document is the "context engineering" artifact for the Ties project.
Append a new section after every loop iteration.

---

## Loop 1 — Skeleton & Graph

### Decisions
- **App name:** `crm` (short, common).
- **Project name:** `ties_project` (Ties = "what connects you to people").
- **Graph model:** `Person ↔ Company` via through-model `Membership` (carries `role`, `started_on`). Plain M2M would lose this metadata.
- **Tag uniqueness:** globally unique case-insensitive (decision recorded in `spec.md` Open Questions — resolved).
- **Interaction.Company is nullable:** so a user can log a personal call/email without a company context.

### Constraints discovered
- Django 6.1 is current (newer than 5.x). M2M through-models and `select_related` behave the same.
- `uv` creates `.venv/` automatically — no need to `python -m venv` first.

### Open questions resolved
- Q: Should tags be globally unique or per-person? **A:** Globally unique case-insensitive (decided during model design).

### Learnings
- Writing the graph model on paper first (`graph.md`) made the M2M decisions obvious — would recommend for any non-trivial data model.

---

## Loop 2 — Person & Company CRUD

### Decisions
- Forms use `forms.ModelForm` rather than hand-rolled HTML to stay DRY.
- Tags input: comma-separated string parsed in the form's `clean_tags` (avoids JS dependency).
- URL structure: `/` → people list, `/people/<id>/` → detail, `/people/new/` → create.
  Same shape for companies (`/companies/`, `/companies/<id>/`, `/companies/new/`).

### Constraints discovered
- Django's `CreateView` with `model = Person` infers the form fields — but we override `form_class` to use `PersonForm` so we can add tag parsing.
- M2M tags must be saved **after** the Person is saved (`form.save_m2m()`) since the through table requires the parent PK.

### Learnings
- For a single-user CRM, generic class-based views are sufficient — no need for DRF or formsets yet.

---

## Loop 3 — Interactions & Search

### Decisions
- `/search/` is a single view that parses `?tag=`, `?company=`, `?recent=` query params and applies them as filters. If multiple are given, they AND together.
- Recent default window: 30 days (matches the spec).
- Interaction's `channel` uses Django's `choices` with a TextChoices enum for type safety.

### Constraints discovered
- `select_related("company")` on interaction lists avoids an N+1 query when rendering a feed.

### Learnings
- Graph traversal queries stay readable when each filter is named (tag / company / recent) instead of chained blindly.

---

## Loop 4 — Loop script & polish

### Decisions
- `scripts/loop.py` prints the next "Doing" item from `backlog.md` and runs the test suite — a visible reminder of the spec → build → test → learn loop.
- README.md answers all 6 questions from `question.md` so the homework is self-contained.
- Added `testserver` to `ALLOWED_HOSTS` (Django refuses unknown `Host:` headers — surfaced when using the in-process test client).
- Removed the empty `crm/tests.py` (created by `startapp`); the package `crm/tests/` is what pytest picks up.

### Final state
- 25 tests passing (`uv run pytest`)
- `manage.py check` → no issues
- End-to-end smoke test (in-process) verifies create flows + search by tag / company / recent
- Dev server (`uv run python manage.py runserver`) boots cleanly per `manage.py check`

### Learnings
- Even on a small project, writing the loop script forces you to commit each iteration explicitly — much harder to skip steps accidentally.
- Comma-separated tag parsing on save is more robust than a JS multi-select for a single-user tool — no front-end dep needed.
- Graph traversal queries compose cleanly with `.distinct()` when joining M2M; without it you get duplicates from the join.
