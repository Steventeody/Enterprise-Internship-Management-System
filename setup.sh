#!/bin/bash
echo "======================================================="
echo "Setup Project Lokal (Tanpa Docker)"
echo "======================================================="

echo "1. Membuat virtual environment (venv)..."
python3 -m venv venv

echo "2. Mengaktifkan venv dan menginstall dependensi..."
source venv/bin/activate
pip install -U pip
pip install -r backend/requirements.txt

echo "3. Menyiapkan environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "File .env berhasil dibuat dari .env.example."
else
    echo "File .env sudah ada."
fi

echo "4. Menjalankan migrasi database SQLite..."
cd backend
python manage.py migrate

echo "5. Membuat superuser default (admin / admin)..."
export DJANGO_SUPERUSER_PASSWORD=admin
python manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Superuser 'admin' mungkin sudah ada atau terjadi kesalahan."
cd ..

echo "======================================================="
echo "Setup selesai! Jalankan ./run.sh untuk memulai server."
echo "======================================================="
