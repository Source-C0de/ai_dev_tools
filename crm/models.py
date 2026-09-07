"""
Graph data model for Ties — a personal CRM.

Nodes:
    Person, Company, Tag, Interaction

Edges:
    Person ↔ Company   via Membership (through-model: role, started_on)
    Person ↔ Tag       M2M
    Person → Interaction   FK
    Company → Interaction  FK (nullable)
"""

from __future__ import annotations

from django.db import models
from django.urls import reverse


class Tag(models.Model):
    """A free-form label applied to people (e.g., 'investor', 'mentor')."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # Case-insensitive uniqueness: normalize on save.
        self.name = self.name.strip()
        super().save(*args, **kwargs)


class Company(models.Model):
    """An organization. People can be linked via Membership."""

    name = models.CharField(max_length=120, unique=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("crm:company_detail", args=[self.pk])


class Person(models.Model):
    """A contact — a node connected to tags, companies, and interactions."""

    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="people", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("crm:person_detail", args=[self.pk])

    @property
    def companies(self):
        """Distinct companies this person is a member of (graph traversal)."""
        return Company.objects.filter(memberships__person=self).distinct()


class Membership(models.Model):
    """Through-model: Person ↔ Company with role and start date."""

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="memberships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=80, blank=True, help_text="e.g., 'CEO', 'Advisor'")
    started_on = models.DateField(null=True, blank=True)

    class Meta:
        # A person can have at most one membership per company.
        constraints = [
            models.UniqueConstraint(fields=["person", "company"], name="unique_membership")
        ]
        ordering = ["company__name"]

    def __str__(self) -> str:
        role_part = f" ({self.role})" if self.role else ""
        return f"{self.person.name} @ {self.company.name}{role_part}"


class Interaction(models.Model):
    """A touchpoint (meeting, call, email, other) with a person."""

    class Channel(models.TextChoices):
        MEETING = "meeting", "Meeting"
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        OTHER = "other", "Other"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="interactions")
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        related_name="interactions",
        null=True,
        blank=True,
    )
    date = models.DateField()
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.MEETING,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.person.name} — {self.channel} on {self.date}"
