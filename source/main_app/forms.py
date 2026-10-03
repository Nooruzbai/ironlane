"""
Django forms that validate everything submitted through the public forms.

Views bind `request.POST`, then either save the form or pass `error_dict()` to the
templates, which render each message next to its input.
"""

from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from main_app.models import DriverApplication, QuoteRequest

REQUIRED = {"required": _("This field is required")}
TEXT_ERRORS = {
    **REQUIRED,
    "min_length": _("This value is too short"),
    "max_length": _("This value is too long"),
}
CHOICE_ERRORS = {**REQUIRED, "invalid_choice": _("Please choose one of the options")}
NUMBER_ERRORS = {**REQUIRED, "invalid": _("Please enter a whole number")}


def short_text(required: bool = True, min_length: int | None = 2) -> forms.CharField:
    return forms.CharField(
        required=required, min_length=min_length, max_length=120, error_messages=TEXT_ERRORS
    )


def email_field() -> forms.EmailField:
    return forms.EmailField(
        error_messages={**REQUIRED, "invalid": _("Please enter a valid email address")}
    )


def phone_field() -> forms.CharField:
    return forms.CharField(
        min_length=6,
        max_length=25,
        validators=[RegexValidator(r"^\+?[\d\s\-()]+$", _("Please enter a valid phone number"))],
        error_messages=TEXT_ERRORS,
    )


def message_field() -> forms.CharField:
    return forms.CharField(
        required=False, max_length=3000, widget=forms.Textarea, error_messages=TEXT_ERRORS
    )


class PublicForm(forms.ModelForm):
    # Honeypot: hidden from humans with CSS, bots tend to fill it in.
    website = forms.CharField(required=False)

    @property
    def is_spam(self) -> bool:
        return bool(self.cleaned_data.get("website"))

    def error_dict(self) -> dict[str, str]:
        """First error per field, as `{field: message}` for the templates."""
        return {field: str(errors[0]) for field, errors in self.errors.items()}


class QuoteRequestForm(PublicForm):
    full_name = short_text()
    company = short_text(required=False, min_length=None)
    email = email_field()
    phone = phone_field()
    origin = short_text()
    destination = short_text()
    weight_kg = forms.IntegerField(
        required=False, min_value=1, max_value=40_000, error_messages=NUMBER_ERRORS
    )
    pickup_date = forms.DateField(
        required=False, error_messages={"invalid": _("Please enter a valid date")}
    )
    message = message_field()

    class Meta:
        model = QuoteRequest
        fields = [
            "full_name",
            "company",
            "email",
            "phone",
            "origin",
            "destination",
            "freight_type",
            "weight_kg",
            "pickup_date",
            "message",
        ]
        error_messages = {"freight_type": CHOICE_ERRORS}

    def clean_pickup_date(self):
        value = self.cleaned_data["pickup_date"]
        if value is not None and value < timezone.localdate():
            raise forms.ValidationError(_("Pickup date cannot be in the past"))
        return value

    def clean(self):
        cleaned = super().clean()
        origin, destination = cleaned.get("origin"), cleaned.get("destination")
        if origin and destination and origin.casefold() == destination.casefold():
            self.add_error("destination", _("Origin and destination must be different"))
        return cleaned


class DriverApplicationForm(PublicForm):
    full_name = short_text()
    email = email_field()
    phone = phone_field()
    years_experience = forms.IntegerField(min_value=0, max_value=60, error_messages=NUMBER_ERRORS)
    message = message_field()

    class Meta:
        model = DriverApplication
        fields = ["full_name", "email", "phone", "license_class", "years_experience", "message"]
        error_messages = {"license_class": CHOICE_ERRORS}
