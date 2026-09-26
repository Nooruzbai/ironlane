from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from main_app.models import DriverApplication, QuoteRequest
from main_app.notifications import notify_driver_application, notify_quote_request
from main_app.schemas import (
    FREIGHT_TYPE_LABELS,
    LICENSE_CLASS_LABELS,
    DriverApplicationSchema,
    QuoteRequestSchema,
)


class IndexView(TemplateView):
    template_name = "index.html"


class QuoteView(View):
    template_name = "quote.html"

    def render_form(self, request, values=None, errors=None, status=200):
        return render(
            request,
            self.template_name,
            {
                "values": values or {"freight_type": request.GET.get("service", "")},
                "errors": errors or {},
                "freight_types": FREIGHT_TYPE_LABELS.items(),
            },
            status=status,
        )

    def get(self, request):
        return self.render_form(request)

    def post(self, request):
        data, errors = QuoteRequestSchema.from_post(request.POST)
        if data is None:
            return self.render_form(request, request.POST, errors, status=400)
        if not data.website:
            notify_quote_request(QuoteRequest.from_schema(data))
        messages.success(
            request, "Thanks! A dispatcher will get back to you within one business hour."
        )
        return redirect("quote")


class CareersView(View):
    template_name = "careers.html"

    def render_form(self, request, values=None, errors=None, status=200):
        return render(
            request,
            self.template_name,
            {
                "values": values or {},
                "errors": errors or {},
                "license_classes": LICENSE_CLASS_LABELS.items(),
            },
            status=status,
        )

    def get(self, request):
        return self.render_form(request)

    def post(self, request):
        data, errors = DriverApplicationSchema.from_post(request.POST)
        if data is None:
            return self.render_form(request, request.POST, errors, status=400)
        if not data.website:
            notify_driver_application(DriverApplication.from_schema(data))
        messages.success(
            request, "Application received! Our recruiting team will call you shortly."
        )
        return redirect("careers")
