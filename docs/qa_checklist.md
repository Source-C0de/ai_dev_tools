# QA Checklist

> **Role:** QA Engineer

## Automated tests (must pass)

- [ ] `Person` is created with just a name (other fields optional)
- [ ] `Person` can have multiple `Tag`s; tags are case-insensitive on dedupe
- [ ] `Company` is created with just a name
- [ ] `Membership` carries `role` and `started_on`
- [ ] `Interaction` requires a `person`; `company` is optional
- [ ] Person list view renders 200
- [ ] Person detail view shows tags, memberships, recent interactions
- [ ] Company list / detail views render 200
- [ ] `/search/?tag=investor` returns tagged people only
- [ ] `/search/?company=<id>` returns members of that company only
- [ ] `/search/?recent=30` returns people touched in last 30 days

## Manual smoke tests

- [ ] `uv run python manage.py runserver` boots cleanly on :8000
- [ ] Home page (`/`) loads and shows empty state
- [ ] Add a person with tag `investor` → appears on `/`
- [ ] Add a company → appears on `/companies/`
- [ ] Link the person to the company via membership → detail page shows it
- [ ] Log an interaction → appears on person's detail page
- [ ] Visit `/search/?tag=investor` → person appears

## Regression risk areas

- Tag input parsing (comma-separated) — whitespace, empty entries, duplicates
- `Membership` uniqueness — same person + same company + same role should be rejected (or deduped)
- Time zone handling in "recent" filter — `USE_TZ = True`, so dates are timezone-aware

## Test command

```bash
uv run pytest
```
