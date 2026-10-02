"""
PKL CMS — Evaluation Service
Kalkulasi skor akhir dan grade secara objektif berdasarkan bobot kriteria.
"""

from decimal import Decimal
from apps.evaluations.models import Evaluation, EvaluationScore, EvaluationCriteria


class GradeCalculatorService:
    """
    Mengkalkulasi final_score dan grade evaluasi intern secara otomatis.

    Formula:
        final_score = Σ (raw_score_i × weight_i)   untuk setiap kriteria i

    Grade scale (dapat dikonfigurasi di settings):
        A  ≥ 85.00
        B  75.00 – 84.99
        C  65.00 – 74.99
        D  55.00 – 64.99
        E  < 55.00
    """

    GRADE_SCALE = [
        (Decimal("85.00"), "A"),
        (Decimal("75.00"), "B"),
        (Decimal("65.00"), "C"),
        (Decimal("55.00"), "D"),
        (Decimal("0.00"),  "E"),
    ]

    def __init__(self, evaluation: Evaluation):
        self.evaluation = evaluation

    def calculate(self) -> dict:
        """
        Kalkulasi skor akhir dari semua EvaluationScore yang sudah diinput.
        Return dict berisi final_score, grade, dan breakdown per kriteria.
        """
        scores = EvaluationScore.objects.filter(
            evaluation=self.evaluation
        ).select_related("criteria")

        if not scores.exists():
            return {
                "final_score": None,
                "grade": None,
                "breakdown": [],
                "error": "Belum ada nilai yang diinput. Harap isi semua kriteria evaluasi."
            }

        # Validasi: pastikan semua kriteria aktif sudah diisi
        active_criteria_count = EvaluationCriteria.objects.filter(is_active=True).count()
        if scores.count() < active_criteria_count:
            missing = active_criteria_count - scores.count()
            return {
                "final_score": None,
                "grade": None,
                "breakdown": [],
                "error": f"Masih ada {missing} kriteria yang belum dinilai."
            }

        # Hitung skor berbobot
        total_score = Decimal("0.0")
        breakdown = []

        for score in scores:
            weighted = Decimal(str(score.raw_score)) * score.criteria.weight
            total_score += weighted
            breakdown.append({
                "criteria_id":   str(score.criteria.id),
                "criteria_name": score.criteria.name,
                "category":      score.criteria.category,
                "raw_score":     float(score.raw_score),
                "weight":        float(score.criteria.weight),
                "weighted_score": float(round(weighted, 4)),
            })

        final_score = round(total_score, 2)
        grade = self._determine_grade(final_score)

        # Simpan ke database
        self.evaluation.final_score = final_score
        self.evaluation.grade = grade
        self.evaluation.save(update_fields=["final_score", "grade", "updated_at"])

        return {
            "final_score": float(final_score),
            "grade": grade,
            "breakdown": breakdown,
            "total_weight_used": float(sum(
                score.criteria.weight for score in scores
            )),
        }

    def _determine_grade(self, score: Decimal) -> str:
        for threshold, grade in self.GRADE_SCALE:
            if score >= threshold:
                return grade
        return "E"

    @classmethod
    def recalculate_all_for_intern(cls, intern_id: str) -> list:
        """
        Recalculate semua evaluasi (non-finalized) untuk satu intern.
        Digunakan setelah ada perubahan bobot kriteria.
        """
        evaluations = Evaluation.objects.filter(
            intern_id=intern_id,
            status__in=["draft", "submitted"]
        )
        results = []
        for evaluation in evaluations:
            result = cls(evaluation).calculate()
            results.append({
                "evaluation_id": str(evaluation.id),
                "period": evaluation.period_label,
                **result
            })
        return results
