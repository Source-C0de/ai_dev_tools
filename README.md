# Ties — a personal CRM

A small Django + Python app demonstrating five engineering concepts:

1. **Spec-driven development** — `docs/spec.md` is the source of truth.
2. **Context engineering** — `docs/context.md` is the rolling engineering journal.
3. **PM / SE / QA roles** — `docs/spec.md` (PM), `docs/backlog.md` (SE + PM), `docs/qa_checklist.md` (QA).
4. **Loop engineering** — `scripts/loop.py` drives the spec → build → test → learn loop.
5. **Graph engineering** — `docs/graph.md` + `crm/models.py` model people, companies, and interactions as a graph.

## Features

The spec settled on **4 features**:

1. **Add a Person** — name, email, phone, notes, and comma-separated tags.
2. **Add a Company** — name, website, industry; link to people via memberships.
3. **Log an Interaction** — a meeting/call/email between you, a person, and optionally a company.
4. **Search & Filter** — find people by tag, company, or "touched in the last N days" (graph traversal).

## Quick start

```bash
uv sync                                    # install deps
uv run python manage.py migrate            # create SQLite schema
uv run python manage.py runserver          # dev server at http://localhost:8000
```

Then visit:

- `/` — list of people
- `/people/new/` — add a person
- `/companies/` — list of companies
- `/companies/new/` — add a company
- `/search/` — filter by tag / company / recent
- `/admin/` — Django admin

## Tests

```bash
uv run pytest
```

## Loop script

```bash
uv run python scripts/loop.py            # show next Doing task + run tests
uv run python scripts/loop.py --status   # backlog status summary
uv run python scripts/loop.py --complete # mark Doing task as Done
```

## Project structure

```
ties_project/        Django project config (settings.py, urls.py)
crm/                 Django app — models, views, forms, templates, tests
docs/
  spec.md            PM: feature spec with acceptance criteria
  context.md         All: rolling engineering journal
  backlog.md         SE + PM: ordered task list with status
  qa_checklist.md    QA: manual + automated test pass-down
  graph.md           SE: graph data model + traversal queries
scripts/
  loop.py            Loop engineering driver
```

## Answers to `question.md`

1. **Which coding agent did you use?**
   **puku-cli**

2. **What are the 2-4 features your spec settled on?**
   **Add a Person, Add a Company, Log an Interaction, Search & Filter.**

3. **Which file do you edit to include your app in the Django project?**
   **`settings.py`** — add the app name to `INSTALLED_APPS`.

4. **What is task 1 in your backlog.md?**
   **"Create `Person`, `Company`, `Tag`, `Interaction`, `Membership` models with M2M relationships."**

5. **Which command starts the Django development server?**
   **`uv run python manage.py runserver`**

6. **Which command runs the tests in the terminal?**
   **`pytest`** (run via `uv run pytest` in this project)
