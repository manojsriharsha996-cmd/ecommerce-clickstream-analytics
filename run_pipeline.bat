@echo off
title Run Clickstream Big Data Pipeline
echo =========================================================================
echo   Executing Clickstream Big Data Processing Pipeline...
echo   Student: KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
echo =========================================================================
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe run_pipeline.py
) else (
    python run_pipeline.py
)
pause
