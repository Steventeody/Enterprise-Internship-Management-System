"""
PKL CMS — Attendance Model (minimal untuk dev awal)
"""
from django.db import models
from core.models import BaseModel


class Attendance(BaseModel):

    class Status(models.TextChoices):
        PRESENT = "present", "Hadir"
        LATE    = "late",    "Terlambat"
        ABSENT  = "absent",  "Tidak Hadir"
        EXCUSED = "excused", "Izin"
        REMOTE  = "remote",  "WFH/Remote"

    intern      = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name="Intern"
    )
    date        = models.DateField(verbose_name="Tanggal", db_index=True)
    check_in    = models.TimeField(null=True, blank=True, verbose_name="Check In")
    check_out   = models.TimeField(null=True, blank=True, verbose_name="Check Out")
    status      = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT,
        verbose_name="Status"
    )
    location    = models.CharField(max_length=100, blank=True, verbose_name="Lokasi")
    notes       = models.TextField(blank=True, verbose_name="Catatan")
    approved_by = models.ForeignKey(
        "accounts.CustomUser",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_attendances",
        verbose_name="Disetujui oleh"
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Kehadiran"
        verbose_name_plural = "Kehadiran"
        unique_together = [["intern", "date"]]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.intern.full_name} — {self.date} ({self.status})"

    @property
    def work_hours(self):
        if self.check_in and self.check_out:
            from datetime import datetime, date
            ci = datetime.combine(date.today(), self.check_in)
            co = datetime.combine(date.today(), self.check_out)
            diff = co - ci
            return round(diff.seconds / 3600, 2)
        return 0
