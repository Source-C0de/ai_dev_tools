"""Root URL configuration for ties_project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("crm.urls", namespace="crm")),
]
