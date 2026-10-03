from django.db import models
from django.utils.translation import gettext_lazy as _


class FreightType(models.TextChoices):
    FULL_TRUCKLOAD = "ftl", _("Full Truckload (FTL)")
    LESS_THAN_TRUCKLOAD = "ltl", _("Less Than Truckload (LTL)")
    REFRIGERATED = "reefer", _("Refrigerated (Reefer)")
    FLATBED = "flatbed", _("Flatbed / Oversized")
    DEDICATED = "dedicated", _("Dedicated Fleet")
    OTHER = "other", _("Other")


class LicenseClass(models.TextChoices):
    CLASS_A = "cdl_a", _("CDL Class A")
    CLASS_B = "cdl_b", _("CDL Class B")


class QuoteRequest(models.Model):
    full_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    freight_type = models.CharField(max_length=20, choices=FreightType)
    weight_kg = models.PositiveIntegerField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    is_handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name}: {self.origin} -> {self.destination}"


class DriverApplication(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    license_class = models.CharField(max_length=10, choices=LicenseClass)
    years_experience = models.PositiveSmallIntegerField()
    message = models.TextField(blank=True)
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_license_class_display()})"
