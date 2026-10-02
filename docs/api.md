# REST API Reference — PKL CMS
# Version: 1.0 | Base URL: /api/v1

## Authentication

Semua endpoint (kecuali `/auth/token/`) memerlukan header:
```
Authorization: Bearer <access_token>
```

Token diperoleh dari POST `/api/v1/auth/token/`.

---

## Auth Endpoints

### POST /api/v1/auth/token/
Login dan dapatkan JWT token pair.

**Request:**
```json
{ "email": "admin@pklcms.id", "password": "securepass123" }
```

**Response 200:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### POST /api/v1/auth/token/refresh/
Perbarui access token menggunakan refresh token.

---

## Intern Management

### POST /api/v1/interns/register/
Mendaftarkan mahasiswa PKL baru.
**Permission:** `admin`

**Request:**
```json
{
  "email": "budi.santoso@mahasiswa.ui.ac.id",
  "full_name": "Budi Santoso",
  "phone": "08123456789",
  "department": "uuid-dept",
  "student_id": "2106123456",
  "university_name": "Universitas Indonesia",
  "faculty": "Ilmu Komputer",
  "study_program": "Sistem Informasi",
  "semester": 6,
  "internship_start": "2025-01-06",
  "internship_end": "2025-04-04",
  "mentor_id": "uuid-mentor-user"
}
```

**Response 201:**
```json
{
  "status": "success",
  "message": "Intern Budi Santoso berhasil didaftarkan. Password sementara dikirim ke email.",
  "data": {
    "id": "uuid-user",
    "email": "budi.santoso@mahasiswa.ui.ac.id",
    "full_name": "Budi Santoso",
    "role": "intern",
    "intern_profile": {
      "student_id": "2106123456",
      "university_name": "Universitas Indonesia",
      "internship_start": "2025-01-06",
      "internship_end": "2025-04-04",
      "duration_days": 88,
      "mentor_name": "Andi Wijaya"
    }
  }
}
```

**Error 400:**
```json
{
  "email": ["Email sudah terdaftar dalam sistem."],
  "student_id": ["NIM sudah terdaftar dalam sistem."],
  "internship_end": ["Tanggal selesai harus setelah tanggal mulai magang."]
}
```

### GET /api/v1/interns/
Daftar intern aktif. Mentor hanya melihat bimbingannya.
**Permission:** `admin`, `mentor`

**Query Params:** `?search=budi&page=1&page_size=20`

---

## Task Management

### POST /api/v1/tasks/assign/
Assign tugas teknis ke intern.
**Permission:** `admin`, `mentor`

**Request:**
```json
{
  "title": "Implementasi REST API Authentication",
  "description": "Buat endpoint /auth/login dan /auth/logout menggunakan JWT...",
  "priority": "high",
  "assigned_to": "uuid-intern-user",
  "department": "uuid-dept",
  "due_date": "2025-03-15",
  "estimated_hours": 12.5,
  "tags": ["backend", "api", "jwt", "security"]
}
```

**Response 201:**
```json
{
  "status": "success",
  "message": "Tugas 'Implementasi REST API Authentication' berhasil diassign ke Budi Santoso.",
  "data": {
    "id": "uuid-task",
    "title": "Implementasi REST API Authentication",
    "status": "todo",
    "priority": "high",
    "assigned_to_detail": {
      "id": "uuid-intern",
      "full_name": "Budi Santoso",
      "email": "budi@ui.ac.id",
      "role": "intern"
    },
    "assigned_by_detail": {
      "id": "uuid-mentor",
      "full_name": "Andi Wijaya",
      "role": "mentor"
    },
    "due_date": "2025-03-15",
    "estimated_hours": "12.50",
    "is_overdue": false,
    "submission_count": 0
  }
}
```

### GET /api/v1/tasks/
Daftar tugas (role-filtered).
**Query Params:** `?status=in_progress&priority=high&assigned_to=uuid&due_before=2025-04-01`

