from django.contrib import admin

from .models import Company, Interaction, Membership, Person, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "website")
    search_fields = ("name", "industry")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email")
    filter_horizontal = ("tags",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("person", "company", "role", "started_on")
    list_filter = ("company",)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("person", "company", "date", "channel")
    list_filter = ("channel", "date")
