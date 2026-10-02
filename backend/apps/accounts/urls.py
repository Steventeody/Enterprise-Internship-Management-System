from django.urls import path
from apps.accounts.views import (
    RegisterInternView, ListInternsView,
    InternDetailView, DashboardStatsView
)

app_name = "accounts"

urlpatterns = [
    # GET    /api/v1/interns/         — Daftar intern (role-filtered)
    path("",            ListInternsView.as_view(),   name="intern-list"),
    # POST   /api/v1/interns/register/ — Tambah intern baru (Admin)
    path("register/",  RegisterInternView.as_view(), name="intern-register"),
    # GET    /api/v1/interns/{id}/    — Detail intern
    path("<uuid:pk>/", InternDetailView.as_view(),   name="intern-detail"),
    # GET    /api/v1/interns/dashboard/stats/ — Statistik dashboard
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
]

