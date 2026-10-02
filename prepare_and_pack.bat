@echo off
echo Memulai proses pembersihan dan pemaketan...

REM Menghapus file .env
if exist .env (
    del /f /q .env
    echo File .env berhasil dihapus.
) else (
    echo File .env tidak ditemukan, dilewati.
)

REM Menghapus file db.sqlite3 (jika ada di root atau backend)
if exist db.sqlite3 (
    del /f /q db.sqlite3
    echo File db.sqlite3 di root berhasil dihapus.
)
if exist backend\db.sqlite3 (
    del /f /q backend\db.sqlite3
    echo File backend\db.sqlite3 berhasil dihapus.
)

REM Menghapus semua folder __pycache__ secara rekursif
echo Menghapus folder __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Pembersihan selesai. Mulai membuat file TAR.GZ...

REM Membuat file tar.gz di folder induk
tar -czvf "..\pkl-web-project.tar.gz" .

echo.
echo =======================================================
echo Pemaketan selesai!
echo File hasil kompresi berada di folder induk:
cd ..
echo %CD%\pkl-web-project.tar.gz
cd pkl web
echo =======================================================
pause
