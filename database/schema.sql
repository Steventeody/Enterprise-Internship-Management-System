-- =============================================================================
-- PKL CMS — PostgreSQL Database Schema (DDL)
-- Version: 1.0.0
-- Dibuat untuk: Enterprise Internship Management System
-- =============================================================================

-- Aktifkan ekstensi uuid
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- DOMAIN TYPES
-- =============================================================================
CREATE TYPE user_role      AS ENUM ('admin', 'mentor', 'intern');
CREATE TYPE task_status    AS ENUM ('backlog', 'todo', 'in_progress', 'in_review', 'done', 'rejected');
CREATE TYPE task_priority  AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE attend_status  AS ENUM ('present', 'late', 'absent', 'excused', 'remote');
CREATE TYPE eval_status    AS ENUM ('draft', 'submitted', 'approved', 'finalized');
CREATE TYPE grade_letter   AS ENUM ('A', 'B', 'C', 'D', 'E');

-- =============================================================================
-- TABLE: departments
-- Departemen/divisi dalam software house
-- =============================================================================
CREATE TABLE departments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL UNIQUE,
    code        VARCHAR(10)  NOT NULL UNIQUE,
    head_user_id UUID,                        -- FK → users (nullable, set after)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE departments IS 'Divisi/departemen di software house (Backend, Frontend, DevOps, dll)';

-- =============================================================================
-- TABLE: users
-- Semua pengguna sistem: Admin, Mentor, dan Intern
-- =============================================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   TEXT         NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            user_role    NOT NULL DEFAULT 'intern',
    department_id   UUID         REFERENCES departments(id) ON DELETE SET NULL,
    avatar_url      TEXT,
    phone           VARCHAR(20),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'Master tabel pengguna dengan RBAC. Role menentukan hak akses seluruh sistem.';
COMMENT ON COLUMN users.role IS 'admin=HR/Kaprodi, mentor=Project Manager, intern=Mahasiswa PKL';

-- Tambahkan FK head department setelah tabel users dibuat
ALTER TABLE departments
    ADD CONSTRAINT fk_dept_head FOREIGN KEY (head_user_id) REFERENCES users(id) ON DELETE SET NULL;

-- =============================================================================
-- TABLE: intern_profiles
-- Data spesifik mahasiswa PKL (extends users WHERE role='intern')
-- =============================================================================
CREATE TABLE intern_profiles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    student_id          VARCHAR(50) NOT NULL UNIQUE,    -- NIM
    university_name     VARCHAR(200) NOT NULL,
    faculty             VARCHAR(200),
    study_program       VARCHAR(200),
    semester            SMALLINT CHECK (semester BETWEEN 1 AND 14),
    internship_start    DATE NOT NULL,
    internship_end      DATE NOT NULL,
    mentor_id           UUID REFERENCES users(id) ON DELETE SET NULL,  -- Pembimbing
    supervisor_id       UUID REFERENCES users(id) ON DELETE SET NULL,  -- Kaprodi/Penguji
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_internship_dates CHECK (internship_end > internship_start)
);

COMMENT ON TABLE intern_profiles IS 'Profil lengkap mahasiswa PKL: data akademik, periode magang, dan pembimbing';
COMMENT ON COLUMN intern_profiles.mentor_id IS 'Mentor dari perusahaan (role=mentor)';
COMMENT ON COLUMN intern_profiles.supervisor_id IS 'Dosen pembimbing/penguji dari universitas';

-- =============================================================================
-- TABLE: tasks
-- Tugas teknis yang diberikan kepada intern (Kanban board)
-- =============================================================================
CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(300) NOT NULL,
    description     TEXT,
    status          task_status  NOT NULL DEFAULT 'backlog',
    priority        task_priority NOT NULL DEFAULT 'medium',
    assigned_to     UUID REFERENCES users(id) ON DELETE SET NULL,   -- intern user_id
    assigned_by     UUID REFERENCES users(id) ON DELETE SET NULL,   -- mentor user_id
    department_id   UUID REFERENCES departments(id) ON DELETE SET NULL,
    due_date        DATE,
    estimated_hours NUMERIC(5,2),
    actual_hours    NUMERIC(5,2),
    tags            TEXT[],                  -- ['backend', 'api', 'bugfix']
    attachments     JSONB DEFAULT '[]',      -- [{name, url, size, type}]
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE tasks IS 'Tugas teknis Kanban. Status flow: backlog→todo→in_progress→in_review→done/rejected';
COMMENT ON COLUMN tasks.attachments IS 'Array JSON berisi metadata file lampiran tugas';

