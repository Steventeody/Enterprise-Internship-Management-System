"""
PKL CMS — API Views: Intern Registration & Task Assignment
Endpoint utama yang diminta dalam spesifikasi.
"""

from django.db.models import Count, Q, Avg
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import CustomUser, InternProfile
from apps.accounts.serializers import (
    RegisterInternSerializer, InternDetailSerializer, UserBasicSerializer
)
from apps.tasks.models import Task, TaskSubmission
from apps.tasks.serializers import (
    AssignTaskSerializer, TaskSerializer,
    TaskSubmissionSerializer, ReviewSubmissionSerializer
)
from core.permissions import IsAdmin, IsMentor, IsAdminOrMentor, IsIntern, IsOwnerOrAdmin
from core.audit import log_audit


# ═══════════════════════════════════════════════════════════
# INTERN MANAGEMENT VIEWS
# ═══════════════════════════════════════════════════════════

class RegisterInternView(generics.CreateAPIView):
    """
    POST /api/v1/interns/

    Mendaftarkan mahasiswa PKL baru ke dalam sistem.
    Membuat akun User (role=intern) + InternProfile secara atomik.
    Password sementara dikirim otomatis ke email intern.

    Permission: Admin only
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = RegisterInternSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, profile = serializer.save()

        # Audit log
        log_audit(
            actor=request.user,
            action="CREATE_INTERN",
            entity_type="InternProfile",
            entity_id=profile.id,
            new_data={
                "user_id": str(user.id),
                "student_id": profile.student_id,
                "full_name": user.full_name,
            },
            request=request
        )

        response_data = InternDetailSerializer(user, context={"request": request}).data
        return Response(
            {
                "status": "success",
                "message": f"Intern {user.full_name} berhasil didaftarkan. "
                           f"Password sementara telah dikirim ke {user.email}.",
                "data": response_data
            },
            status=status.HTTP_201_CREATED
        )


class ListInternsView(generics.ListAPIView):
    """
    GET /api/v1/interns/

    Daftar semua intern aktif.
    - Admin: melihat semua intern
    - Mentor: hanya melihat intern bimbingannya
    """
    permission_classes = [IsAuthenticated, IsAdminOrMentor]
    serializer_class = InternDetailSerializer

    def get_queryset(self):
        qs = CustomUser.objects.filter(
            role=CustomUser.Role.INTERN,
            is_active=True
        ).select_related("intern_profile", "intern_profile__mentor", "department")

        user = self.request.user
        if user.role == CustomUser.Role.MENTOR:
            qs = qs.filter(intern_profile__mentor=user)

        # Query params filter
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(intern_profile__student_id__icontains=search) |
                Q(intern_profile__university_name__icontains=search)
            )

        return qs


class InternDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/interns/{id}/      — Detail intern
    PATCH /api/v1/interns/{id}/    — Update profil intern
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = InternDetailSerializer
    queryset = CustomUser.objects.filter(role=CustomUser.Role.INTERN).select_related(
        "intern_profile", "department"
    )


# ═══════════════════════════════════════════════════════════
# TASK MANAGEMENT VIEWS
# ═══════════════════════════════════════════════════════════

class AssignTaskView(generics.CreateAPIView):
    """
    POST /api/v1/tasks/assign/

    Mentor atau Admin membuat dan mengassign tugas baru ke intern.
    Tugas langsung berstatus TODO setelah dibuat.
    Trigger notifikasi email ke intern (async via Celery).

    Permission: Admin atau Mentor
    Request body:
        {
            "title": "Implementasi REST API Login",
            "description": "Buat endpoint /auth/login menggunakan JWT...",
            "priority": "high",
            "assigned_to": "<intern-user-uuid>",
            "department": "<department-uuid>",
            "due_date": "2025-03-15",
            "estimated_hours": 8.0,
            "tags": ["backend", "api", "jwt"]
        }
    """
    permission_classes = [IsAuthenticated, IsAdminOrMentor]
    serializer_class = AssignTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        # Audit log
        log_audit(
            actor=request.user,
            action="ASSIGN_TASK",
            entity_type="Task",
            entity_id=task.id,
            new_data={
                "title": task.title,
                "assigned_to": str(task.assigned_to_id),
                "priority": task.priority,
                "due_date": str(task.due_date) if task.due_date else None,
            },
            request=request
        )

        # Kirim notifikasi ke intern (async)
        from celery_tasks.notifications import send_task_assigned_notification
        send_task_assigned_notification.delay(task_id=str(task.id))

        return Response(
            {
                "status": "success",
                "message": f"Tugas '{task.title}' berhasil diassign ke {task.assigned_to.full_name}.",
                "data": TaskSerializer(task, context={"request": request}).data
            },
            status=status.HTTP_201_CREATED
        )


class TaskListView(generics.ListAPIView):
    """
    GET /api/v1/tasks/

    - Admin: semua tugas
    - Mentor: tugas yang dibuat atau untuk intern bimbingannya
    - Intern: hanya tugas miliknya sendiri

    Query params: status, priority, assigned_to, due_before, due_after
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related(
            "assigned_to", "assigned_by", "department"
        ).prefetch_related("submissions")

        if user.role == CustomUser.Role.INTERN:
            qs = qs.filter(assigned_to=user)
        elif user.role == CustomUser.Role.MENTOR:
            qs = qs.filter(
                Q(assigned_by=user) |
                Q(assigned_to__intern_profile__mentor=user)
            )
        # Admin: tidak ada filter, lihat semua

        # Apply query param filters
        params = self.request.query_params
        if status_filter := params.get("status"):
            qs = qs.filter(status=status_filter)
        if priority_filter := params.get("priority"):
            qs = qs.filter(priority=priority_filter)
        if assignee := params.get("assigned_to"):
            qs = qs.filter(assigned_to__id=assignee)
        if due_before := params.get("due_before"):
            qs = qs.filter(due_date__lte=due_before)
        if due_after := params.get("due_after"):
            qs = qs.filter(due_date__gte=due_after)

        return qs.order_by("-created_at")


