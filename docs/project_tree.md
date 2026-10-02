pkl-cms/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
│
├── database/
│   ├── schema.sql                  # DDL — semua CREATE TABLE
│   ├── seed_data.sql               # Data awal (roles, criteria)
│   └── migrations/                 # Versi migrasi manual (opsional)
│
├── backend/                        # Django Project Root
│   ├── manage.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   │
│   ├── config/                     # Django Settings Package
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py             # Settings bersama
│   │   │   ├── development.py      # Dev overrides (DEBUG=True, SQLite opsional)
│   │   │   └── production.py       # Prod overrides (allowed hosts, HTTPS, S3)
│   │   ├── urls.py                 # Root URL dispatcher
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── apps/
│   │   │
│   │   ├── accounts/               # App: Autentikasi & User Management
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # CustomUser, InternProfile
│   │   │   ├── serializers.py      # UserSerializer, InternProfileSerializer
│   │   │   ├── views.py            # RegisterInternView, LoginView, UserDetailView
│   │   │   ├── permissions.py      # IsAdmin, IsMentor, IsIntern, IsOwnerOrAdmin
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   └── tests/
│   │   │       ├── test_models.py
│   │   │       └── test_views.py
│   │   │
│   │   ├── tasks/                  # App: Manajemen Tugas Kanban
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # Task, TaskSubmission
│   │   │   ├── serializers.py
│   │   │   ├── views.py            # TaskViewSet, TaskSubmissionViewSet
│   │   │   ├── filters.py          # DjangoFilterBackend: status, priority, assignee
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   └── tests/
│   │   │
│   │   ├── attendance/             # App: Sistem Absensi
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # Attendance
│   │   │   ├── serializers.py
│   │   │   ├── views.py            # CheckInView, CheckOutView, AttendanceReportView
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── evaluations/            # App: Sistem Evaluasi & BAST
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # EvaluationCriteria, Evaluation, EvaluationScore
│   │   │   ├── serializers.py
│   │   │   ├── views.py            # EvaluationViewSet, CalculateScoreView
│   │   │   ├── services.py         # GradeCalculatorService, BASTGeneratorService
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── documents/              # App: Generasi Dokumen PDF
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # Document
│   │   │   ├── views.py            # GenerateBASTView, GenerateCertificateView
│   │   │   ├── templates/          # Template HTML untuk WeasyPrint
│   │   │   │   ├── bast.html
│   │   │   │   └── certificate.html
│   │   │   └── urls.py
│   │   │
│   │   └── dashboard/              # App: Dashboard & Statistik
│   │       ├── __init__.py
│   │       ├── views.py            # DashboardStatsView, MentorDashboardView
│   │       └── urls.py
│   │
│   ├── core/                       # Shared utilities
│   │   ├── __init__.py
│   │   ├── models.py               # BaseModel (id UUID, created_at, updated_at)
│   │   ├── permissions.py          # Shared DRF permissions
│   │   ├── pagination.py           # StandardResultsPagination
│   │   ├── exceptions.py           # Custom DRF exception handler
│   │   ├── audit.py                # AuditLog mixin
│   │   └── utils.py                # Helpers (generate doc number, etc.)
│   │
│   └── celery_tasks/               # Async tasks (Celery)
│       ├── __init__.py
│       ├── notifications.py        # Email/notif: deadline reminder, eval ready
│       └── reports.py              # Scheduled: weekly attendance summary
│
├── frontend/                       # Vanilla JS + CSS Frontend
│   ├── index.html                  # SPA shell
│   ├── css/
│   │   ├── main.css                # Design tokens + reset
│   │   ├── bento.css               # Bento Grid layout system
│   │   ├── components.css          # UI Components (cards, badges, modals)
│   │   └── dashboard.css           # Dashboard-specific styles
│   ├── js/
│   │   ├── api.js                  # Axios wrapper + auth interceptor
│   │   ├── router.js               # Client-side routing (hash-based)
│   │   ├── store.js                # State management (lightweight)
│   │   └── pages/
│   │       ├── dashboard.js
│   │       ├── interns.js          # Daftar & form tambah intern
│   │       ├── tasks.js            # Kanban board
│   │       ├── attendance.js
│   │       └── evaluations.js
│   └── assets/
│       ├── icons/
│       └── images/
│
└── docs/
    ├── architecture.md             # ERD + Arsitektur sistem
    ├── api.md                      # REST API Reference
    └── ui-spec.md                  # UI/UX Spec & Figma Component Guide