-- Index untuk query Kanban board
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- =============================================================================
-- TABLE: task_submissions
-- Bukti penyelesaian tugas dari intern
-- =============================================================================
CREATE TABLE task_submissions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    submitted_by    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    repo_url        TEXT,                   -- GitHub/GitLab repository link
    demo_url        TEXT,                   -- Live demo / staging URL
    description     TEXT NOT NULL,          -- Penjelasan implementasi
    files           JSONB DEFAULT '[]',     -- [{name, url, size}]
    mentor_feedback TEXT,
    mentor_score    SMALLINT CHECK (mentor_score BETWEEN 0 AND 100),
    reviewed_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at     TIMESTAMPTZ,
    is_accepted     BOOLEAN,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE task_submissions IS 'Submission dari intern: repo link, file bukti, dan feedback mentor';

CREATE INDEX idx_submissions_task ON task_submissions(task_id);
CREATE INDEX idx_submissions_user ON task_submissions(submitted_by);

-- =============================================================================
-- TABLE: attendance
-- Rekap kehadiran harian intern
-- =============================================================================
CREATE TABLE attendance (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intern_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    check_in        TIME,
    check_out       TIME,
    status          attend_status NOT NULL DEFAULT 'present',
    work_hours      NUMERIC(4,2) GENERATED ALWAYS AS (
                        CASE WHEN check_in IS NOT NULL AND check_out IS NOT NULL
                        THEN EXTRACT(EPOCH FROM (check_out - check_in)) / 3600.0
                        ELSE 0 END
                    ) STORED,
    location        VARCHAR(100),           -- 'office', 'remote', koordinat GPS
    notes           TEXT,
    approved_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (intern_id, date)
);

COMMENT ON TABLE attendance IS 'Absensi harian intern. work_hours dikalkulasi otomatis dari check_in/check_out';

CREATE INDEX idx_attendance_intern ON attendance(intern_id);
CREATE INDEX idx_attendance_date   ON attendance(date);
CREATE INDEX idx_attendance_status ON attendance(status);

-- =============================================================================
-- TABLE: evaluation_criteria
-- Template kriteria penilaian (dapat dikonfigurasi per batch/periode)
-- =============================================================================
CREATE TABLE evaluation_criteria (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    category    VARCHAR(100),              -- 'technical', 'soft_skill', 'attitude'
    max_score   SMALLINT NOT NULL DEFAULT 100,
    weight      NUMERIC(5,4) NOT NULL,     -- bobot (0.0000 - 1.0000), total harus = 1
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE evaluation_criteria IS 'Template kriteria evaluasi. Weight total harus = 1.0 untuk kalkulasi skor akhir yang valid';

-- Seed data kriteria evaluasi standar
INSERT INTO evaluation_criteria (name, description, category, max_score, weight) VALUES
    ('Technical Skill',       'Kemampuan coding, problem solving, debugging',     'technical',  100, 0.35),
    ('Code Quality',          'Clean code, dokumentasi, best practices',          'technical',  100, 0.20),
    ('Task Completion Rate',  'Persentase tugas yang diselesaikan tepat waktu',   'technical',  100, 0.20),
    ('Communication',         'Komunikasi tim, presentasi progress, laporan',     'soft_skill', 100, 0.10),
    ('Attitude & Discipline', 'Kedisiplinan, inisiatif, etika kerja',             'attitude',   100, 0.10),
    ('Attendance',            'Kehadiran, ketepatan waktu check-in',              'attitude',   100, 0.05);

-- =============================================================================
-- TABLE: evaluations
-- Evaluasi akhir per intern oleh mentor
-- =============================================================================
CREATE TABLE evaluations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intern_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentor_id       UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    period_label    VARCHAR(100) NOT NULL,  -- 'Batch 2024/1', 'Jan-Mar 2025'
    status          eval_status NOT NULL DEFAULT 'draft',
    final_score     NUMERIC(6,2),           -- Kalkulasi otomatis (0.00 - 100.00)
    grade           grade_letter,           -- A/B/C/D/E (kalkulasi otomatis)
    narrative       TEXT,                   -- Komentar naratif mentor
    recommendation  TEXT,                   -- Rekomendasi: absorp/tidak/referensi
    approved_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (intern_id, period_label)
);

COMMENT ON TABLE evaluations IS 'Header evaluasi akhir. final_score & grade dikalkulasi oleh backend dari evaluation_scores';

-- =============================================================================
-- TABLE: evaluation_scores
-- Detail nilai per kriteria evaluasi (many-to-many: evaluations × criteria)
-- =============================================================================
CREATE TABLE evaluation_scores (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id   UUID NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
    criteria_id     UUID NOT NULL REFERENCES evaluation_criteria(id) ON DELETE RESTRICT,
    raw_score       NUMERIC(5,2) NOT NULL CHECK (raw_score >= 0),
    weighted_score  NUMERIC(8,4) GENERATED ALWAYS AS (
                        raw_score * (SELECT weight FROM evaluation_criteria ec WHERE ec.id = criteria_id)
                    ) STORED,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (evaluation_id, criteria_id)
);