class UpdateTaskStatusView(generics.UpdateAPIView):
    """
    PATCH /api/v1/tasks/{id}/status/

    Update status tugas. Validasi transisi status yang valid.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    # Transisi status yang diizinkan
    VALID_TRANSITIONS = {
        Task.Status.BACKLOG:     [Task.Status.TODO],
        Task.Status.TODO:        [Task.Status.IN_PROGRESS, Task.Status.BACKLOG],
        Task.Status.IN_PROGRESS: [Task.Status.IN_REVIEW, Task.Status.TODO],
        Task.Status.IN_REVIEW:   [Task.Status.DONE, Task.Status.REJECTED],
        Task.Status.REJECTED:    [Task.Status.IN_PROGRESS],
        Task.Status.DONE:        [],
    }

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        new_status = request.data.get("status")

        if new_status not in Task.Status.values:
            return Response(
                {"error": f"Status '{new_status}' tidak valid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed = self.VALID_TRANSITIONS.get(task.status, [])
        if new_status not in allowed:
            return Response(
                {"error": f"Transisi dari '{task.status}' ke '{new_status}' tidak diizinkan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save(update_fields=["status", "updated_at"])

        return Response(TaskSerializer(task).data)


class SubmitTaskView(generics.CreateAPIView):
    """
    POST /api/v1/tasks/{id}/submit/

    Intern mengupload submission bukti penyelesaian tugas.
    Secara otomatis mengubah status task ke 'in_review'.

    Permission: Intern (hanya pemilik task)
    """
    permission_classes = [IsAuthenticated, IsIntern]
    serializer_class = TaskSubmissionSerializer

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("pk")
        data = request.data.copy()
        data["task"] = task_id

        serializer = self.get_serializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Submission berhasil dikirim. Menunggu review dari mentor.",
                "data": TaskSubmissionSerializer(submission).data
            },
            status=status.HTTP_201_CREATED
        )


class ReviewSubmissionView(generics.UpdateAPIView):
    """
    PATCH /api/v1/tasks/submissions/{id}/review/

    Mentor mereview submission: memberikan feedback, nilai, dan keputusan (accept/reject).
    Status task otomatis berubah: Done (accept) atau Rejected (reject).

    Permission: Mentor atau Admin
    """
    permission_classes = [IsAuthenticated, IsAdminOrMentor]
    serializer_class = ReviewSubmissionSerializer
    queryset = TaskSubmission.objects.select_related("task", "submitted_by")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data,
            partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()

        verdict = "diterima ✓" if submission.is_accepted else "ditolak ✗"
        return Response(
            {
                "status": "success",
                "message": f"Submission {verdict}. Task status diperbarui.",
                "data": TaskSubmissionSerializer(submission).data
            }
        )


# ═══════════════════════════════════════════════════════════
# DASHBOARD STATS VIEW
# ═══════════════════════════════════════════════════════════

class DashboardStatsView(views.APIView):
    """
    GET /api/v1/dashboard/stats/

    Statistik global untuk kartu ringkasan dasbor.
    - Admin: statistik sistem keseluruhan
    - Mentor: statistik tim bimbingannya
    - Intern: statistik personal
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == CustomUser.Role.ADMIN:
            data = self._admin_stats()
        elif user.role == CustomUser.Role.MENTOR:
            data = self._mentor_stats(user)
        else:
            data = self._intern_stats(user)

        return Response({"status": "success", "data": data})

    def _admin_stats(self):
        # Import lazy agar tidak crash jika model belum ada
        try:
            from apps.attendance.models import Attendance
            from apps.evaluations.models import Evaluation
            _has_attendance = True
            _has_eval = True
        except ImportError:
            _has_attendance = False
            _has_eval = False

        today = timezone.now().date()
        active_interns = InternProfile.objects.filter(is_active=True).count()

        task_stats = Task.objects.aggregate(
            total=Count("id"),
            in_progress=Count("id", filter=Q(status=Task.Status.IN_PROGRESS)),
            in_review=Count("id", filter=Q(status=Task.Status.IN_REVIEW)),
            done=Count("id", filter=Q(status=Task.Status.DONE)),
            overdue=Count("id", filter=Q(
                due_date__lt=today,
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
            ))
        )

        attendance_today = {"present": 0, "absent": 0, "late": 0}
        if _has_attendance:
            attendance_today = Attendance.objects.filter(date=today).aggregate(
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
                late=Count("id", filter=Q(status="late")),
            )

        eval_avg = None
        if _has_eval:
            eval_avg = Evaluation.objects.filter(
                status="finalized"
            ).aggregate(avg=Avg("final_score"))["avg"]

        return {
            "active_interns": active_interns,
            "tasks": task_stats,
            "attendance_today": attendance_today,
            "avg_eval_score": round(eval_avg, 2) if eval_avg else None,
        }

    def _mentor_stats(self, mentor):
        intern_ids = InternProfile.objects.filter(
            mentor=mentor, is_active=True
        ).values_list("user_id", flat=True)

        task_stats = Task.objects.filter(
            assigned_to__in=intern_ids
        ).aggregate(
            total=Count("id"),
            in_progress=Count("id", filter=Q(status=Task.Status.IN_PROGRESS)),
            in_review=Count("id", filter=Q(status=Task.Status.IN_REVIEW)),
            done=Count("id", filter=Q(status=Task.Status.DONE)),
        )

        return {
            "team_interns": len(intern_ids),
            "tasks": task_stats,
        }

    def _intern_stats(self, intern):
        thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)

        task_stats = Task.objects.filter(assigned_to=intern).aggregate(
            total=Count("id"),
            done=Count("id", filter=Q(status=Task.Status.DONE)),
            in_progress=Count("id", filter=Q(status=Task.Status.IN_PROGRESS)),
        )

        attend_stats = {"present": 0, "absent": 0}
        try:
            from apps.attendance.models import Attendance
            attend_stats = Attendance.objects.filter(
                intern=intern,
                date__gte=thirty_days_ago
            ).aggregate(
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
            )
        except Exception:
            pass

        return {
            "tasks": task_stats,
            "attendance_last30": attend_stats,
        }
