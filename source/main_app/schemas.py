"""
Pydantic schemas that validate everything submitted through the public forms.

Views pass `request.POST` in, and get back either a typed object or a
`{field: message}` dict that the templates render next to each input.
"""

from datetime import date
from enum import StrEnum
from typing import Annotated, Self

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
    FreightType.FULL_TRUCKLOAD: "Full Truckload (FTL)",
    FreightType.LESS_THAN_TRUCKLOAD: "Less Than Truckload (LTL)",
    FreightType.REFRIGERATED: "Refrigerated (Reefer)",
    FreightType.FLATBED: "Flatbed / Oversized",
    FreightType.DEDICATED: "Dedicated Fleet",
    FreightType.OTHER: "Other",
}


class LicenseClass(StrEnum):
    CLASS_A = "cdl_a"
    CLASS_B = "cdl_b"


LICENSE_CLASS_LABELS: dict[LicenseClass, str] = {
    LicenseClass.CLASS_A: "CDL Class A",
    LicenseClass.CLASS_B: "CDL Class B",
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
            raise ValueError("Pickup date cannot be in the past")
        return value

    @model_validator(mode="after")
    def _origin_differs_from_destination(self) -> Self:
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError("Origin and destination must be different")
        return self


class DriverApplicationSchema(FormSchema):
    full_name: ShortText
    email: EmailStr
    phone: Phone
    license_class: LicenseClass
    years_experience: Annotated[int, Field(ge=0, le=60)]
    message: LongText = ""


FRIENDLY_MESSAGES = {
    "missing": "This field is required",
    "string_too_short": "This value is too short",
    "string_too_long": "This value is too long",
    "string_pattern_mismatch": "Please enter a valid phone number",
    "enum": "Please choose one of the options",
    "int_parsing": "Please enter a whole number",
    "date_from_datetime_parsing": "Please enter a valid date",
    "date_parsing": "Please enter a valid date",
}


def _flatten_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else "form"
        if field in errors:
            continue
        if field == "email":
            message = "Please enter a valid email address"
        elif err["type"] == "value_error" and "error" in err.get("ctx", {}):
            message = str(err["ctx"]["error"])
        else:
            message = FRIENDLY_MESSAGES.get(err["type"], err["msg"])
        errors[field] = message
    return errors
