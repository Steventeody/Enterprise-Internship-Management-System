"""
Evaluations Admin — EvaluationCriteria, Evaluation, EvaluationScore
Fitur: Export Excel (rekap semua) & Export PDF (laporan per-intern)
       hanya untuk user dengan role Admin atau Mentor.
"""
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html

from .models import EvaluationCriteria, Evaluation, EvaluationScore
from .exports import (
    export_evaluations_excel,
    export_evaluation_pdf_single,
    export_evaluation_pdf_zip,
)


# ─────────────────────────────────────────────────────────────────
# INLINE
# ─────────────────────────────────────────────────────────────────

class EvaluationScoreInline(admin.TabularInline):
    model   = EvaluationScore
    extra   = 0
    fields  = ("criteria", "raw_score", "notes")
    show_change_link = True


# ─────────────────────────────────────────────────────────────────
# ADMIN ACTIONS — guard RBAC
# ─────────────────────────────────────────────────────────────────

def _check_rbac(request):
    """Pastikan user adalah Admin atau Mentor (role-based)."""
    role = getattr(request.user, "role", None)
    if role not in ("admin", "mentor"):
        raise PermissionDenied(
            "Akses ditolak: hanya Admin atau Mentor yang dapat mengekspor data evaluasi."
        )


@admin.action(description="📥 Export ke Excel (.xlsx) — rekap semua yang dipilih")
def action_export_excel(modeladmin, request, queryset):
    _check_rbac(request)
    return export_evaluations_excel(queryset)


@admin.action(description="📄 Export Laporan PDF (per-intern) — satu atau banyak")
def action_export_pdf(modeladmin, request, queryset):
    _check_rbac(request)
    count = queryset.count()
    if count == 0:
        modeladmin.message_user(request, "Tidak ada evaluasi yang dipilih.", level="warning")
        return
    if count == 1:
        return export_evaluation_pdf_single(queryset.first())
    return export_evaluation_pdf_zip(queryset)


# ─────────────────────────────────────────────────────────────────
# EVALUATION CRITERIA
# ─────────────────────────────────────────────────────────────────

@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display   = ("name", "category", "max_score", "weight_display", "is_active")
    list_filter    = ("category", "is_active")
    search_fields  = ("name", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Kriteria", {
            "fields": ("name", "description", "category"),
        }),
        ("Bobot & Skor", {
            "fields": ("max_score", "weight", "is_active"),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Bobot")
    def weight_display(self, obj):
        pct = float(obj.weight) * 100
        return format_html("<span style='font-weight:600'>{:.0f}%</span>", pct)


# ─────────────────────────────────────────────────────────────────
# EVALUATION (main)
# ─────────────────────────────────────────────────────────────────

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display   = (
        "intern", "mentor", "period_label",
        "status_badge", "final_score", "grade_badge",
    )
    list_filter    = ("status", "grade")
    search_fields  = ("intern__full_name", "mentor__full_name", "period_label")
    readonly_fields = ("approved_at", "created_at", "updated_at")
    inlines        = [EvaluationScoreInline]
    actions        = [action_export_excel, action_export_pdf]

    fieldsets = (
        ("Peserta", {
            "fields": ("intern", "mentor", "period_label"),
        }),
        ("Hasil Evaluasi", {
            "fields": ("status", "final_score", "grade"),
        }),
        ("Narasi & Rekomendasi", {
            "fields": ("narrative", "recommendation"),
            "classes": ("collapse",),
        }),
        ("Persetujuan", {
            "fields": ("approved_by", "approved_at"),
            "classes": ("collapse",),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # ── Custom display columns ────────────────────────────────
    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            "draft":     ("#e5e7eb", "#374151"),
            "submitted": ("#dbeafe", "#1d4ed8"),
            "approved":  ("#d1fae5", "#065f46"),
            "finalized": ("#0f3460", "#ffffff"),
        }
        bg, fg = colors.get(obj.status, ("#e5e7eb", "#333"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:4px;'
            'font-size:0.8em;font-weight:600;text-transform:uppercase">{}</span>',
            bg, fg, obj.get_status_display(),
        )

    @admin.display(description="Grade", ordering="grade")
    def grade_badge(self, obj):
        if not obj.grade:
            return "—"
        colors = {"A": "#16a34a", "B": "#2563eb", "C": "#d97706", "D": "#ea580c", "E": "#dc2626"}
        color = colors.get(obj.grade, "#555")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:4px;'
            'font-weight:700;font-size:0.9em">{}</span>',
            color, obj.grade,
        )


# ─────────────────────────────────────────────────────────────────
# EVALUATION SCORE
# ─────────────────────────────────────────────────────────────────

@admin.register(EvaluationScore)
class EvaluationScoreAdmin(admin.ModelAdmin):
    list_display   = ("evaluation", "criteria", "raw_score")
    search_fields  = ("evaluation__intern__full_name", "criteria__name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Skor", {
            "fields": ("evaluation", "criteria", "raw_score", "notes"),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
