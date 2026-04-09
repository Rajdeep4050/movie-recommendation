@echo off
REM Airflow Initialization Script for Movie Recommendation System (Windows)
REM This script sets up Airflow for the first time

echo ==========================================
echo   Airflow Setup - Movie Recommender
echo ==========================================

REM Set Airflow home to current airflow directory
set AIRFLOW_HOME=%CD%
echo.
echo AIRFLOW_HOME set to: %AIRFLOW_HOME%

REM Initialize Airflow database
echo.
echo [1/3] Initializing Airflow database...
airflow db init

REM Create admin user
echo.
echo [2/3] Creating admin user...
airflow users create ^
    --username admin ^
    --firstname Admin ^
    --lastname User ^
    --role Admin ^
    --email admin@example.com ^
    --password admin

REM List DAGs to verify setup
echo.
echo [3/3] Verifying DAG installation...
airflow dags list | findstr movie_recommender

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo To start Airflow:
echo   1. Set environment: set AIRFLOW_HOME=%CD%
echo   2. Start standalone: airflow standalone
echo.
echo Access Airflow UI: http://localhost:8080
echo   Username: admin
echo   Password: admin
echo.
echo Note: Airflow works best on Linux/WSL2
echo For Windows, consider using WSL2 or Docker
echo.
pause
