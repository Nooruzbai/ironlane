from django.urls import path

from main_app.views import CareersView, IndexView, QuoteView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("quote/", QuoteView.as_view(), name="quote"),
    path("careers/", CareersView.as_view(), name="careers"),
]
