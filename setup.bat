@echo off
echo =======================================================
echo Setup Project Lokal (Tanpa Docker)
echo =======================================================

echo 1. Membuat virtual environment (venv)...
python -m venv venv

echo 2. Mengaktifkan venv dan menginstall dependensi...
call venv\Scripts\activate.bat
pip install -U pip
pip install -r backend\requirements.txt

echo 3. Menyiapkan environment variables...
if not exist .env (
    copy .env.example .env
    echo File .env berhasil dibuat dari .env.example.
) else (
    echo File .env sudah ada.
)

echo 4. Menjalankan migrasi database SQLite...
cd backend
python manage.py migrate

echo 5. Membuat superuser default (admin / admin)...
set DJANGO_SUPERUSER_PASSWORD=admin
python manage.py createsuperuser --noinput --username admin --email admin@example.com
if %ERRORLEVEL% NEQ 0 (
    echo Superuser 'admin' mungkin sudah ada atau terjadi kesalahan.
) else (
    echo Superuser 'admin' berhasil dibuat dengan password 'admin'.
)
cd ..

echo =======================================================
echo Setup selesai! Jalankan run.bat untuk memulai server.
echo =======================================================
pause
