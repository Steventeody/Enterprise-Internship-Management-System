"""
PKL CMS — Tasks App Models
Task (Kanban) + TaskSubmission (bukti penyelesaian intern)
"""

from django.db import models
from core.models import BaseModel
from apps.accounts.models import CustomUser, Department


class Task(BaseModel):

    class Status(models.TextChoices):
        BACKLOG     = "backlog",     "Backlog"
        TODO        = "todo",        "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        IN_REVIEW   = "in_review",   "In Review"
        DONE        = "done",        "Done"
        REJECTED    = "rejected",    "Rejected"

    class Priority(models.TextChoices):
        LOW      = "low",      "Low"
        MEDIUM   = "medium",   "Medium"
        HIGH     = "high",     "High"
        CRITICAL = "critical", "Critical"

    title       = models.CharField(max_length=300, verbose_name="Judul Tugas")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    status      = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.BACKLOG,
        db_index=True,
        verbose_name="Status"
    )
    priority    = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
        verbose_name="Prioritas"
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        limit_choices_to={"role": CustomUser.Role.INTERN},
        verbose_name="Ditugaskan ke"
    )
    assigned_by = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        limit_choices_to={"role__in": [CustomUser.Role.ADMIN, CustomUser.Role.MENTOR]},
        verbose_name="Ditugaskan oleh"
    )
    department      = models.ForeignKey(
        Department,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Departemen"
    )
    due_date        = models.DateField(null=True, blank=True, verbose_name="Deadline", db_index=True)
    estimated_hours = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Estimasi Jam"
    )
    actual_hours    = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Jam Aktual"
    )
    tags        = models.JSONField(default=list, blank=True, verbose_name="Tags")
    attachments = models.JSONField(default=list, blank=True, verbose_name="Lampiran")

    class Meta:
        verbose_name = "Tugas"
        verbose_name_plural = "Tugas"
        indexes = [
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date", "status"]),
        ]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.status != self.Status.DONE:
            return self.due_date < timezone.now().date()
        return False


class TaskSubmission(BaseModel):
    task            = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Tugas"
    )
    submitted_by    = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="task_submissions",
        limit_choices_to={"role": CustomUser.Role.INTERN},
        verbose_name="Dikirim oleh"
    )
    repo_url        = models.URLField(blank=True, verbose_name="URL Repositori")
    demo_url        = models.URLField(blank=True, verbose_name="URL Demo/Staging")
    description     = models.TextField(verbose_name="Penjelasan Implementasi")
    files           = models.JSONField(default=list, blank=True, verbose_name="File Bukti")

    # Review section (diisi oleh mentor)
    mentor_feedback = models.TextField(blank=True, verbose_name="Feedback Mentor")
    mentor_score    = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name="Nilai Mentor (0-100)"
    )
    reviewed_by     = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_submissions",
        verbose_name="Direview oleh"
    )
    reviewed_at     = models.DateTimeField(null=True, blank=True, verbose_name="Waktu Review")
    is_accepted     = models.BooleanField(null=True, blank=True, verbose_name="Diterima?")
    submitted_at    = models.DateTimeField(auto_now_add=True, verbose_name="Waktu Submit")

    class Meta:
        verbose_name = "Submission Tugas"
        verbose_name_plural = "Submission Tugas"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Submission [{self.task.title}] by {self.submitted_by.full_name}"