### PATCH /api/v1/tasks/{id}/status/
Update status task mengikuti state machine yang valid.
**Request:** `{ "status": "in_progress" }`

### POST /api/v1/tasks/{id}/submit/
Intern submit bukti penyelesaian tugas.
**Permission:** `intern`

**Request:**
```json
{
  "task": "uuid-task",
  "repo_url": "https://github.com/budi/pkl-project",
  "demo_url": "https://staging.pklproject.id",
  "description": "Saya mengimplementasikan JWT auth menggunakan library djangorestframework-simplejwt...",
  "files": [
    { "name": "screenshot-api.png", "url": "/media/submissions/uuid.png", "size": 245000 }
  ]
}
```

### PATCH /api/v1/tasks/submissions/{id}/review/
Mentor mereview submission.
**Permission:** `mentor`, `admin`
**Request:** `{ "mentor_feedback": "Baik, perlu refactor error handling", "mentor_score": 85, "is_accepted": true }`

---

## Evaluation

### POST /api/v1/evaluations/
Buat evaluasi akhir intern.
**Permission:** `mentor`, `admin`

**Request:**
```json
{
  "intern_id": "uuid-intern",
  "period_label": "Batch 2025/Q1",
  "narrative": "Budi menunjukkan perkembangan signifikan dalam 3 bulan...",
  "recommendation": "Direkomendasikan untuk project berikutnya",
  "scores": [
    { "criteria_id": "uuid-crit-1", "raw_score": 80, "notes": "Memahami REST API" },
    { "criteria_id": "uuid-crit-2", "raw_score": 75, "notes": "Code masih perlu refactor" },
    { "criteria_id": "uuid-crit-3", "raw_score": 90 },
    { "criteria_id": "uuid-crit-4", "raw_score": 70 },
    { "criteria_id": "uuid-crit-5", "raw_score": 85 },
    { "criteria_id": "uuid-crit-6", "raw_score": 95 }
  ]
}
```

### GET /api/v1/evaluations/{id}/calculate/
Kalkulasi dan simpan skor akhir.
**Permission:** `mentor`, `admin`

**Response 200:**
```json
{
  "final_score": 81.25,
  "grade": "B",
  "breakdown": [
    { "criteria_name": "Technical Skill", "raw_score": 80, "weight": 0.35, "weighted_score": 28.0 },
    { "criteria_name": "Code Quality",    "raw_score": 75, "weight": 0.20, "weighted_score": 15.0 },
    { "criteria_name": "Task Completion", "raw_score": 90, "weight": 0.20, "weighted_score": 18.0 },
    { "criteria_name": "Communication",   "raw_score": 70, "weight": 0.10, "weighted_score": 7.0 },
    { "criteria_name": "Attitude",        "raw_score": 85, "weight": 0.10, "weighted_score": 8.5 },
    { "criteria_name": "Attendance",      "raw_score": 95, "weight": 0.05, "weighted_score": 4.75 }
  ],
  "total_weight_used": 1.0
}
```

---

## Dashboard

### GET /api/v1/dashboard/stats/
Statistik dasbor sesuai role pengguna yang login.

**Response (Admin) 200:**
```json
{
  "status": "success",
  "data": {
    "active_interns": 24,
    "tasks": {
      "total": 187, "in_progress": 43, "in_review": 12, "done": 120, "overdue": 5
    },
    "attendance_today": { "present": 20, "absent": 2, "late": 2 },
    "avg_eval_score": 78.45
  }
}
```

---

## HTTP Status Codes

| Code | Makna |
|---|---|
| 200 | OK — request berhasil |
| 201 | Created — resource baru berhasil dibuat |
| 400 | Bad Request — validasi gagal |
| 401 | Unauthorized — token tidak ada atau expired |
| 403 | Forbidden — role tidak memiliki izin |
| 404 | Not Found — resource tidak ditemukan |
| 409 | Conflict — duplikat data (email/NIM) |
| 422 | Unprocessable — business rule violation |
| 500 | Internal Server Error |