COMMENT ON TABLE evaluation_scores IS 'Detail nilai per kriteria. weighted_score = raw_score × weight (kalkulasi otomatis)';

CREATE INDEX idx_eval_scores_eval ON evaluation_scores(evaluation_id);

-- =============================================================================
-- TABLE: documents
-- Dokumen yang di-generate sistem (BAST, Surat Keterangan, dll)
-- =============================================================================
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intern_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    evaluation_id   UUID REFERENCES evaluations(id) ON DELETE SET NULL,
    doc_type        VARCHAR(50) NOT NULL,   -- 'BAST', 'certificate', 'recommendation'
    doc_number      VARCHAR(100) UNIQUE,    -- Nomor surat resmi
    title           VARCHAR(300) NOT NULL,
    file_url        TEXT,                   -- Path ke file PDF yang di-generate
    generated_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    signed_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE documents IS 'Dokumen resmi yang di-generate sistem: BAST, sertifikat, surat rekomendasi';

-- =============================================================================
-- TABLE: audit_logs
-- Audit trail untuk semua operasi sensitif
-- =============================================================================
CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,      -- 'CREATE_INTERN', 'ASSIGN_TASK', 'FINALIZE_EVAL'
    entity_type VARCHAR(100),               -- 'Intern', 'Task', 'Evaluation'
    entity_id   UUID,
    old_data    JSONB,
    new_data    JSONB,
    ip_address  INET,
    user_agent  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Immutable audit trail. Tidak ada UPDATE/DELETE pada tabel ini.';

CREATE INDEX idx_audit_user   ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_logs(action);

-- =============================================================================
-- TRIGGERS: Updated At Auto-Update
-- =============================================================================
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplikasikan ke semua tabel yang punya kolom updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'departments', 'users', 'intern_profiles', 'tasks',
        'task_submissions', 'attendance', 'evaluations', 'evaluation_scores', 'documents'
    ]
    LOOP
        EXECUTE format('
            CREATE TRIGGER set_timestamp_%I
            BEFORE UPDATE ON %I
            FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();
        ', t, t);
    END LOOP;
END;
$$;

-- =============================================================================
-- VIEWS: Materialized Views untuk Dashboard
-- =============================================================================

-- View: Statistik per intern (untuk kartu dashboard)
CREATE VIEW v_intern_stats AS
SELECT
    u.id AS intern_id,
    u.full_name,
    ip.university_name,
    ip.internship_start,
    ip.internship_end,
    ip.mentor_id,
    mentor.full_name AS mentor_name,

    -- Task stats
    COUNT(DISTINCT t.id) FILTER (WHERE t.status != 'done') AS tasks_open,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'done')  AS tasks_done,
    COUNT(DISTINCT t.id)                                    AS tasks_total,

    -- Attendance stats (last 30 days)
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'present') AS days_present,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'absent')  AS days_absent,

    -- Latest eval score
    e.final_score,
    e.grade

FROM users u
JOIN intern_profiles ip       ON ip.user_id = u.id
LEFT JOIN users mentor        ON mentor.id = ip.mentor_id
LEFT JOIN tasks t             ON t.assigned_to = u.id
LEFT JOIN attendance a        ON a.intern_id = u.id
                             AND a.date >= CURRENT_DATE - INTERVAL '30 days'
LEFT JOIN evaluations e       ON e.intern_id = u.id AND e.status = 'finalized'
WHERE u.role = 'intern'
  AND ip.is_active = TRUE
GROUP BY
    u.id, u.full_name, ip.university_name, ip.internship_start,
    ip.internship_end, ip.mentor_id, mentor.full_name,
    e.final_score, e.grade;

-- View: Dashboard global admin
CREATE VIEW v_dashboard_summary AS
SELECT
    COUNT(DISTINCT u.id)                             AS total_active_interns,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status IN ('todo','in_progress')) AS tasks_in_progress,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'in_review')             AS tasks_pending_review,
    COUNT(DISTINCT t.id) FILTER (WHERE t.due_date < CURRENT_DATE
                                   AND t.status != 'done')                  AS tasks_overdue,
    ROUND(AVG(e.final_score), 2)                     AS avg_eval_score,
    COUNT(DISTINCT e.id) FILTER (WHERE e.status = 'finalized')             AS evals_finalized
FROM users u
JOIN intern_profiles ip ON ip.user_id = u.id AND ip.is_active = TRUE
LEFT JOIN tasks t        ON t.assigned_to = u.id
LEFT JOIN evaluations e  ON e.intern_id = u.id;
