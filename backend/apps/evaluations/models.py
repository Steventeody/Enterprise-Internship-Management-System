"""
PKL CMS — Evaluation Models
EvaluationCriteria, Evaluation, EvaluationScore
"""

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from apps.accounts.models import CustomUser


class EvaluationCriteria(BaseModel):

    class Category(models.TextChoices):
        TECHNICAL  = "technical",  "Teknis"
        SOFT_SKILL = "soft_skill", "Soft Skill"
        ATTITUDE   = "attitude",   "Sikap & Kedisiplinan"

    name        = models.CharField(max_length=200, verbose_name="Nama Kriteria")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    category    = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name="Kategori"
    )
    max_score   = models.PositiveSmallIntegerField(default=100, verbose_name="Skor Maksimal")
    weight      = models.DecimalField(
        max_digits=5, decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001")), MaxValueValidator(Decimal("1.0000"))],
        verbose_name="Bobot (0.0–1.0)"
    )
    is_active   = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Kriteria Evaluasi"
        verbose_name_plural = "Kriteria Evaluasi"
        ordering = ["-weight", "name"]

    def __str__(self):
        return f"{self.name} (bobot: {self.weight:.0%})"


class Evaluation(BaseModel):

    class EvalStatus(models.TextChoices):
        DRAFT     = "draft",     "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED  = "approved",  "Disetujui"
        FINALIZED = "finalized", "Finalisasi"

    class Grade(models.TextChoices):
        A = "A", "A — Sangat Baik (≥85)"
        B = "B", "B — Baik (75–84)"
        C = "C", "C — Cukup (65–74)"
        D = "D", "D — Kurang (55–64)"
        E = "E", "E — Tidak Lulus (<55)"

    intern          = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="evaluations",
        limit_choices_to={"role": CustomUser.Role.INTERN},
        verbose_name="Intern"
    )
    mentor          = models.ForeignKey(
        CustomUser,
        on_delete=models.RESTRICT,
        related_name="given_evaluations",
        limit_choices_to={"role__in": [CustomUser.Role.MENTOR, CustomUser.Role.ADMIN]},
        verbose_name="Evaluator"
    )
    period_label    = models.CharField(max_length=100, verbose_name="Periode (Label)")
    status          = models.CharField(
        max_length=15,
        choices=EvalStatus.choices,
        default=EvalStatus.DRAFT,
        verbose_name="Status"
    )
    final_score     = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        verbose_name="Skor Akhir"
    )
    grade           = models.CharField(
        max_length=1,
        choices=Grade.choices,
        blank=True, null=True,
        verbose_name="Grade"
    )
    narrative       = models.TextField(blank=True, verbose_name="Narasi/Komentar Mentor")
    recommendation  = models.TextField(blank=True, verbose_name="Rekomendasi")
    approved_by     = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_evaluations",
        verbose_name="Disetujui oleh"
    )
    approved_at     = models.DateTimeField(null=True, blank=True, verbose_name="Waktu Persetujuan")

    class Meta:
        verbose_name = "Evaluasi"
        verbose_name_plural = "Evaluasi"
        unique_together = [["intern", "period_label"]]

    def __str__(self):
        return f"Evaluasi {self.intern.full_name} — {self.period_label}"


class EvaluationScore(BaseModel):
    evaluation  = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name="Evaluasi"
    )
    criteria    = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.RESTRICT,
        verbose_name="Kriteria"
    )
    raw_score   = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Nilai Mentah"
    )
    notes       = models.TextField(blank=True, verbose_name="Catatan")

    class Meta:
        verbose_name = "Skor Evaluasi"
        verbose_name_plural = "Skor Evaluasi"
        unique_together = [["evaluation", "criteria"]]

    def __str__(self):
        return f"{self.criteria.name}: {self.raw_score}"

    @property
    def weighted_score(self):
        return self.raw_score * self.criteria.weight
