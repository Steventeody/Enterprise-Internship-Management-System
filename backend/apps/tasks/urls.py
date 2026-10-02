from django.urls import path
from apps.accounts.views import (
    AssignTaskView, TaskListView, UpdateTaskStatusView,
    SubmitTaskView, ReviewSubmissionView
)

app_name = "tasks"

urlpatterns = [
    # GET    /api/v1/tasks/                  — Daftar tugas (role-filtered)
    path("",                    TaskListView.as_view(),         name="task-list"),
    # POST   /api/v1/tasks/assign/           — Assign tugas baru (Admin/Mentor)
    path("assign/",             AssignTaskView.as_view(),       name="task-assign"),
    # PATCH  /api/v1/tasks/{id}/status/      — Update status Kanban
    path("<uuid:pk>/status/",   UpdateTaskStatusView.as_view(), name="task-status"),
    # POST   /api/v1/tasks/{id}/submit/      — Submit bukti (Intern)
    path("<uuid:pk>/submit/",   SubmitTaskView.as_view(),       name="task-submit"),
    # PATCH  /api/v1/tasks/submissions/{id}/review/ — Review submission (Mentor)
    path("submissions/<uuid:pk>/review/", ReviewSubmissionView.as_view(), name="submission-review"),
]

