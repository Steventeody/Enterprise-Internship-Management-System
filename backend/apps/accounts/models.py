"""
PKL CMS — Accounts App Models
CustomUser (extends AbstractBaseUser) + InternProfile
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel


# ─────────────────────────────────────────────────
# DEPARTMENT
# ─────────────────────────────────────────────────

class Department(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Departemen")
    code = models.CharField(max_length=10, unique=True, verbose_name="Kode Departemen")
    head = models.ForeignKey(
        "accounts.CustomUser",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="headed_departments",
        verbose_name="Kepala Departemen"
    )

    class Meta:
        verbose_name = "Departemen"
        verbose_name_plural = "Departemen"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}"


# ─────────────────────────────────────────────────
# CUSTOM USER
# ─────────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email wajib diisi.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin, BaseModel):

    class Role(models.TextChoices):
        ADMIN  = "admin",  "Admin (HR)"
        MENTOR = "mentor", "Mentor (Project Manager)"
        INTERN = "intern", "Intern (Mahasiswa PKL)"

    email       = models.EmailField(unique=True, verbose_name="Email")
    full_name   = models.CharField(max_length=255, verbose_name="Nama Lengkap")
    role        = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.INTERN,
        verbose_name="Peran",
        db_index=True
    )
    department  = models.ForeignKey(
        Department,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
        verbose_name="Departemen"
    )
    avatar_url  = models.URLField(blank=True, verbose_name="URL Avatar")
    phone       = models.CharField(max_length=20, blank=True, verbose_name="Telepon")
    is_active   = models.BooleanField(default=True, verbose_name="Aktif")
    is_staff    = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name="Login Terakhir")

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Pengguna"

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    @property
    def is_admin(self):  return self.role == self.Role.ADMIN
    @property
    def is_mentor(self): return self.role == self.Role.MENTOR
    @property
    def is_intern(self): return self.role == self.Role.INTERN


# ─────────────────────────────────────────────────
# INTERN PROFILE
# ─────────────────────────────────────────────────

class InternProfile(BaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="intern_profile",
        limit_choices_to={"role": CustomUser.Role.INTERN},
        verbose_name="Pengguna"
    )
    student_id      = models.CharField(max_length=50, unique=True, verbose_name="NIM")
    university_name = models.CharField(max_length=200, verbose_name="Universitas")
    faculty         = models.CharField(max_length=200, blank=True, verbose_name="Fakultas")
    study_program   = models.CharField(max_length=200, blank=True, verbose_name="Program Studi")
    semester        = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        null=True, blank=True,
        verbose_name="Semester"
    )
    internship_start  = models.DateField(verbose_name="Mulai Magang")
    internship_end    = models.DateField(verbose_name="Selesai Magang")
    mentor = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="mentored_interns",
        limit_choices_to={"role": CustomUser.Role.MENTOR},
        verbose_name="Mentor Perusahaan"
    )
    is_active = models.BooleanField(default=True, verbose_name="Sedang Aktif Magang")
    notes     = models.TextField(blank=True, verbose_name="Catatan")

    class Meta:
        verbose_name = "Profil Intern"
        verbose_name_plural = "Profil Intern"

    def __str__(self):
        return f"{self.user.full_name} — {self.student_id}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.internship_end and self.internship_start:
            if self.internship_end <= self.internship_start:
                raise ValidationError({
                    "internship_end": "Tanggal selesai harus setelah tanggal mulai."
                })

    @property
    def duration_days(self):
        if self.internship_start and self.internship_end:
            return (self.internship_end - self.internship_start).days
        return None
