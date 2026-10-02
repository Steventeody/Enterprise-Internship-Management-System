#!/bin/bash
echo "======================================================="
echo "Menjalankan Development Server Django..."
echo "======================================================="
source venv/bin/activate
cd backend
python manage.py runserver
