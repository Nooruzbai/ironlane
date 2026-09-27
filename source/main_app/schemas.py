"""
Pydantic schemas that validate everything submitted through the public forms.

Views pass `request.POST` in, and get back either a typed object or a
`{field: message}` dict that the templates render next to each input.
"""

from datetime import date
from enum import StrEnum
from typing import Annotated, Self

from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
Phone = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=6, max_length=25, pattern=r"^\+?[\d\s\-()]+$"
    ),
]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=3000)]


class FreightType(StrEnum):
    FULL_TRUCKLOAD = "ftl"
    LESS_THAN_TRUCKLOAD = "ltl"
    REFRIGERATED = "reefer"
    FLATBED = "flatbed"
    DEDICATED = "dedicated"
    OTHER = "other"


FREIGHT_TYPE_LABELS: dict[FreightType, str] = {
    FreightType.FULL_TRUCKLOAD: _("Full Truckload (FTL)"),
    FreightType.LESS_THAN_TRUCKLOAD: _("Less Than Truckload (LTL)"),
    FreightType.REFRIGERATED: _("Refrigerated (Reefer)"),
    FreightType.FLATBED: _("Flatbed / Oversized"),
    FreightType.DEDICATED: _("Dedicated Fleet"),
    FreightType.OTHER: _("Other"),
}


class LicenseClass(StrEnum):
    CLASS_A = "cdl_a"
    CLASS_B = "cdl_b"


LICENSE_CLASS_LABELS: dict[LicenseClass, str] = {
    LicenseClass.CLASS_A: _("CDL Class A"),
    LicenseClass.CLASS_B: _("CDL Class B"),
}


class FormSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore", frozen=True)

    # Honeypot: hidden from humans with CSS, bots tend to fill it in.
    website: str = ""

    @classmethod
    def from_post(cls, data) -> tuple[Self | None, dict[str, str]]:
        """Validate a QueryDict. Returns (instance, {}) or (None, errors)."""
        raw = {key: data.get(key) for key in cls.model_fields if data.get(key) not in (None, "")}
        try:
            return cls.model_validate(raw), {}
        except ValidationError as exc:
            return None, _flatten_errors(exc)


class QuoteRequestSchema(FormSchema):
    full_name: ShortText
    company: Annotated[str, StringConstraints(strip_whitespace=True, max_length=120)] = ""
    email: EmailStr
    phone: Phone
    origin: ShortText
    destination: ShortText
    freight_type: FreightType
    weight_kg: Annotated[int, Field(gt=0, le=40_000)] | None = None
    pickup_date: date | None = None
    message: LongText = ""

    @field_validator("pickup_date")
    @classmethod
    def _pickup_not_in_past(cls, value: date | None) -> date | None:
        if value is not None and value < date.today():
            raise ValueError(gettext("Pickup date cannot be in the past"))
        return value

    @model_validator(mode="after")
    def _origin_differs_from_destination(self) -> Self:
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError(gettext("Origin and destination must be different"))
        return self


class DriverApplicationSchema(FormSchema):
    full_name: ShortText
    email: EmailStr
    phone: Phone
    license_class: LicenseClass
    years_experience: Annotated[int, Field(ge=0, le=60)]
    message: LongText = ""


FRIENDLY_MESSAGES = {
    "missing": _("This field is required"),
    "string_too_short": _("This value is too short"),
    "string_too_long": _("This value is too long"),
    "string_pattern_mismatch": _("Please enter a valid phone number"),
    "enum": _("Please choose one of the options"),
    "int_parsing": _("Please enter a whole number"),
    "date_from_datetime_parsing": _("Please enter a valid date"),
    "date_parsing": _("Please enter a valid date"),
}


def _flatten_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else "form"
        if field in errors:
            continue
        if field == "email":
            message = gettext("Please enter a valid email address")
        elif err["type"] == "value_error" and "error" in err.get("ctx", {}):
            message = str(err["ctx"]["error"])
        else:
            message = str(FRIENDLY_MESSAGES.get(err["type"], err["msg"]))
        errors[field] = message
    return errors
