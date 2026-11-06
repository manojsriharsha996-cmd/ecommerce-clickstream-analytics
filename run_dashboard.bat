@echo off
title Launch Marketing-Conversion Dashboard
echo =========================================================================
echo   Starting E-Commerce Clickstream Analytics Dashboard...
echo   Student: KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
echo =========================================================================
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m streamlit run app/dashboard.py
) else (
    python -m streamlit run app/dashboard.py
)
pause
