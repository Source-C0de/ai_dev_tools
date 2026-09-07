"""Views for the crm app."""

from __future__ import annotations

from datetime import timedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
)

from .forms import CompanyForm, InteractionForm, MembershipForm, PersonForm
from .models import Company, Interaction, Membership, Person, Tag


class PersonListView(ListView):
    """Home page — list of all people."""

    model = Person
    template_name = "crm/person_list.html"
    context_object_name = "people"


class PersonDetailView(DetailView):
    model = Person
    template_name = "crm/person_detail.html"
    context_object_name = "person"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["memberships"] = self.object.memberships.select_related("company")
        ctx["recent_interactions"] = self.object.interactions.select_related("company")[:5]
        return ctx


class PersonCreateView(CreateView):
    model = Person
    form_class = PersonForm
    template_name = "crm/person_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url() if self.object else reverse("crm:person_list")


class CompanyListView(ListView):
    model = Company
    template_name = "crm/company_list.html"
    context_object_name = "companies"


class CompanyDetailView(DetailView):
    model = Company
    template_name = "crm/company_detail.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["memberships"] = self.object.memberships.select_related("person")
        return ctx


class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "crm/company_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url() if self.object else reverse("crm:company_list")


class MembershipCreateView(CreateView):
    """Link a person to a company with a role."""

    model = Membership
    form_class = MembershipForm
    template_name = "crm/membership_form.html"

    def _person_from_query(self) -> Person | None:
        person_id = self.request.GET.get("person")
        if person_id:
            return get_object_or_404(Person, pk=person_id)
        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["person"] = self._person_from_query()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        person = self._person_from_query()
        if person is not None:
            ctx["person"] = person
        return ctx

    def get_success_url(self):
        person_id = self.request.GET.get("person")
        if person_id:
            return reverse("crm:person_detail", args=[person_id])
        return reverse("crm:person_list")


class InteractionCreateView(CreateView):
    """Log an interaction with a person (and optionally a company)."""

    model = Interaction
    form_class = InteractionForm
    template_name = "crm/interaction_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["date"] = timezone.now().date()
        person_id = self.request.GET.get("person")
        if person_id:
            initial["person"] = person_id
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        person_id = self.request.GET.get("person")
        if person_id:
            kwargs["person"] = get_object_or_404(Person, pk=person_id)
        return kwargs

    def get_success_url(self):
        return reverse("crm:person_detail", args=[self.object.person_id])


def search(request):
    """Graph traversal search — ?tag=, ?company=, ?recent=<days>."""
    tag = request.GET.get("tag", "").strip()
    company_id = request.GET.get("company", "").strip()
    recent_days = request.GET.get("recent", "").strip()

    qs = Person.objects.all()
    applied = []

    if tag:
        qs = qs.filter(tags__name__iexact=tag).distinct()
        applied.append(("tag", tag))

    if company_id:
        qs = qs.filter(memberships__company_id=company_id).distinct()
        applied.append(("company", company_id))

    if recent_days.isdigit():
        days = int(recent_days)
        cutoff = timezone.now().date() - timedelta(days=days)
        qs = qs.filter(interactions__date__gte=cutoff).distinct()
        applied.append(("recent", f"{days} days"))

    return render(
        request,
        "crm/search.html",
        {
            "people": qs,
            "applied": applied,
            "all_tags": Tag.objects.all(),
            "all_companies": Company.objects.all(),
        },
    )
