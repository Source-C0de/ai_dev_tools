"""URL routes for the crm app."""

from django.urls import path

from . import views

app_name = "crm"

urlpatterns = [
    # People
    path("", views.PersonListView.as_view(), name="person_list"),
    path("people/new/", views.PersonCreateView.as_view(), name="person_create"),
    path("people/<int:pk>/", views.PersonDetailView.as_view(), name="person_detail"),

    # Companies
    path("companies/", views.CompanyListView.as_view(), name="company_list"),
    path("companies/new/", views.CompanyCreateView.as_view(), name="company_create"),
    path("companies/<int:pk>/", views.CompanyDetailView.as_view(), name="company_detail"),

    # Memberships (link person ↔ company)
    path("memberships/new/", views.MembershipCreateView.as_view(), name="membership_create"),

    # Interactions (touchpoints)
    path("interactions/new/", views.InteractionCreateView.as_view(), name="interaction_create"),

    # Search (graph traversal)
    path("search/", views.search, name="search"),
]
