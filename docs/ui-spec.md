# UI/UX Specification — PKL CMS Dashboard
## Standar: Nielsen's 10 Usability Heuristics + Bento Grid Layout

---

## 1. Design System Tokens

```css
/* ── Color Palette ────────────────────────────────── */
--color-bg-base:       #0A0E1A;   /* Deep navy — background utama */
--color-bg-surface:    #111827;   /* Surface card */
--color-bg-elevated:   #1C2333;   /* Elevated card / modal */
--color-bg-hover:      #1F2D40;   /* Hover state */

--color-accent-blue:   #3B82F6;   /* Primary action */
--color-accent-violet: #8B5CF6;   /* Secondary / tag */
--color-accent-emerald:#10B981;   /* Success / done */
--color-accent-amber:  #F59E0B;   /* Warning / in-review */
--color-accent-rose:   #F43F5E;   /* Danger / overdue */
--color-accent-cyan:   #06B6D4;   /* Info / attendance */

--color-text-primary:  #F1F5F9;
--color-text-secondary:#94A3B8;
--color-text-muted:    #475569;
--color-border:        #1E293B;
--color-border-glow:   rgba(59, 130, 246, 0.25);

/* ── Typography ───────────────────────────────────── */
--font-sans: 'Inter', 'Plus Jakarta Sans', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

--text-xs:   0.75rem;    /* 12px — label, tag */
--text-sm:   0.875rem;   /* 14px — body kecil */
--text-base: 1rem;       /* 16px — body default */
--text-lg:   1.125rem;   /* 18px — subheading */
--text-xl:   1.25rem;    /* 20px — card title */
--text-2xl:  1.5rem;     /* 24px — section heading */
--text-3xl:  1.875rem;   /* 30px — page heading */
--text-4xl:  2.25rem;    /* 36px — stat number */

/* ── Spacing ──────────────────────────────────────── */
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-6: 1.5rem;     /* 24px — card padding */
--space-8: 2rem;       /* 32px — section gap */

/* ── Radius ───────────────────────────────────────── */
--radius-sm:  8px;
--radius-md:  12px;
--radius-lg:  16px;
--radius-xl:  20px;
--radius-full: 9999px;

/* ── Shadow / Glow ────────────────────────────────── */
--shadow-card:   0 4px 24px rgba(0,0,0,0.4);
--shadow-glow:   0 0 20px rgba(59,130,246,0.15);
--shadow-active: 0 0 0 2px var(--color-accent-blue);
```

---

## 2. Bento Grid Dashboard Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  SIDEBAR (64px)  │           MAIN CONTENT AREA                     │
│                  │  ┌──────────────────────────────────────────┐   │
│  ┌──┐ Logo       │  │  Topbar: breadcrumb + user avatar + bell │   │
│  ──  Dasbor ←   │  └──────────────────────────────────────────┘   │
│  ──  Intern      │                                                  │
│  ──  Tugas       │  ┌─── BENTO GRID (12-col) ──────────────────┐   │
│  ──  Absensi     │  │                                           │   │
│  ──  Evaluasi    │  │ [StatCard] [StatCard] [StatCard][StatCard]│   │
│  ──  Dokumen     │  │  3-col     3-col       3-col    3-col     │   │
│                  │  │                                           │   │
│  ──  Settings    │  │ ┌─── Kanban Progress ───┐ ┌── Attendance─┐│   │
│  ──  Logout      │  │ │   8-col span          │ │  4-col span  ││   │
│                  │  │ │   Task status bars    │ │  Heatmap     ││   │
│                  │  │ └───────────────────────┘ └──────────────┘│   │
│                  │  │                                           │   │
│                  │  │ ┌── Intern List ──────┐ ┌── Eval Radar ──┐│   │
│                  │  │ │   6-col             │ │   6-col        ││   │
│                  │  │ │   Table + filters   │ │   Chart.js     ││   │
│                  │  │ └─────────────────────┘ └────────────────┘│   │
│                  │  │                                           │   │
│                  │  │ ┌── Recent Activity (Audit Log) 12-col ──┐│   │
│                  │  │ │   Timeline feed dengan avatar + action ││   │
│                  │  │ └────────────────────────────────────────┘│   │
│                  │  └───────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Komponen Utama (Figma Component Spec)

### A. StatCard (4× di atas dashboard)

```
┌─────────────────────────────┐
│  ┌───┐                      │
│  │ 📋│  Total Intern Aktif  │
│  └───┘                      │
│                             │
│        24                   │  ← font-size: 36px, weight: 700
│  ↑ +3 dari bulan lalu       │  ← text-color: emerald (positif)
└─────────────────────────────┘

Properties:
  - icon: Lucide icon (24px, rounded-bg)
  - title: string
  - value: number | string
  - delta: { value: string; direction: 'up' | 'down' | 'neutral' }
  - variant: 'blue' | 'violet' | 'emerald' | 'amber'
  - glassmorphism: backdrop-filter: blur(12px)
  - hover: translateY(-2px) + border-color glow

4 Stat Cards:
  1. 🎓 Intern Aktif       — warna: blue
  2. 📋 Tugas Berjalan     — warna: violet
  3. ✅ Selesai Minggu Ini  — warna: emerald
  4. ⚠️ Tugas Overdue      — warna: amber
```

### B. KanbanProgressPanel (8-col)

