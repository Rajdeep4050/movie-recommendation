#!/bin/bash
# Airflow Initialization Script for Movie Recommendation System
# This script sets up Airflow for the first time

echo "=========================================="
echo "  Airflow Setup - Movie Recommender"
echo "=========================================="

# Set Airflow home to current airflow directory
export AIRFLOW_HOME=$(pwd)

echo "✓ AIRFLOW_HOME set to: $AIRFLOW_HOME"

# Initialize Airflow database
echo ""
echo "[1/3] Initializing Airflow database..."
airflow db init

# Create admin user
echo ""
echo "[2/3] Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# List DAGs to verify setup
echo ""
echo "[3/3] Verifying DAG installation..."
airflow dags list | grep movie_recommender

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To start Airflow:"
echo "  1. Set environment: export AIRFLOW_HOME=$(pwd)"
echo "  2. Start webserver: airflow webserver --port 8080"
echo "  3. Start scheduler: airflow scheduler (in new terminal)"
echo ""
echo "Or use standalone mode:"
echo "  airflow standalone"
echo ""
echo "Access Airflow UI: http://localhost:8080"
echo "  Username: admin"
echo "  Password: admin"
echo ""
