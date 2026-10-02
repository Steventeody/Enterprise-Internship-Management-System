"""
Tasks Admin — Task, TaskSubmission
"""
from django.contrib import admin
from .models import Task, TaskSubmission


class TaskSubmissionInline(admin.TabularInline):
    model        = TaskSubmission
    extra        = 0
    readonly_fields = ("submitted_at",)
    fields       = ("submitted_by", "is_accepted", "mentor_score", "submitted_at")
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display   = ("title", "status", "priority", "assigned_to", "assigned_by", "department", "due_date")
    list_filter    = ("status", "priority", "department")
    search_fields  = ("title", "description", "assigned_to__full_name", "assigned_by__full_name")
    date_hierarchy = "due_date"
    readonly_fields = ("created_at", "updated_at")
    inlines        = [TaskSubmissionInline]

    fieldsets = (
        ("Informasi Tugas", {
            "fields": ("title", "description", "tags"),
        }),
        ("Status & Prioritas", {
            "fields": ("status", "priority", "due_date"),
        }),
        ("Penugasan", {
            "fields": ("assigned_to", "assigned_by", "department"),
        }),
        ("Estimasi Waktu", {
            "fields": ("estimated_hours", "actual_hours"),
            "classes": ("collapse",),
        }),
        ("Lampiran", {
            "fields": ("attachments",),
            "classes": ("collapse",),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display   = ("task", "submitted_by", "submitted_at", "mentor_score", "is_accepted", "reviewed_by")
    list_filter    = ("is_accepted",)
    search_fields  = ("task__title", "submitted_by__full_name")
    readonly_fields = ("submitted_at", "created_at", "updated_at")

    fieldsets = (
        ("Referensi", {
            "fields": ("task", "submitted_by"),
        }),
        ("Konten Submission", {
            "fields": ("description", "repo_url", "demo_url", "files"),
        }),
        ("Review Mentor", {
            "fields": ("reviewed_by", "reviewed_at", "mentor_feedback", "mentor_score", "is_accepted"),
        }),
        ("Metadata", {
            "fields": ("submitted_at", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
