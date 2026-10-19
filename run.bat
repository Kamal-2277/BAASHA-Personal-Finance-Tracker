@echo off
title BAASHA - Personal Finance Tracker
color 0A
echo ======================================================================
echo             BAASHA - PERSONAL FINANCE TRACKER
echo             College Investigatory Project
echo             Team: Kamallesh, Janardhana, Suriya
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python environment...
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=py
) else (
    set PY_CMD=python
)

echo [2/3] Verifying dependencies...
%PY_CMD% -m pip install -r requirements.txt --quiet

echo [3/3] Starting BAASHA Web Application on http://www.baasha.com:5000 (and http://127.0.0.1:5000) ...
echo.
echo Launching your default web browser...
start http://127.0.0.1:5000

%PY_CMD% app.py

pause
