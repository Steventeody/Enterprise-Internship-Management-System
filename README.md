# PKL CMS — Enterprise Internship Management System

> Portal manajemen PKL/Magang internal software house. Dirancang untuk menggantikan proses administrasi manual dengan sistem digital yang terpadu, terukur, dan auditabel.

---

## Tech Stack

| Layer | Teknologi |
|---|---|
| Backend Framework | Django 5.x |
| Database | SQLite (Dev) / PostgreSQL (Prod) |
| Cache / Task Queue | Redis + Celery (Dev support via django-celery-beat/results) |
| REST API | Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Frontend | Vanilla JS + CSS (Bento Grid) |
| PDF Generation | WeasyPrint |

## Roles & Permissions (RBAC)

| Fitur | Admin | Mentor | Intern |
|---|---|---|---|
| Tambah/hapus intern | ✅ | ❌ | ❌ |
| Assign tugas | ✅ | ✅ | ❌ |
| Upload submission | ❌ | ❌ | ✅ |
| Input nilai evaluasi | ❌ | ✅ | ❌ |
| Generate BAST | ✅ | ❌ | ❌ |
| Lihat dashboard global | ✅ | ✅ (team) | ❌ (self) |
| Approve kehadiran | ✅ | ✅ | ❌ |

## Quick Start (Local Development)

Proyek ini menggunakan virtual environment standar Python (tanpa Docker). Database bawaan untuk development adalah **SQLite**, sehingga tidak perlu setup server database eksternal.

### Prasyarat
- **Python 3.10+**
- **pip** (Python package installer)
- **Redis** (Opsional untuk development, wajib untuk production. Jika tidak menginstall Redis, task asinkron mungkin gagal atau harus dijalankan secara synchronous). 

*Catatan: Pada OS Windows, Anda dapat menginstall [Memurai](https://www.memurai.com/) sebagai alternatif Redis native, atau menggunakan WSL2. Jika ingin yang lebih ringan, Anda bisa mengkonfigurasi Celery untuk menggunakan broker berbasis database via `django-celery-results` & `django-celery-beat` yang sudah disertakan di `requirements.txt`.*

### 1. Clone & Setup Awal
Clone repositori ini:
```bash
git clone <repo-url> pkl-cms
cd pkl-cms
```

### 2. Cara Menjalankan Script Setup (Otomatis)
Kami telah menyediakan script untuk membuat virtual environment, menginstall dependensi, dan melakukan setup database awal.

**Windows:**
```bat
setup.bat
```

**Linux / Mac:**
```bash
chmod +x setup.sh run.sh
./setup.sh
```

*(Proses ini juga akan otomatis membuat superuser dengan username: `admin` dan password: `admin`)*

### 3. Cara Menjalankan Server
Gunakan script runner yang telah disediakan:

**Windows:**
```bat
run.bat
```

**Linux / Mac:**
```bash
./run.sh
```
Atau secara manual: `python manage.py runserver` di dalam folder `backend` setelah venv aktif.

### 4. Akses Aplikasi
- **Frontend / Portal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Docs:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

**Kredensial Default:**
- **Username:** `admin`
- **Password:** `admin`

## Dokumentasi Teknis

- [`/docs/architecture.md`](docs/architecture.md) — ERD & Arsitektur Sistem
- [`/docs/api.md`](docs/api.md) — REST API Reference
- [`/docs/ui-spec.md`](docs/ui-spec.md) — UI/UX Spec & Figma Component Guide
- [`/database/schema.sql`](database/schema.sql) — DDL SQL Schema (Untuk PostgreSQL / Production)

## Panduan Ekstrak Project (Untuk Penerima / Pihak Kampus)

Project ini dikompresi menggunakan format `.tar.gz` untuk mempercepat proses kompresi karena ukuran folder yang besar (termasuk folder `venv`).

**Cara Mengekstrak:**
1. **Melalui Command Prompt/PowerShell (Bawaan Windows):**
   Buka terminal di lokasi file `.tar.gz` berada, lalu jalankan perintah:
   ```bash
   tar -xzvf pkl-web-project.tar.gz
   ```
2. **Melalui Aplikasi Pihak Ketiga:**
   Jika Anda menggunakan aplikasi seperti **7-Zip** atau **WinRAR**, Anda dapat mengklik kanan pada file `.tar.gz` dan memilih opsi ekstrak (misal: *Extract Here* atau *Extract to pkl-web-project*).

**Catatan Terkait Virtual Environment (`venv`):**
Folder `venv` (virtual environment) sudah disertakan dalam file kompresi ini untuk memudahkan. Namun, karena virtual environment terikat secara spesifik pada path (lokasi folder) di komputer pengirim, kemungkinan besar `venv` ini **tidak akan berfungsi langsung** jika folder project diletakkan di lokasi atau drive yang berbeda di komputer Anda.

**Jika terjadi error terkait Python atau modul tidak ditemukan setelah ekstrak, ikuti langkah berikut:**
1. Hapus folder `venv` yang lama.
2. Jalankan ulang script `setup.bat` (Windows) atau `setup.sh` (Mac/Linux) untuk membuat virtual environment baru dan menginstall ulang semua dependensi.
3. Setelah `venv` baru berhasil dibuat, lakukan inisiasi ulang database dengan urutan perintah berikut di terminal:
   - **Aktifkan venv:** `venv\Scripts\activate` (Windows) atau `source venv/bin/activate` (Mac/Linux)
   - **Pindah ke folder backend:** `cd backend`
   - **Jalankan migrasi:** `python manage.py migrate`
   - **Buat akun superuser:** `python manage.py createsuperuser`
   - **Jalankan server:** Kembali ke folder utama (`cd ..`) lalu jalankan `run.bat` (Windows) atau `./run.sh` (Mac/Linux).

