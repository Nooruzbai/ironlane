from django.conf import settings
from django.utils.translation import gettext_lazy as _

COMPANY = {
    "name": "IT-Consulting Freight & Digital",
    "tagline": _("Digital solutions, dispatch services and freight operations"),
    "phone": "+996 (550) 65 51 71",
    "email": settings.INBOX_EMAIL,
    "address": "Kyrgyzstan, Bishkek, 720000, 72, 60 Kalyk Akiev str.",
}


def company(request):
    return {"company": COMPANY}
