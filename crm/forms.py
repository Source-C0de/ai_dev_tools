"""Forms for the crm app — Person, Company, Membership, Interaction."""

from __future__ import annotations

from django import forms

from .models import Company, Interaction, Membership, Person, Tag


class PersonForm(forms.ModelForm):
    """Person form with comma-separated tag input."""

    tags_csv = forms.CharField(
        required=False,
        label="Tags",
        help_text="Comma-separated, e.g. 'investor, mentor'",
    )

    class Meta:
        model = Person
        fields = ["name", "email", "phone", "notes"]

    def clean_tags_csv(self):
        raw = self.cleaned_data.get("tags_csv", "")
        # Parse, normalize, drop empties; preserve order, dedupe case-insensitively.
        seen = set()
        names = []
        for piece in raw.split(","):
            name = piece.strip()
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            names.append(name)
        return names

    def save(self, commit: bool = True):
        person = super().save(commit=commit)
        if commit:
            self._save_tags(person)
        else:
            # Defer tag saving until after the person has a PK.
            self._pending_tags = self.cleaned_data.get("tags_csv", [])
        return person

    def save_m2m(self, *args, **kwargs):
        super().save_m2m(*args, **kwargs)
        if hasattr(self, "_pending_tags"):
            self._save_tags(self.instance)

    def _save_tags(self, person: Person) -> None:
        names = self.cleaned_data.get("tags_csv", [])
        person.tags.clear()
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            person.tags.add(tag)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "website", "industry"]


class MembershipForm(forms.ModelForm):
    """Link a person to a company with a role."""

    class Meta:
        model = Membership
        fields = ["person", "company", "role", "started_on"]
        widgets = {"started_on": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, person: Person | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if person is not None:
            self.fields["person"].initial = person
            self.fields["person"].widget = forms.HiddenInput()


class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ["person", "company", "date", "channel", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, person: Person | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if person is not None:
            self.fields["person"].initial = person
            self.fields["person"].widget = forms.HiddenInput()
