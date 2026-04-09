# Utility Scripts

This folder contains utility scripts for setup, testing, and maintenance.

## Training & Setup

**`download_and_train.py`**
- Downloads TMDB dataset from Kaggle
- Trains the recommendation model
- Saves models to `training/models/`
- **Usage:** `python scripts/download_and_train.py`
- **Time:** 10-15 minutes
- **Requirements:** Kaggle credentials in `.env` file

## Airflow Testing

**`test_airflow_dag.py`**
- Tests Airflow DAG integration without full webserver
- Validates DAG structure, dependencies, and credentials
- Runs sample tasks to verify functionality
- **Usage:** `python scripts/test_airflow_dag.py`
- **Time:** 5 seconds
- **Windows Compatible:** ✅ Yes

**`run_airflow_pipeline_manually.py`**
- Interactive pipeline demonstration
- Three modes: Quick Test, Light Run, Full Pipeline
- Shows how tasks execute and communicate
- **Usage:** `python scripts/run_airflow_pipeline_manually.py`
- **Time:** 5 seconds to 30 minutes (depending on mode)
- **Windows Compatible:** ✅ Yes

## Usage Examples

### Initial Setup
```bash
# 1. Setup environment and train models
python scripts/download_and_train.py
```

### Verify Airflow Integration
```bash
# 2. Quick verification (Windows compatible)
python scripts/test_airflow_dag.py

# 3. Interactive demo
python scripts/run_airflow_pipeline_manually.py
```

### Django Application
```bash
# 4. Run the web application
python manage.py migrate
python manage.py runserver
```

## Notes

- All scripts should be run from the **project root directory**
- Ensure virtual environment is activated before running scripts
- Kaggle credentials required for `download_and_train.py`
