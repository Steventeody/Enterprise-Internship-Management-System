"""
PKL CMS — Tasks Serializers
TaskSerializer, AssignTaskSerializer, TaskSubmissionSerializer
"""

from django.utils import timezone
from rest_framework import serializers
from apps.tasks.models import Task, TaskSubmission
from apps.accounts.serializers import UserBasicSerializer


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserBasicSerializer(source="assigned_to", read_only=True)
    assigned_by_detail = UserBasicSerializer(source="assigned_by", read_only=True)
    is_overdue         = serializers.BooleanField(read_only=True)
    submission_count   = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority",
            "assigned_to", "assigned_to_detail",
            "assigned_by", "assigned_by_detail",
            "department", "due_date", "estimated_hours", "actual_hours",
            "tags", "attachments", "is_overdue",
            "submission_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "assigned_by", "created_at", "updated_at"]

    def get_submission_count(self, obj):
        return obj.submissions.count()


class AssignTaskSerializer(serializers.ModelSerializer):
    """
    Serializer untuk endpoint POST /api/v1/tasks/assign/
    Mentor/Admin mengisi judul, deskripsi, assignee, deadline, dan prioritas.
    """
    class Meta:
        model = Task
        fields = [
            "title", "description", "priority", "assigned_to",
            "department", "due_date", "estimated_hours", "tags",
        ]
        extra_kwargs = {
            "title":       {"required": True},
            "assigned_to": {"required": True},
        }

    def validate_assigned_to(self, user):
        if user.role != user.Role.INTERN:
            raise serializers.ValidationError(
                "Tugas hanya bisa diassign ke pengguna dengan role Intern."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Pengguna intern ini sudah tidak aktif."
            )
        return user

    def validate_due_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "Deadline tidak boleh di masa lalu."
            )
        return value

    def validate(self, data):
        """
        Jika mentor, pastikan intern yang diassign adalah bimbingannya.
        Admin bisa assign ke siapa saja.
        """
        request = self.context.get("request")
        if request and request.user.role == "mentor":
            intern = data.get("assigned_to")
            if intern:
                profile = getattr(intern, "intern_profile", None)
                if profile and profile.mentor_id != request.user.id:
                    raise serializers.ValidationError({
                        "assigned_to": "Anda hanya bisa memberikan tugas kepada intern bimbingan Anda."
                    })
        return data

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["assigned_by"] = request.user
        validated_data["status"] = Task.Status.TODO
        return super().create(validated_data)


class TaskSubmissionSerializer(serializers.ModelSerializer):
    submitted_by_detail = UserBasicSerializer(source="submitted_by", read_only=True)
    task_title          = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = TaskSubmission
        fields = [
            "id", "task", "task_title",
            "submitted_by", "submitted_by_detail",
            "repo_url", "demo_url", "description", "files",
            "mentor_feedback", "mentor_score", "reviewed_by",
            "reviewed_at", "is_accepted", "submitted_at",
        ]
        read_only_fields = [
            "id", "submitted_by", "mentor_feedback", "mentor_score",
            "reviewed_by", "reviewed_at", "is_accepted", "submitted_at",
        ]

    def validate_task(self, task):
        request = self.context["request"]
        if task.assigned_to_id != request.user.id:
            raise serializers.ValidationError(
                "Anda tidak bisa submit tugas yang bukan milik Anda."
            )
        if task.status == Task.Status.DONE:
            raise serializers.ValidationError(
                "Tugas ini sudah selesai dan tidak menerima submission baru."
            )
        return task

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["submitted_by"] = request.user

        submission = super().create(validated_data)

        # Update task status ke 'in_review' secara otomatis
        task = submission.task
        if task.status in (Task.Status.TODO, Task.Status.IN_PROGRESS):
            task.status = Task.Status.IN_REVIEW
            task.save(update_fields=["status", "updated_at"])

        return submission


class ReviewSubmissionSerializer(serializers.ModelSerializer):
    """Untuk mentor mereview submission (feedback, score, accept/reject)."""
    class Meta:
        model = TaskSubmission
        fields = ["mentor_feedback", "mentor_score", "is_accepted"]

    def validate_mentor_score(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError("Nilai harus antara 0 dan 100.")
        return value

    def update(self, instance, validated_data):
        from django.utils import timezone as tz
        request = self.context["request"]
        instance.mentor_feedback = validated_data.get("mentor_feedback", instance.mentor_feedback)
        instance.mentor_score    = validated_data.get("mentor_score", instance.mentor_score)
        instance.is_accepted     = validated_data.get("is_accepted", instance.is_accepted)
        instance.reviewed_by     = request.user
        instance.reviewed_at     = tz.now()
        instance.save()

        # Update task status berdasarkan hasil review
        task = instance.task
        if instance.is_accepted:
            task.status = Task.Status.DONE
        else:
            task.status = Task.Status.REJECTED
        task.save(update_fields=["status", "updated_at"])

        return instance
