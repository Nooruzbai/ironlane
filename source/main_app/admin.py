from django.contrib import admin

from main_app.models import DriverApplication, QuoteRequest


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "company",
        "origin",
        "destination",
        "freight_type",
        "pickup_date",
        "is_handled",
        "created_at",
    )
    list_filter = ("is_handled", "freight_type", "created_at")
    list_editable = ("is_handled",)
    search_fields = ("full_name", "company", "email", "origin", "destination")
    readonly_fields = ("created_at",)


@admin.register(DriverApplication)
class DriverApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "license_class", "years_experience", "is_reviewed", "created_at")
    list_filter = ("is_reviewed", "license_class")
    list_editable = ("is_reviewed",)
    search_fields = ("full_name", "email", "phone")
    readonly_fields = ("created_at",)
