# Ties — Graph Model

> **Role:** Software Engineer (data design)

## Nodes

| Node | Key fields |
|---|---|
| **Person** | `name` (required), `email`, `phone`, `notes`, `created_at` |
| **Company** | `name` (required), `website`, `industry`, `created_at` |
| **Tag** | `name` (required, unique case-insensitive) |
| **Interaction** | `person` (FK), `company` (FK, nullable), `date`, `channel`, `notes` |

## Edges

| Edge | Type | Carries |
|---|---|---|
| **Person ↔ Company** | M2M via `Membership` (through-model) | `role` (e.g., "CEO"), `started_on` |
| **Person ↔ Tag** | M2M | — |
| **Person → Interaction** | FK | `date`, `channel`, `notes` |
| **Company → Interaction** | FK (nullable) | same interaction row |

## ASCII Diagram

```
   ┌───────┐         ┌───────────┐
   │  Tag  │◄────M2M─┤  Person   │
   └───────┘         │           │
                     │  name     │
                     │  email    │
                     │  phone    │
                     └─────┬─────┘
                           │FK
              M2M via Membership
              (role, started_on)
                           │
                     ┌─────▼─────┐         ┌──────────────┐
                     │  Company  │◄──FK────┤ Interaction  │
                     │           │ (null)  │              │
                     │  name     │         │  date        │
                     │  industry │         │  channel     │
                     └───────────┘         │  notes       │
                                           └──────────────┘
```

## Example Graph Traversal Queries (the "graph engineering" core)

### Q1 — People tagged `investor`
```python
Person.objects.filter(tags__name__iexact="investor").distinct()
```
**Graph path:** `Person → (Person↔Tag M2M) → Tag`

### Q2 — People who are members of any company in industry `AI`
```python
Person.objects.filter(memberships__company__industry__iexact="AI").distinct()
```
**Graph path:** `Person → Membership → Company → (filter on industry)`

### Q3 — People touched in the last 30 days
```python
from datetime import timedelta
from django.utils import timezone
cutoff = timezone.now().date() - timedelta(days=30)
Person.objects.filter(interactions__date__gte=cutoff).distinct()
```
**Graph path:** `Person → Interaction → (filter on date)`

### Q4 — People connected to Company X via any interaction in 2026
```python
Person.objects.filter(
    interactions__company=company_x,
    interactions__date__year=2026,
).distinct()
```
**Graph path:** `Person → Interaction → Company` (two-step traversal)

### Q5 — Recent interactions for a person (graph "neighborhood")
```python
person.interactions.select_related("company").order_by("-date")[:5]
```
**Graph path:** `Person → Interaction → Company` (one-step neighborhood)

## Why this is "graph engineering"

The data isn't just tables — it's a graph where:
- A `Person` is a **node** reachable from many directions (tags, companies, interactions).
- `Membership` is an **edge with attributes** (role, started_on).
- The "recent" feature is a **graph neighborhood query** (all edges from a node within a time window).
- Search is a **graph traversal** (tag → person → company), not a flat text search.

This makes the model future-proof for richer queries (e.g., "introduce me to anyone connected to Alice within 2 hops") without restructuring.
