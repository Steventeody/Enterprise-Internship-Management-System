"""
PKL CMS — RBAC Permission Classes
Implementasi Role-Based Access Control dengan tiga tier: Admin, Mentor, Intern.

Semua permission class mewarisi BasePermission dari DRF dan melakukan cek
pada user.role yang tersimpan di database.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


# ─────────────────────────────────────────────────
# ROLE CONSTANTS (sinkronkan dengan model User)
# ─────────────────────────────────────────────────
class Roles:
    ADMIN  = "admin"
    MENTOR = "mentor"
    INTERN = "intern"


# ─────────────────────────────────────────────────
# ATOMIC ROLE PERMISSIONS
# ─────────────────────────────────────────────────

class IsAdmin(BasePermission):
    """
    Hanya admin (HR/Kaprodi) yang boleh mengakses.
    Digunakan untuk: tambah/hapus intern, finalize evaluasi, generate BAST.
    """
    message = "Akses ditolak: hanya Admin yang dapat melakukan tindakan ini."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == Roles.ADMIN
        )


class IsMentor(BasePermission):
    """
    Hanya mentor (Project Manager) yang boleh mengakses.
    Digunakan untuk: assign tugas, review submission, input nilai evaluasi.
    """
    message = "Akses ditolak: hanya Mentor yang dapat melakukan tindakan ini."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == Roles.MENTOR
        )


class IsIntern(BasePermission):
    """
    Hanya intern (mahasiswa) yang boleh mengakses.
    Digunakan untuk: upload submission, check-in/check-out absensi.
    """
    message = "Akses ditolak: hanya Intern yang dapat melakukan tindakan ini."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == Roles.INTERN
        )


# ─────────────────────────────────────────────────
# COMPOSITE PERMISSIONS
# ─────────────────────────────────────────────────

class IsAdminOrMentor(BasePermission):
    """Admin atau Mentor dapat mengakses. Digunakan untuk approve kehadiran."""
    message = "Akses ditolak: hanya Admin atau Mentor."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in (Roles.ADMIN, Roles.MENTOR)
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin bisa tulis; semua authenticated user bisa baca (GET, HEAD, OPTIONS).
    Digunakan untuk resource seperti EvaluationCriteria.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == Roles.ADMIN


# ─────────────────────────────────────────────────
# OBJECT-LEVEL PERMISSIONS
# ─────────────────────────────────────────────────

class IsOwnerOrAdmin(BasePermission):
    """
    User hanya bisa mengakses/memodifikasi objek miliknya sendiri.
    Admin dapat mengakses semua objek.

    Syarat: objek harus memiliki atribut `user` atau `intern` yang merujuk ke User.
    """
    message = "Akses ditolak: Anda hanya bisa mengakses data milik sendiri."

    def has_object_permission(self, request, view, obj):
        if request.user.role == Roles.ADMIN:
            return True

        # Cek atribut kepemilikan yang umum digunakan
        owner_attrs = ("user", "intern", "submitted_by", "assigned_to")
        for attr in owner_attrs:
            owner = getattr(obj, attr, None)
            if owner is not None:
                owner_id = getattr(owner, "id", owner)
                return owner_id == request.user.id

        return False


class IsMentorOfIntern(BasePermission):
    """
    Mentor hanya bisa mengakses data intern yang dibimbingnya.
    Digunakan untuk evaluasi dan task assignment.
    """
    message = "Akses ditolak: intern ini bukan bimbingan Anda."

    def has_object_permission(self, request, view, obj):
        if request.user.role == Roles.ADMIN:
            return True

        if request.user.role == Roles.MENTOR:
            # obj bisa Intern profile atau Task
            intern_user = getattr(obj, "assigned_to", None) or getattr(obj, "user", None)
            if intern_user:
                intern_profile = getattr(intern_user, "intern_profile", None)
                if intern_profile:
                    return intern_profile.mentor_id == request.user.id

        return False
