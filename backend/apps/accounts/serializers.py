"""
PKL CMS — Accounts Serializers
UserSerializer, InternProfileSerializer, RegisterInternSerializer
"""

from django.db import transaction
from rest_framework import serializers
from apps.accounts.models import CustomUser, InternProfile, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code"]


class UserBasicSerializer(serializers.ModelSerializer):
    """Ringkasan user untuk embedding di serializer lain."""
    class Meta:
        model = CustomUser
        fields = ["id", "full_name", "email", "role", "avatar_url"]
        read_only_fields = fields


class InternProfileSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(
        source="mentor.full_name", read_only=True
    )
    duration_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = InternProfile
        fields = [
            "id", "student_id", "university_name", "faculty",
            "study_program", "semester", "internship_start",
            "internship_end", "duration_days", "mentor", "mentor_name",
            "is_active", "notes", "created_at",
        ]


class RegisterInternSerializer(serializers.Serializer):
    """
    Serializer untuk endpoint POST /api/v1/interns/
    Membuat User (role=intern) + InternProfile sekaligus dalam satu transaksi atomik.
    """
    # --- User fields ---
    email       = serializers.EmailField()
    full_name   = serializers.CharField(max_length=255)
    phone       = serializers.CharField(max_length=20, required=False, allow_blank=True)
    department  = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
    )

    # --- InternProfile fields ---
    student_id        = serializers.CharField(max_length=50)
    university_name   = serializers.CharField(max_length=200)
    faculty           = serializers.CharField(max_length=200, required=False, allow_blank=True)
    study_program     = serializers.CharField(max_length=200, required=False, allow_blank=True)
    semester          = serializers.IntegerField(min_value=1, max_value=14, required=False)
    internship_start  = serializers.DateField()
    internship_end    = serializers.DateField()
    mentor_id         = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.Role.MENTOR),
        required=False, allow_null=True
    )
    notes             = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email sudah terdaftar dalam sistem.")
        return value.lower()

    def validate_student_id(self, value):
        if InternProfile.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("NIM sudah terdaftar dalam sistem.")
        return value

    def validate(self, data):
        start = data.get("internship_start")
        end   = data.get("internship_end")
        if start and end and end <= start:
            raise serializers.ValidationError({
                "internship_end": "Tanggal selesai harus setelah tanggal mulai magang."
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Buat User dan InternProfile dalam satu transaksi atomik.
        Password sementara dikirim via email (dihandle Celery task).
        """
        # Pisahkan data user vs profile
        profile_fields = [
            "student_id", "university_name", "faculty", "study_program",
            "semester", "internship_start", "internship_end", "mentor_id", "notes"
        ]
        profile_data = {k: validated_data.pop(k) for k in profile_fields if k in validated_data}
        mentor = profile_data.pop("mentor_id", None)

        # Buat user dengan password sementara (random)
        import secrets, string
        temp_password = "".join(secrets.choice(
            string.ascii_letters + string.digits
        ) for _ in range(12))

        user = CustomUser.objects.create_user(
            role=CustomUser.Role.INTERN,
            **validated_data
        )
        user.set_password(temp_password)
        user.save()

        # Buat profil intern
        profile = InternProfile.objects.create(
            user=user,
            mentor=mentor,
            **profile_data
        )

        # Trigger email task (async)
        from celery_tasks.notifications import send_intern_welcome_email
        send_intern_welcome_email.delay(
            user_id=str(user.id),
            temp_password=temp_password
        )

        return user, profile


class InternDetailSerializer(serializers.ModelSerializer):
    """Serializer lengkap untuk response setelah registrasi intern."""
    intern_profile = InternProfileSerializer(read_only=True)
    department     = DepartmentSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "full_name", "phone", "role",
            "department", "avatar_url", "is_active",
            "intern_profile", "created_at",
        ]
        read_only_fields = fields
