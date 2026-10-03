from datetime import date, timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from main_app.forms import QuoteRequestForm
from main_app.models import DriverApplication, QuoteRequest

VALID_QUOTE = {
    "full_name": "Jane Shipper",
    "company": "Acme Goods",
    "email": "jane@acme-goods.com",
    "phone": "+1 555 010 2000",
    "origin": "Dallas, TX",
    "destination": "Atlanta, GA",
    "freight_type": "reefer",
    "weight_kg": "18000",
    "pickup_date": (date.today() + timedelta(days=3)).isoformat(),
    "message": "Keep at 2C",
}


class QuoteRequestFormTests(TestCase):
    def test_valid_data(self):
        form = QuoteRequestForm(VALID_QUOTE)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["weight_kg"], 18000)

    def test_empty_optional_fields_are_ignored(self):
        form = QuoteRequestForm({**VALID_QUOTE, "weight_kg": "", "pickup_date": ""})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["weight_kg"])

    def test_field_errors(self):
        form = QuoteRequestForm(
            {**VALID_QUOTE, "email": "nope", "freight_type": "rocket", "full_name": ""}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.error_dict()), {"email", "freight_type", "full_name"})

    def test_past_pickup_date_rejected(self):
        past = (date.today() - timedelta(days=1)).isoformat()
        form = QuoteRequestForm({**VALID_QUOTE, "pickup_date": past})
        self.assertIn("pickup_date", form.error_dict())

    def test_same_origin_and_destination_rejected(self):
        form = QuoteRequestForm({**VALID_QUOTE, "destination": "dallas, tx"})
        self.assertIn("destination", form.error_dict())


class PageTests(TestCase):
    def test_pages_render(self):
        for name in ("index", "quote", "careers"):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_robots_and_sitemap(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)


class QuoteViewTests(TestCase):
    def test_valid_submission_saves_and_emails(self):
        response = self.client.post(reverse("quote"), VALID_QUOTE)
        self.assertRedirects(response, reverse("quote"))
        self.assertEqual(QuoteRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.reply_to, ["Jane Shipper <jane@acme-goods.com>"])
        self.assertIn("Jane Shipper via", sent.from_email)
        self.assertIn("Dallas, TX", sent.alternatives[0].content)

    def test_invalid_submission_shows_errors(self):
        response = self.client.post(reverse("quote"), {**VALID_QUOTE, "email": "bad"})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "valid email address", status_code=400)
        self.assertEqual(QuoteRequest.objects.count(), 0)

    def test_honeypot_submission_is_dropped(self):
        response = self.client.post(reverse("quote"), {**VALID_QUOTE, "website": "spam.test"})
        self.assertRedirects(response, reverse("quote"))
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)


class CareersViewTests(TestCase):
    def test_valid_application(self):
        response = self.client.post(
            reverse("careers"),
            {
                "full_name": "Sam Driver",
                "email": "sam@gmail.com",
                "phone": "555-010-3000",
            },
        )
        self.assertRedirects(response, reverse("careers"))
        self.assertEqual(DriverApplication.objects.get().phone, "555-010-3000")
