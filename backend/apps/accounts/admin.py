"""
Accounts Admin — CustomUser, Department, InternProfile
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Department, InternProfile


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    ordering       = ("-created_at",)
    list_display   = ("email", "full_name", "role", "department", "is_active", "is_staff")
    list_filter    = ("role", "is_active", "is_staff", "department")
    search_fields  = ("email", "full_name", "phone")
    readonly_fields = ("created_at", "updated_at", "last_login_at", "last_login")

    fieldsets = (
        ("Akun", {
            "fields": ("email", "password"),
        }),
        ("Informasi Pribadi", {
            "fields": ("full_name", "phone", "avatar_url"),
        }),
        ("Peran & Departemen", {
            "fields": ("role", "department"),
        }),
        ("Status", {
            "fields": ("is_active", "is_staff", "is_superuser"),
            "classes": ("collapse",),
        }),
        ("Perizinan", {
            "fields": ("groups", "user_permissions"),
            "classes": ("collapse",),
        }),
        ("Metadata", {
            "fields": ("last_login", "last_login_at", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "role", "department", "password1", "password2"),
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display   = ("code", "name", "head")
    search_fields  = ("name", "code")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Informasi Departemen", {
            "fields": ("name", "code", "head"),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display   = ("user", "student_id", "university_name", "mentor", "is_active")
    list_filter    = ("is_active", "university_name")
    search_fields  = ("user__full_name", "user__email", "student_id", "university_name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Akun Terkait", {
            "fields": ("user",),
        }),
        ("Data Akademik", {
            "fields": ("student_id", "university_name", "faculty", "study_program", "semester"),
        }),
        ("Periode Magang", {
            "fields": ("internship_start", "internship_end", "is_active"),
        }),
        ("Pembimbing", {
            "fields": ("mentor",),
        }),
        ("Catatan", {
            "fields": ("notes",),
            "classes": ("collapse",),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Sembunyikan tombol '+' (tambah cepat) pada field Mentor Perusahaan.
        Mentor sebaiknya ditambahkan melalui menu Pengguna secara langsung."""
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "mentor":
            formfield.widget.can_add_related  = False
            formfield.widget.can_change_related = False
        return formfield

