"""
Django settings for the IronLane Freight website.

All environment-dependent values come from `ironlane.config`, which validates them
with pydantic-settings. See `.env.example` in the repository root.
"""

from pathlib import Path

from ironlane.config import config

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config.secret_key.get_secret_value()
DEBUG = config.debug
ALLOWED_HOSTS = ["*"] if DEBUG else config.allowed_hosts

if not DEBUG and config.enable_https:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Redirect it-cons.com -> www.it-cons.com (avoids duplicate indexing)
    PREPEND_WWW = config.prepend_www


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ironlane.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main_app.context_processors.company",
            ],
        },
    },
]

WSGI_APPLICATION = "ironlane.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": config.database_path,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("ky", "Кыргызча"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR.parent / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Hashed, compressed files need `collectstatic`, so only use them outside of DEBUG
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}


EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG and not config.email_host_user
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config.email_host
EMAIL_PORT = config.email_port
EMAIL_USE_SSL = config.email_use_ssl
EMAIL_USE_TLS = not config.email_use_ssl
EMAIL_HOST_USER = config.email_host_user
EMAIL_HOST_PASSWORD = config.email_password.get_secret_value()
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = config.default_from_email
INBOX_EMAIL = config.inbox_email


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
