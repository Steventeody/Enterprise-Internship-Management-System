"""
Attendance Admin — Attendance
"""
from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display   = ("intern", "date", "status", "check_in", "check_out", "location", "approved_by")
    list_filter    = ("status", "date", "location")
    search_fields  = ("intern__full_name", "intern__email", "location", "notes")
    date_hierarchy = "date"
    readonly_fields = ("approved_at", "created_at", "updated_at")

    fieldsets = (
        ("Intern & Tanggal", {
            "fields": ("intern", "date"),
        }),
        ("Waktu Kehadiran", {
            "fields": ("status", "check_in", "check_out", "location"),
        }),
        ("Persetujuan", {
            "fields": ("approved_by", "approved_at", "notes"),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
