@echo off
echo =======================================================
echo Menjalankan Development Server Django...
echo =======================================================
call venv\Scripts\activate.bat
cd backend
python manage.py runserver
