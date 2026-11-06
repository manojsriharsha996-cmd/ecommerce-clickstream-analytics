@echo off
title Run Pipeline Test Suite
echo =========================================================================
echo   Executing Clickstream Pipeline Unit & Integration Tests...
echo   Student: KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
echo =========================================================================
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
) else (
    python -m unittest discover -s tests -p "test_*.py" -v
)
echo.
echo =========================================================================
pause
