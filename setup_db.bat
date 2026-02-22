@echo off
REM Quick setup script - just creates database and tables

echo ======================================================================
echo Database Setup - Academic Management System
echo ======================================================================
echo.

call .venv\Scripts\activate.bat

echo This will create the database 'academic_mgmt' with default credentials.
echo.
echo MySQL root@localhost:3306
echo Database: academic_mgmt
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

python manage.py setup_database

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo SUCCESS! Database is ready.
    echo ======================================================================
    echo.
    echo You can now:
    echo   1. Run the server: python manage.py runserver
    echo   2. Create admin: python manage.py createsuperuser
    echo.
) else (
    echo.
    echo ======================================================================
    echo Setup failed. Try with custom credentials:
    echo ======================================================================
    echo.
    echo python manage.py setup_database --user YOUR_USER --password YOUR_PASS
    echo.
)

pause
