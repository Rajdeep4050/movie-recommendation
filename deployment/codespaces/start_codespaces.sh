#!/bin/bash

echo "========================================="
echo "Movie Recommendation System - Codespaces"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Set Airflow home
export AIRFLOW_HOME=$(pwd)/airflow

# Check if .env exists (in project root)
if [ ! -f ../../.env ]; then
    echo "Creating .env file..."
    echo "Please add your Kaggle credentials in project root:"
    echo ""
    echo "KAGGLE_USERNAME=your_username"
    echo "KAGGLE_KEY=your_api_key"
    echo ""
    echo "# Create .env file by running from project root:"
    echo "# cp .env.example .env"
    exit 1
fi

echo -e "${GREEN}[1/5]${NC} Initializing Airflow database..."
airflow db init

echo ""
echo -e "${GREEN}[2/5]${NC} Creating Airflow admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

echo ""
echo -e "${GREEN}[3/5]${NC} Running Django migrations..."
python manage.py migrate

echo ""
echo -e "${GREEN}[4/5]${NC} Starting Airflow in standalone mode..."
echo -e "${BLUE}Airflow UI will be available on port 8080${NC}"
echo -e "${BLUE}Username: admin | Password: admin${NC}"
echo ""
echo -e "${GREEN}[5/5]${NC} To start Django separately, run:"
echo -e "${BLUE}python manage.py runserver 0.0.0.0:8000${NC}"
echo ""
echo "========================================="
echo "Starting Airflow..."
echo "========================================="

airflow standalone
