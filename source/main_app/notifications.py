import logging
from email.utils import formataddr

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import override

from main_app.models import DriverApplication, QuoteRequest

logger = logging.getLogger(__name__)

SITE_NAME = "IT-Consulting website"


def _one_line(value: object) -> str:
    # Visitors control these values; email headers must not contain line breaks
    return " ".join(str(value).split())


def _send(
    request,
    *,
    subject: str,
    heading: str,
    sender_name: str,
    rows: list[tuple[str, object]],
    message: str,
    email: str,
    phone: str,
    admin_path: str,
    created_at,
) -> bool:
    context = {
        "heading": heading,
        "rows": [(label, value) for label, value in rows if value not in (None, "")],
        "message": message,
        "email": email,
        "phone": phone,
        "admin_url": request.build_absolute_uri(admin_path),
        "created_at": created_at,
        "site_name": SITE_NAME,
    }
    subject = _one_line(subject)
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=render_to_string("emails/notification.txt", context),
            # Gmail only sends from the signed-in account, so the visitor's name goes in the
            # display name and their address in Reply-To: hitting Reply answers them directly.
            from_email=formataddr(
                (f"{_one_line(sender_name)} via {SITE_NAME}", settings.DEFAULT_FROM_EMAIL)
            ),
            to=[settings.INBOX_EMAIL],
            reply_to=[formataddr((_one_line(sender_name), email))],
        )
        msg.attach_alternative(render_to_string("emails/notification.html", context), "text/html")
        msg.send(fail_silently=False)
    except Exception:
        # The submission is already saved in the database, so a mail outage loses nothing.
        logger.exception("Failed to send notification email: %s", subject)
        return False
    return True


def notify_quote_request(quote: QuoteRequest, request) -> bool:
    # The office inbox reads English, whatever language the visitor browsed in.
    with override("en"):
        return _send(
            request,
            subject=f"Quote request: {quote.origin} → {quote.destination} ({quote.full_name})",
            heading="New quote request",
            sender_name=quote.full_name,
            rows=[
                ("Name", quote.full_name),
                ("Company", quote.company),
                ("Email", quote.email),
                ("Phone", quote.phone),
                ("Freight", quote.get_freight_type_display()),
                ("Route", f"{quote.origin} → {quote.destination}"),
                ("Weight", f"{quote.weight_kg:,} kg" if quote.weight_kg else None),
                (
                    "Pickup date",
                    quote.pickup_date.strftime("%d %b %Y") if quote.pickup_date else None,
                ),
            ],
            message=quote.message,
            email=quote.email,
            phone=quote.phone,
            admin_path=reverse("admin:main_app_quoterequest_change", args=[quote.pk]),
            created_at=quote.created_at,
        )


def notify_driver_application(application: DriverApplication, request) -> bool:
    with override("en"):
        return _send(
            request,
            subject=f"Driver application: {application.full_name}",
            heading="New driver application",
            sender_name=application.full_name,
            rows=[
                ("Name", application.full_name),
                ("Email", application.email),
                ("Phone", application.phone),
            ],
            message=application.message,
            email=application.email,
            phone=application.phone,
            admin_path=reverse("admin:main_app_driverapplication_change", args=[application.pk]),
            created_at=application.created_at,
        )
