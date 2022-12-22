import environ
from pathlib import Path

env = environ.Env()
env.prefix = "PENPOT_"

DEBUG = env.bool("DEBUG", False)
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY", "django-insecure-hz0vq%q6tkxey&ofaco)=_h)=qr!t62hjo00s3erfav(bg(wlb")

ALLOWED_HOSTS = env.list("ADMIN_ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "penpot_admin.penpot.apps.PenpotConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "penpot_admin.core.PenpotMiddleware",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.str("REDIS_URI", "redis://redis:6379/1")
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

ROOT_URLCONF = "penpot_admin.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "penpot_admin.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DATABASE_NAME", "penpot"),
        "USER": env.str("DATABASE_USERNAME", "penpot"),
        "PASSWORD": env.str("DATABASE_PASSWORD", "penpot"),
        "HOST": env.str("DATABASE_HOST", "postgres"),
        "PORT": env.str("DATABASE_PORT", "5432")
    }
}

AUTH_PASSWORD_VALIDATORS = []

PUBLIC_URI = env.str("PUBLIC_URI", "http://localhost:3449")
API_URI = env.str("API_URI", "http://localhost:6060")

AUTHENTICATION_BACKENDS = [
    "penpot_admin.auth.PenpotBackend"
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "admin/static/"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "penpot.Profile"
