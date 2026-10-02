# Arsitektur Sistem & ERD — PKL CMS

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│   Browser (Vanilla JS)  ←→  Django Templates (SSR fallback)     │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP/REST (JWT Auth)
┌────────────────────────────▼─────────────────────────────────────┐
│                     DJANGO APPLICATION                           │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌───────────────┐ │
│  │ accounts │  │  tasks   │  │ attendance │  │ evaluations   │ │
│  │ (RBAC)   │  │ (Kanban) │  │ (absensi)  │  │ (penilaian)   │ │
│  └──────────┘  └──────────┘  └────────────┘  └───────────────┘ │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────────────┐ │
│  │documents │  │dashboard │  │     core/ (RBAC, audit, utils) │ │
│  │  (BAST)  │  │  (stats) │  │                                │ │
│  └──────────┘  └──────────┘  └────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌────────────┐    ┌──────────────┐    ┌──────────────┐
   │ PostgreSQL │    │    Redis     │    │   Celery     │
   │  (primary) │    │  (cache+MQ)  │    │   (async)    │
   └────────────┘    └──────────────┘    └──────────────┘
```

---

## ERD (Entity Relationship Diagram)

```
┌─────────────────────┐       ┌──────────────────────────────┐
│    departments      │       │           users              │
├─────────────────────┤       ├──────────────────────────────┤
│ PK id (UUID)        │◄──────│ PK id (UUID)                 │
│    name             │  N:1  │    email (UNIQUE)            │
│    code             │       │    password_hash             │
│ FK head_user_id     │       │    full_name                 │
│    created_at       │       │    role ENUM(admin,mentor,   │
│    updated_at       │       │              intern)         │
└─────────────────────┘       │ FK department_id             │
                              │    avatar_url                │
                              │    phone                     │
                              │    is_active                 │
                              │    last_login_at             │
                              └──────────────┬───────────────┘
                                             │
              ┌──────────────────────────────┤
              │                             │1
              │                             ▼
              │              ┌─────────────────────────────┐
              │              │       intern_profiles        │
              │              ├─────────────────────────────┤
              │              │ PK id (UUID)                 │
              │              │ FK user_id (1:1)             │
              │              │    student_id (NIM, UNIQUE)  │
              │              │    university_name           │
              │              │    faculty                   │
              │              │    study_program             │
              │              │    semester                  │
              │              │    internship_start          │
              │              │    internship_end            │
              │              │ FK mentor_id → users         │
              │              │ FK supervisor_id → users     │
              │              │    is_active                 │
              │              └──────────────┬──────────────┘
              │                             │
    ┌─────────┴──────────┐                  │ 1
    │                    │                  ▼
    │ (assigned_to)      │  ┌───────────────────────────────┐
    │       N            │  │          attendance            │
    │       ▼            │  ├───────────────────────────────┤
┌───┴──────────────────┐ │  │ PK id (UUID)                  │
│        tasks         │ │  │ FK intern_id → users          │
├──────────────────────┤ │  │    date                       │
│ PK id (UUID)         │ │  │    check_in                   │
│    title             │ │  │    check_out                  │
│    description       │ │  │    status ENUM(present,late,  │
│    status ENUM       │ │  │              absent,excused,  │
│    priority ENUM     │ │  │              remote)          │
│ FK assigned_to →users│ │  │    work_hours (COMPUTED)      │
│ FK assigned_by →users│ │  │    location                   │
│ FK department_id     │ │  │ FK approved_by → users        │
│    due_date          │ │  │    UNIQUE(intern_id, date)    │
│    estimated_hours   │ │  └───────────────────────────────┘
│    actual_hours      │ │
│    tags (JSONB[])    │ │  ┌───────────────────────────────┐
│    attachments (JSON)│ │  │        evaluations            │
└──────────┬───────────┘ │  ├───────────────────────────────┤
           │ 1           │  │ PK id (UUID)                  │
           ▼ N           │  │ FK intern_id → users          │
