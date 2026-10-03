import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import override

from main_app.models import DriverApplication, QuoteRequest

logger = logging.getLogger(__name__)


def _send(subject: str, lines: list[tuple[str, object]], body: str, reply_to: str) -> bool:
    details = "\n".join(f"{label:<14}{value or '-'}" for label, value in lines)
    text = f"{details}\n\n{body or '(no message)'}\n\n-- Sent from the IronLane Freight website"
    # Visitors control parts of the subject; header values must not contain line breaks
    subject = " ".join(subject.split())
    try:
        EmailMessage(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.INBOX_EMAIL],
            reply_to=[reply_to],
        ).send(fail_silently=False)
    except Exception:
        # The submission is already saved in the database, so a mail outage loses nothing.
        logger.exception("Failed to send notification email: %s", subject)
        return False
    return True


def notify_quote_request(quote: QuoteRequest) -> bool:
    # The office inbox reads English, whatever language the visitor browsed in.
    with override("en"):
        return _send(
            subject=f"New quote request: {quote.origin} -> {quote.destination}",
            lines=[
                ("Name:", quote.full_name),
                ("Company:", quote.company),
                ("Email:", quote.email),
                ("Phone:", quote.phone),
                ("Freight:", quote.get_freight_type_display()),
                ("Origin:", quote.origin),
                ("Destination:", quote.destination),
                ("Weight (kg):", quote.weight_kg),
                ("Pickup date:", quote.pickup_date),
            ],
            body=quote.message,
            reply_to=quote.email,
        )


def notify_driver_application(application: DriverApplication) -> bool:
    with override("en"):
        return _send(
            subject=f"New driver application: {application.full_name}",
            lines=[
                ("Name:", application.full_name),
                ("Email:", application.email),
                ("Phone:", application.phone),
                ("License:", application.get_license_class_display()),
                ("Experience:", f"{application.years_experience} years"),
            ],
            body=application.message,
            reply_to=application.email,
        )
