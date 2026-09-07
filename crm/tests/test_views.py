"""HTTP / view tests for the crm app."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from crm.models import Company, Interaction, Membership, Person, Tag


# ---------- Person CRUD ----------


@pytest.mark.django_db
def test_person_list_renders(client):
    Person.objects.create(name="Alice")
    resp = client.get(reverse("crm:person_list"))
    assert resp.status_code == 200
    assert b"Alice" in resp.content


@pytest.mark.django_db
def test_person_create_post_persists_and_tags(client):
    resp = client.post(
        reverse("crm:person_create"),
        data={
            "name": "Alice",
            "email": "alice@example.com",
            "phone": "555-1234",
            "notes": "Met at conference",
            "tags_csv": "investor, mentor, investor",
        },
    )
    assert resp.status_code == 302  # redirect to detail
    alice = Person.objects.get(name="Alice")
    assert alice.email == "alice@example.com"
    tag_names = set(alice.tags.values_list("name", flat=True))
    # Tags are deduped case-insensitively; "investor" should appear once.
    assert tag_names == {"investor", "mentor"}


@pytest.mark.django_db
def test_person_detail_renders(client):
    alice = Person.objects.create(name="Alice", email="a@e.com")
    resp = client.get(reverse("crm:person_detail", args=[alice.pk]))
    assert resp.status_code == 200
    assert b"Alice" in resp.content
    assert b"a@e.com" in resp.content


# ---------- Company CRUD ----------


@pytest.mark.django_db
def test_company_list_and_create(client):
    resp = client.post(
        reverse("crm:company_create"),
        data={"name": "Acme", "industry": "AI", "website": "https://acme.example"},
    )
    assert resp.status_code == 302
    acme = Company.objects.get(name="Acme")
    assert acme.industry == "AI"

    listing = client.get(reverse("crm:company_list"))
    assert listing.status_code == 200
    assert b"Acme" in listing.content


@pytest.mark.django_db
def test_company_detail_lists_members(client):
    acme = Company.objects.create(name="Acme")
    alice = Person.objects.create(name="Alice")
    Membership.objects.create(person=alice, company=acme, role="CEO")
    resp = client.get(reverse("crm:company_detail", args=[acme.pk]))
    assert resp.status_code == 200
    assert b"Alice" in resp.content
    assert b"CEO" in resp.content


# ---------- Membership (link person ↔ company) ----------


@pytest.mark.django_db
def test_membership_create_links_person_to_company(client):
    alice = Person.objects.create(name="Alice")
    acme = Company.objects.create(name="Acme")
    resp = client.post(
        f"{reverse('crm:membership_create')}?person={alice.pk}",
        data={"person": alice.pk, "company": acme.pk, "role": "CEO", "started_on": "2026-01-01"},
    )
    assert resp.status_code == 302
    alice.refresh_from_db()
    assert list(alice.memberships.values_list("company", flat=True)) == [acme.pk]
    assert alice.memberships.first().role == "CEO"


# ---------- Interaction CRUD ----------


@pytest.mark.django_db
def test_interaction_create_persists_and_redirects_to_person(client):
    alice = Person.objects.create(name="Alice")
    today = timezone.now().date()
    resp = client.post(
        reverse("crm:interaction_create"),
        data={
            "person": alice.pk,
            "company": "",
            "date": today.isoformat(),
            "channel": "meeting",
            "notes": "Lunch meeting",
        },
    )
    assert resp.status_code == 302
    assert Interaction.objects.filter(person=alice, channel="meeting").exists()


# ---------- Search / graph traversal ----------


@pytest.mark.django_db
def test_search_by_tag(client):
    investor = Tag.objects.create(name="investor")
    mentor = Tag.objects.create(name="mentor")
    alice = Person.objects.create(name="Alice")
    alice.tags.add(investor)
    bob = Person.objects.create(name="Bob")
    bob.tags.add(mentor)

    resp = client.get(reverse("crm:search") + "?tag=investor")
    assert resp.status_code == 200
    assert b"Alice" in resp.content
    assert b"Bob" not in resp.content


@pytest.mark.django_db
def test_search_by_company(client):
    acme = Company.objects.create(name="Acme")
    globex = Company.objects.create(name="Globex")
    alice = Person.objects.create(name="Alice")
    bob = Person.objects.create(name="Bob")
    Membership.objects.create(person=alice, company=acme)
    Membership.objects.create(person=bob, company=globex)

    resp = client.get(f"{reverse('crm:search')}?company={acme.pk}")
    assert resp.status_code == 200
    assert b"Alice" in resp.content
    assert b"Bob" not in resp.content


@pytest.mark.django_db
def test_search_recent_days(client):
    alice = Person.objects.create(name="Alice")
    bob = Person.objects.create(name="Bob")
    today = timezone.now().date()
    Interaction.objects.create(person=alice, date=today - timedelta(days=5))
    Interaction.objects.create(person=bob, date=today - timedelta(days=200))

    resp = client.get(reverse("crm:search") + "?recent=30")
    assert resp.status_code == 200
    assert b"Alice" in resp.content
    assert b"Bob" not in resp.content


@pytest.mark.django_db
def test_search_combined_filters_and(client):
    """tag=investor AND company=Acme — both must match."""
    investor = Tag.objects.create(name="investor")
    mentor = Tag.objects.create(name="mentor")
    acme = Company.objects.create(name="Acme")
    alice = Person.objects.create(name="Alice")
    alice.tags.add(investor)
    Membership.objects.create(person=alice, company=acme)
    bob = Person.objects.create(name="Bob")
    bob.tags.add(mentor)
    Membership.objects.create(person=bob, company=acme)

    resp = client.get(f"{reverse('crm:search')}?tag=investor&company={acme.pk}")
    assert b"Alice" in resp.content
    assert b"Bob" not in resp.content
