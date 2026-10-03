from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, View

from main_app.forms import DriverApplicationForm, QuoteRequestForm
from main_app.models import FreightType, LicenseClass
from main_app.notifications import notify_driver_application, notify_quote_request


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
                "freight_types": FreightType.choices,
            },
            status=status,
        )

    def get(self, request):
        return self.render_form(request)

    def post(self, request):
        form = QuoteRequestForm(request.POST)
        if not form.is_valid():
            return self.render_form(request, request.POST, form.error_dict(), status=400)
        if not form.is_spam:
            notify_quote_request(form.save())
        messages.success(
            request, _("Thanks! A dispatcher will get back to you within one business hour.")
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
                "license_classes": LicenseClass.choices,
            },
            status=status,
        )

    def get(self, request):
        return self.render_form(request)

    def post(self, request):
        form = DriverApplicationForm(request.POST)
        if not form.is_valid():
            return self.render_form(request, request.POST, form.error_dict(), status=400)
        if not form.is_spam:
            notify_driver_application(form.save())
        messages.success(
            request, _("Application received! Our recruiting team will call you shortly.")
        )
        return redirect("careers")
