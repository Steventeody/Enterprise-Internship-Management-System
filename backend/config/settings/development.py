"""
Django Settings — Development
Untuk lokal development tanpa Docker.
"""

from pathlib import Path
import environ

# ── Base dir ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── Environment variables ───────────────────────────────────
env = environ.Env(
    DEBUG=(bool, True),
)
environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-secret-key-change-in-production")
DEBUG = True
ALLOWED_HOSTS = ["*"]
X_FRAME_OPTIONS = "SAMEORIGIN"   # diperlukan agar popup '+' di Django Admin bisa terbuka

# ── Apps ────────────────────────────────────────────────────
INSTALLED_APPS = [
    "jazzmin",          # harus sebelum django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # Local apps
    "apps.accounts",
    "apps.tasks",
    "apps.evaluations",
    "apps.attendance",
    "apps.documents",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# ── Database — SQLite untuk dev cepat ───────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── Auth ────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── DRF ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# ── JWT ─────────────────────────────────────────────────────
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
}

# ── CORS ────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True   # Dev only!

# ── Jazzmin Admin Theme ─────────────────────────────────────
JAZZMIN_SETTINGS = {
    # ── Branding ────────────────────────────────────────────
    "site_title":        "IMS Admin",
    "site_header":       "Internship Management System",
    "site_brand":        "IMS",
    "site_logo":         None,          # ganti dengan path logo jika sudah ada
    "login_logo":        None,
    "site_logo_classes": "img-circle",
    "site_icon":         None,
    "welcome_sign":      "Selamat Datang di IMS Admin Panel",
    "copyright":         "PKL CMS © 2025",

    # ── Search ───────────────────────────────────────────────
"search_model": "accounts.CustomUser",
    # ── User avatar ──────────────────────────────────────────
    "user_avatar": None,

    # ── Top Menu ─────────────────────────────────────────────
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Lihat Situs", "url": "/", "new_window": True},
    ],

    # ── User Menu (kanan atas) ────────────────────────────────
    "usermenu_links": [
        {"name": "Profil Saya", "url": "admin:accounts_customuser_change", "icon": "fas fa-user"},
    ],

    # ── Sidebar ──────────────────────────────────────────────
    "show_sidebar":              True,
    "navigation_expanded":       True,
    "hide_apps":                 [],
    "hide_models":               [],
    "order_with_respect_to": [
        "accounts",
        "accounts.CustomUser",
        "accounts.Department",
        "accounts.InternProfile",
        "tasks",
        "tasks.Task",
        "tasks.TaskSubmission",
        "attendance",
        "attendance.Attendance",
        "evaluations",
        "evaluations.Evaluation",
        "evaluations.EvaluationCriteria",
        "evaluations.EvaluationScore",
        "auth",
    ],

    # ── Custom links sidebar ──────────────────────────────────
    "custom_links": {},

    # ── Icons (Font Awesome 5) ────────────────────────────────
    "icons": {
        "auth":                        "fas fa-shield-alt",
        "auth.Group":                  "fas fa-users",
        "accounts.CustomUser":         "fas fa-user-circle",
        "accounts.Department":         "fas fa-building",
        "accounts.InternProfile":      "fas fa-id-badge",
        "tasks.Task":                  "fas fa-tasks",
        "tasks.TaskSubmission":        "fas fa-file-upload",
        "attendance.Attendance":       "fas fa-calendar-check",
        "evaluations.Evaluation":      "fas fa-star",
        "evaluations.EvaluationCriteria": "fas fa-list-check",
        "evaluations.EvaluationScore": "fas fa-chart-bar",
    },
    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # ── Related Modal ─────────────────────────────────────────
    "related_modal_active": True,

    # ── UI Tweaks ─────────────────────────────────────────────
    "custom_css": None,
    "custom_js":  None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,           # aktifkan True saat ingin kustomisasi live

    # ── Change view ───────────────────────────────────────────
    "changeform_format":          "horizontal_tabs",
    "changeform_format_overrides": {
        "accounts.customuser":    "collapsible",
        "accounts.internprofile": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text":       False,
    "footer_small_text":       False,
    "body_small_text":         False,
    "brand_small_text":        False,
    "brand_colour":            "navbar-success",  # aksen hijau profesional
    "accent":                  "accent-teal",
    "navbar":                  "navbar-dark",
    "no_navbar_border":        True,
    "navbar_fixed":            True,
    "layout_boxed":            False,
    "footer_fixed":            False,
    "sidebar_fixed":           True,
    "sidebar":                 "sidebar-dark-teal",  # sidebar gelap dengan aksen teal
    "sidebar_nav_small_text":  False,
    "sidebar_disable_expand":  False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style":   False,
    "theme":                   "cosmo",  # Bootstrap theme bersih & modern
    "dark_mode_theme":         "darkly",
    "button_classes": {
        "primary":   "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}

# ── i18n ────────────────────────────────────────────────────
LANGUAGE_CODE = "id-id"
TIME_ZONE     = "Asia/Jakarta"
USE_I18N      = True
USE_TZ        = True

# ── Static & Media ──────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Email — console backend untuk dev ───────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