```
Kanban Progress Bar (horizontal):
  Backlog   [▓▓░░░░░░░░] 20%
  To Do     [▓▓▓▓░░░░░░] 40%
  In Prog   [▓▓▓▓▓▓░░░░] 60%
  In Review [▓▓▓░░░░░░░] 30%
  Done      [▓▓▓▓▓▓▓▓░░] 80%

+ Daftar 5 tugas terbaru dengan:
  [Avatar intern] [Nama tugas] [Priority badge] [Deadline] [Status pill]
```

### C. AttendanceHeatmap (4-col)

```
Heatmap style Github contribution:
  Minggu 1: ■ ■ ■ ■ □
  Minggu 2: ■ ■ □ ■ ■
  Minggu 3: ■ ■ ■ ■ ■
  Minggu 4: ■ ○ ■ ■ ■

Legend:
  ■ Hadir  ■ Late  ○ Absen  □ Izin

Footer: "Kehadiran bulan ini: 87.5%"
Compact stats: Hadir: 21 | Terlambat: 2 | Absen: 1
```

### D. EvaluationRadarChart (6-col)

```
Chart.js Radar — 6 sumbu:
  - Technical Skill
  - Code Quality
  - Task Completion
  - Communication
  - Attitude
  - Attendance

Style:
  backgroundColor: rgba(59, 130, 246, 0.15)
  borderColor: #3B82F6
  pointBackgroundColor: #3B82F6

Below chart:
  [Grade Badge: B+]  [Score: 81.25/100]
  [Status: Submitted — Menunggu Finalisasi]
```

### E. InternTable (6-col)

```
┌──┬──────────────────┬──────────┬────────┬───────┬──────────┐
│  │ Nama Intern      │ Univ     │ Mentor │ Tasks │ Action   │
├──┼──────────────────┼──────────┼────────┼───────┼──────────┤
│🟢│ Budi Santoso     │ UI       │ Andi   │ 8/12  │ [Detail] │
│🟡│ Siti Rahayu      │ ITB      │ Reza   │ 5/10  │ [Detail] │
│🔴│ Ahmad Fauzi      │ UGM      │ Andi   │ 2/8   │ [Detail] │
└──┴──────────────────┴──────────┴────────┴───────┴──────────┘
```

### F. Activity Timeline (12-col)

```
● [Avatar] Admin menambahkan Budi Santoso sebagai intern   — 5 menit lalu
● [Avatar] Mentor Andi mengassign tugas "REST API Login"   — 1 jam lalu
● [Avatar] Siti Rahayu submit tugas "Database Design"      — 2 jam lalu
● [Avatar] Evaluasi Ahmad Fauzi difinalisasi (Grade: B)    — 3 jam lalu
```

---

## 4. Nielsen's 10 Heuristics — Implementasi

| Heuristic | Implementasi dalam CMS |
|---|---|
| **1. Visibility of System Status** | Loading skeleton saat fetch data, progress bar saat generate PDF, badge status realtime pada task card |
| **2. Match Between System & Real World** | Terminologi Bahasa Indonesia (PKL, Magang, NIM, BAST), ikon intuitif, label "Grade B" bukan kode internal |
| **3. User Control & Freedom** | Konfirmasi dialog sebelum hapus, tombol "Batalkan" pada setiap form modal, undo toast 5 detik |
| **4. Consistency & Standards** | Design tokens CSS terpusat, komponen reusable, pola URL REST yang konsisten |
| **5. Error Prevention** | Validasi inline sebelum submit, disable tombol saat form tidak lengkap, date picker dengan range restriction |
| **6. Recognition over Recall** | Sidebar navigasi selalu terlihat, breadcrumb path, tooltip pada semua icon action |
| **7. Flexibility & Efficiency** | Keyboard shortcut (K: Kanban, I: Intern, E: Eval), filter pinned, bulk action pada tabel |
| **8. Aesthetic & Minimalist Design** | Bento grid menampilkan hanya info kritis, whitespace cukup, typographic hierarchy ketat |
| **9. Help Users Recognize Errors** | Pesan error spesifik (bukan "Error 400"), highlight field bermasalah berwarna rose, solusi tertulis |
| **10. Help & Documentation** | Tooltip contextual, halaman help dengan glossary, empty state informatif dengan CTA |

---

## 5. Micro-Animations Spec

```css
/* Card hover lift */
.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(59, 130, 246, 0.2);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Status badge pulse (untuk overdue) */
.badge-overdue {
  animation: pulse-rose 2s ease-in-out infinite;
}
@keyframes pulse-rose {
  0%, 100% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.4); }
  50%       { box-shadow: 0 0 0 8px rgba(244, 63, 94, 0); }
}

/* Number counter animation (StatCard) */
.stat-value { transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); }

/* Skeleton loading shimmer */
.skeleton {
  background: linear-gradient(90deg,
    #1C2333 25%, #253044 50%, #1C2333 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
```

---

## 6. Page Inventory (Untuk Figma Frame)

| Frame Name | Route | Role Access |
|---|---|---|
| 🏠 Dashboard | `/dashboard` | All (role-filtered) |
| 👥 Intern List | `/interns` | Admin, Mentor |
| ➕ Tambah Intern | `/interns/new` | Admin only |
| 📋 Task Board (Kanban) | `/tasks` | All |
| ✅ Task Detail + Submit | `/tasks/:id` | All |
| 🗓 Absensi | `/attendance` | All |
| ⭐ Evaluasi | `/evaluations` | Mentor, Admin |
| 📊 Evaluasi Detail | `/evaluations/:id` | Mentor, Admin |
| 📄 Generate BAST | `/documents/bast/:id` | Admin only |
| ⚙️ Pengaturan | `/settings` | Admin only |
| 🔑 Login | `/login` | Public |
