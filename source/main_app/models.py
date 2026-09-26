from django.db import models

from main_app.schemas import (
    FREIGHT_TYPE_LABELS,
    LICENSE_CLASS_LABELS,
    DriverApplicationSchema,
    QuoteRequestSchema,
)


class QuoteRequest(models.Model):
    full_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    freight_type = models.CharField(
        max_length=20, choices=[(k.value, v) for k, v in FREIGHT_TYPE_LABELS.items()]
    )
    weight_kg = models.PositiveIntegerField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    is_handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name}: {self.origin} -> {self.destination}"

    @classmethod
    def from_schema(cls, data: QuoteRequestSchema) -> "QuoteRequest":
        return cls.objects.create(**data.model_dump(exclude={"website"}))


class DriverApplication(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    license_class = models.CharField(
        max_length=10, choices=[(k.value, v) for k, v in LICENSE_CLASS_LABELS.items()]
    )
    years_experience = models.PositiveSmallIntegerField()
    message = models.TextField(blank=True)
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_license_class_display()})"

    @classmethod
    def from_schema(cls, data: DriverApplicationSchema) -> "DriverApplication":
        return cls.objects.create(**data.model_dump(exclude={"website"}))
