from django.conf import settings

COMPANY = {
    "name": "IronLane Freight & Digital",
    "tagline": "Freight dispatch, fleet operations, and custom web solutions",
    "phone": "+1 (555) 014-2200",
    "email": settings.INBOX_EMAIL,
    "address": "2400 Industrial Parkway, Dallas, TX 75207",
    "dot_number": "USDOT 0000000",
    "mc_number": "MC 000000",
}


def company(request):
    return {"company": COMPANY}
