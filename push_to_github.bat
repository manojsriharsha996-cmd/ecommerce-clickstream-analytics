@echo off
title Push to GitHub - E-Commerce Clickstream Analytics
cd /d "%~dp0"

REM Add local Git to PATH
if exist "C:\Users\MANOJ\.local\git\cmd\git.exe" (
    set "PATH=C:\Users\MANOJ\.local\git\cmd;%PATH%"
)

echo =========================================================================
echo    GitHub Push Helper - E-Commerce Clickstream Analytics
echo    Student: KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
echo =========================================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git could not be located.
    pause
    exit /b
)

echo [OK] Git is ready.
echo.
echo -------------------------------------------------------------------------
echo STEP 1: Make sure you created a repository on GitHub named:
echo         ecommerce-clickstream-analytics
echo         (Go to: https://github.com/new)
echo -------------------------------------------------------------------------
echo.
set /p USER_INPUT="STEP 2: Enter your GitHub Username (or full Repo URL) and press ENTER: "

if "%USER_INPUT%"=="" (
    echo [ERROR] No input provided. Exiting...
    pause
    exit /b
)

echo %USER_INPUT% | findstr /i "github.com" >nul
if %ERRORLEVEL% equ 0 (
    set "REPO_URL=%USER_INPUT%"
) else (
    set "REPO_URL=https://github.com/%USER_INPUT%/ecommerce-clickstream-analytics.git"
)

echo.
echo Target Repository: %REPO_URL%
echo.

if not exist .git (
    echo Initializing Git...
    git init
)

echo Staging files...
git add .

echo Committing files...
git commit -m "Initial commit: E-Commerce Clickstream Big Data Pipeline & Dashboard" >nul 2>&1

echo Setting main branch...
git branch -M main

echo Configuring remote...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo.
echo Pushing project to GitHub...
echo (If a browser window appears, click 'Sign in with your browser' to authorize)
echo.

git push -u origin main

if %ERRORLEVEL% neq 0 (
    echo.
    echo [INFO] Normal push failed. Attempting to sync with remote...
    git pull origin main --rebase --autostash >nul 2>&1
    git push -u origin main
)

if %ERRORLEVEL% equ 0 (
    echo.
    echo =========================================================================
    echo [SUCCESS] Your project has been successfully uploaded to GitHub!
    echo View it at: %REPO_URL%
    echo =========================================================================
) else (
    echo.
    echo =========================================================================
    echo [PUSH FAILED]
    echo Common reasons:
    echo 1. The repository does not exist yet at: %REPO_URL%
    echo    -> Create it at: https://github.com/new
    echo 2. Check your GitHub username / URL spelling.
    echo 3. Permission denied -> Make sure you are signed into the correct account.
    echo =========================================================================
)

echo.
pause
