@echo off
title BAASHA - Domain Setup (www.baasha.com)
color 0B
echo ======================================================================
echo              BAASHA - Setup Domain www.baasha.com
echo ======================================================================
echo.

:: Check for administrative rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting Administrator privileges to map www.baasha.com...
    echo.
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

echo [+] Checking Windows hosts file...
findstr /i "www.baasha.com" "%WINDIR%\System32\drivers\etc\hosts" >nul
if %errorlevel% equ 0 (
    echo [*] www.baasha.com is already configured in your hosts file!
) else (
    echo [+] Adding www.baasha.com and baasha.com mapping to 127.0.0.1...
    echo. >> "%WINDIR%\System32\drivers\etc\hosts"
    echo 127.0.0.1 www.baasha.com baasha.com >> "%WINDIR%\System32\drivers\etc\hosts"
    echo [+] Successfully mapped www.baasha.com to 127.0.0.1!
)

echo.
echo ======================================================================
echo   Success! You can now open http://www.baasha.com:5000 in your browser!
echo ======================================================================
echo.
pause