┌──────────────────────┐ │  │ FK mentor_id → users          │
│   task_submissions   │ │  │    period_label               │
├──────────────────────┤ │  │    status ENUM(draft,         │
│ PK id (UUID)         │ │  │         submitted,approved,   │
│ FK task_id           │ │  │         finalized)            │
│ FK submitted_by→users│ │  │    final_score (COMPUTED)     │
│    repo_url          │ │  │    grade ENUM(A,B,C,D,E)     │
│    demo_url          │ │  │    narrative                  │
│    description       │ │  │    recommendation             │
│    files (JSONB)     │ │  │ FK approved_by → users        │
│    mentor_feedback   │ │  │    UNIQUE(intern_id,period)   │
│    mentor_score      │ │  └──────────────┬────────────────┘
│ FK reviewed_by→users │ │                 │ 1
│    reviewed_at       │ │                 ▼ N
│    is_accepted       │ │  ┌───────────────────────────────┐
│    submitted_at      │ │  │     evaluation_scores         │
└──────────────────────┘ │  ├───────────────────────────────┤
                         │  │ PK id (UUID)                  │
                         │  │ FK evaluation_id              │
                         │  │ FK criteria_id                │
                         │  │    raw_score                  │
                         │  │    weighted_score (COMPUTED)  │
                         │  │    notes                      │
                         │  │    UNIQUE(eval_id, crit_id)   │
                         │  └───────────────────────────────┘
                         │
                         │  ┌───────────────────────────────┐
                         │  │    evaluation_criteria        │
                         │  ├───────────────────────────────┤
                         │  │ PK id (UUID)                  │
                         └─►│    name                       │
                            │    category ENUM              │
                            │    max_score                  │
                            │    weight (0.0–1.0)           │
                            │    is_active                  │
                            └───────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    documents                          │
├──────────────────────────────────────────────────────┤
│ PK id (UUID)                                         │
│ FK intern_id → users                                 │
│ FK evaluation_id → evaluations                       │
│    doc_type (BAST/certificate/recommendation)        │
│    doc_number (UNIQUE)                               │
│    title                                             │
│    file_url (PDF path)                               │
│ FK generated_by → users                              │
│    signed_at                                         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    audit_logs                         │
├──────────────────────────────────────────────────────┤
│ PK id (BIGSERIAL)                                    │
│ FK user_id → users                                   │
│    action (CREATE_INTERN, ASSIGN_TASK, FINALIZE_EVAL)│
│    entity_type                                       │
│    entity_id (UUID)                                  │
│    old_data (JSONB)                                  │
│    new_data (JSONB)                                  │
│    ip_address                                        │
│    created_at (IMMUTABLE)                            │
└──────────────────────────────────────────────────────┘
```

## Relasi Tabel Ringkasan

| Tabel | Relasi | Keterangan |
|---|---|---|
| `users` → `departments` | N:1 | Setiap user bisa di satu departemen |
| `intern_profiles` → `users` | 1:1 | Profil khusus untuk intern |
| `intern_profiles` → `users (mentor)` | N:1 | Setiap intern punya satu mentor |
| `tasks` → `users (assigned_to)` | N:1 | Banyak tugas bisa ke satu intern |
| `task_submissions` → `tasks` | N:1 | Satu tugas bisa ada banyak submission |
| `attendance` → `users` | N:1 | Satu baris = satu hari per intern |
| `evaluations` → `users` | N:1 | Evaluasi per intern per periode |
| `evaluation_scores` → `evaluations` | N:1 | Detail nilai per kriteria |
| `evaluation_scores` → `criteria` | N:1 | Referensi template kriteria |
| `documents` → `evaluations` | N:1 | BAST dibuat dari evaluasi finalisasi |

## Kalkulasi Skor Evaluasi

```
final_score = Σ (raw_score_i × weight_i)

Contoh:
  Technical Skill    : 80 × 0.35 = 28.00
  Code Quality       : 75 × 0.20 = 15.00
  Task Completion    : 90 × 0.20 = 18.00
  Communication      : 70 × 0.10 =  7.00
  Attitude & Discip  : 85 × 0.10 =  8.50
  Attendance         : 95 × 0.05 =  4.75
                              ──────────
  final_score        =         81.25  → Grade B
```
