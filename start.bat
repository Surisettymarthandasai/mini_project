@echo off
REM Academic Management System - Automatic Setup Script
REM This script will set up the database and start the server

echo ======================================================================
echo Academic Management System - Auto Setup
echo ======================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv .venv
    echo [+] Virtual environment created
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [*] Installing dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies
    pause
    exit /b 1
)
echo [+] Dependencies installed

REM Setup database
echo.
echo ======================================================================
echo Database Setup
echo ======================================================================
echo.
echo This will automatically create the MySQL database and tables.
echo.
echo Press Ctrl+C to cancel or any key to continue with default credentials
echo (MySQL root@localhost:3306, database: academic_mgmt)
echo.
pause >nul

python manage.py setup_database
if %errorlevel% neq 0 (
    echo.
    echo [!] Database setup failed!
    echo.
    echo Would you like to try with custom credentials? (Y/N)
    set /p custom=
    if /i "%custom%"=="Y" (
        echo.
        echo Enter MySQL credentials:
        set /p db_host=Host (default 127.0.0.1): 
        if "%db_host%"=="" set db_host=127.0.0.1
        
        set /p db_user=Username (default root): 
        if "%db_user%"=="" set db_user=root
        
        set /p db_pass=Password: 
        if "%db_pass%"=="" set db_pass=root
        
        python manage.py setup_database --host %db_host% --user %db_user% --password %db_pass%
        if %errorlevel% neq 0 (
            echo [!] Setup failed with custom credentials
            pause
            exit /b 1
        )
    ) else (
        pause
        exit /b 1
    )
)

echo.
echo ======================================================================
echo Setup Complete!
echo ======================================================================
echo.
echo [+] Database is ready
echo [+] Tables have been created
echo.
echo Next steps:
echo   1. Create an admin user: python manage.py createsuperuser
echo   2. Start the server: python manage.py runserver
echo.
echo Would you like to create an admin user now? (Y/N)
set /p create_admin=
if /i "%create_admin%"=="Y" (
    echo.
    python manage.py createsuperuser
)

echo.
echo ======================================================================
echo Starting Development Server
echo ======================================================================
echo.
echo Clearing old sessions (forcing logout of all users)...
python manage.py clear_sessions --all >nul 2>&1
echo [+] Old sessions cleared
echo.
echo Syncing user profiles with academic system...
python manage.py sync_profiles >nul 2>&1
echo [+] Profiles synchronized
echo.
echo Loading JNTUH subjects...
python manage.py load_jntuh_subjects >nul 2>&1
echo [+] Subjects loaded
echo.
echo Server will start at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
echo NOTE: Sessions auto-expire after 30 minutes of inactivity
echo.
pause

python manage.py runserver

pause
