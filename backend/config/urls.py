"""
PKL CMS — URL Configuration
Root URL dispatcher yang meregistrasi semua sub-router aplikasi.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ── Django Admin ──────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── Auth (JWT) ────────────────────────────────────────────
    path("api/v1/auth/token/",         TokenObtainPairView.as_view(),  name="token_obtain"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(),     name="token_refresh"),

    # ── Intern Management ─────────────────────────────────────
    path("api/v1/interns/", include("apps.accounts.urls")),

    # ── Task Management ───────────────────────────────────────
    path("api/v1/tasks/", include("apps.tasks.urls")),

    # Endpoint lain ditambahkan bertahap setelah model selesai:
    # path("api/v1/attendance/",   include("apps.attendance.urls")),
    # path("api/v1/evaluations/",  include("apps.evaluations.urls")),
    # path("api/v1/documents/",    include("apps.documents.urls")),
    # path("api/v1/dashboard/",    include("apps.dashboard.urls")),
]

