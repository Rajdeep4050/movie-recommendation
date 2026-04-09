# Apache Airflow Integration - Movie Recommendation System

## Overview

This directory contains Apache Airflow configuration for **automated ML pipeline orchestration**. The main DAG (`movie_recommender_retrain_dag.py`) automates the entire model retraining workflow on a weekly schedule.

## What Does Airflow Do Here?

**Automated Weekly Retraining Pipeline:**
1. ✅ Downloads latest TMDB dataset from Kaggle
2. ✅ Validates data quality (checks for required columns, sufficient data)
3. ✅ Backs up current production model
4. ✅ Trains new recommendation model
5. ✅ Evaluates model performance
6. ✅ Deploys if quality checks pass
7. ✅ Sends completion notification
8. ✅ Cleans up old backups (keeps last 5)

**Schedule:** Every Sunday at 2:00 AM

## Project Structure

```
airflow/
├── dags/
│   └── movie_recommender_retrain_dag.py  # Main retraining DAG
├── logs/                                   # Airflow execution logs
├── plugins/                                # Custom Airflow plugins
├── backups/                                # Model backups (auto-created)
├── airflow.cfg                             # Airflow configuration
└── README.md                               # This file
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- Apache Airflow installed (see main README)
- Kaggle API credentials configured in `.env`

### Step 1: Initialize Airflow Database

```bash
# Set Airflow home directory
export AIRFLOW_HOME=$(pwd)/airflow

# Initialize the database
airflow db init
```

### Step 2: Create Airflow User

```bash
# Create admin user for web interface
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### Step 3: Start Airflow Services

**Option A: Start Web Server + Scheduler (2 terminals)**

Terminal 1 - Web Server:
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver --port 8080
```

Terminal 2 - Scheduler:
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

**Option B: Start Standalone (Single Command)**
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow standalone
```

### Step 4: Access Airflow UI

Open browser: http://localhost:8080

- Username: `admin`
- Password: `admin` (or what you set)

## Using the DAG

### View DAG in UI

1. Go to http://localhost:8080
2. Find DAG: `movie_recommender_retraining`
3. Click to view details

### Trigger Manual Run

**Via UI:**
- Click on DAG name
- Click "Trigger DAG" button (play icon)

**Via CLI:**
```bash
airflow dags trigger movie_recommender_retraining
```

### Monitor DAG Execution

**Via UI:**
- Click on DAG run to see task status
- Green = Success, Red = Failed, Yellow = Running

**Via CLI:**
```bash
# List DAG runs
airflow dags list-runs -d movie_recommender_retraining

# Check task status
airflow tasks test movie_recommender_retraining train_model 2024-01-01
```

### View Logs

**Via UI:**
- Click on task instance
- Click "Log" button

**Via CLI:**
```bash
tail -f airflow/logs/dag_id=movie_recommender_retraining/*/task_id=train_model/*.log
```

## DAG Task Breakdown

### Task Graph Flow

```
check_kaggle_credentials
    ↓
download_dataset
    ↓
validate_dataset
    ↓
backup_current_model
    ↓
train_model (15-20 minutes)
    ↓
evaluate_model
    ↓
deploy_model
    ↓
send_notification + restart_django_server
    ↓
cleanup_old_backups
```

### Task Details

| Task | Duration | Description |
|------|----------|-------------|
| `check_kaggle_credentials` | 1s | Verifies Kaggle API credentials |
| `download_dataset` | 2-5 min | Downloads TMDB dataset (~240 MB) |
| `validate_dataset` | 30s | Quality checks on data |
| `backup_current_model` | 1 min | Backs up production model |
| `train_model` | 15-20 min | Trains new model (26K movies) |
| `evaluate_model` | 30s | Validates model performance |
| `deploy_model` | 5s | Marks model as production-ready |
| `send_notification` | 5s | Sends completion alert |
| `restart_django_server` | 5s | Reminder to restart server |
| `cleanup_old_backups` | 10s | Removes old backups |

**Total Pipeline Duration:** ~20-30 minutes

## Configuration

### Modify Schedule

Edit `movie_recommender_retrain_dag.py`:

```python
schedule_interval='0 2 * * 0',  # Cron format: Min Hour Day Month DayOfWeek
```

Common schedules:
- Daily: `'0 2 * * *'` (2 AM every day)
- Weekly: `'0 2 * * 0'` (2 AM every Sunday)
- Monthly: `'0 2 1 * *'` (2 AM on 1st of month)
- Hourly: `'0 * * * *'` (Every hour)

### Adjust Training Parameters

Edit the `train_model` function in the DAG:

```python
trainer.train(
    dataset_path,
    quality_threshold='medium',  # low/medium/high
    max_movies=50000             # Adjust based on resources
)
```

### Enable Email Notifications

1. Edit `airflow.cfg`:
```ini
[smtp]
smtp_host = smtp.gmail.com
smtp_user = your-email@gmail.com
smtp_password = your-app-password
smtp_port = 587
smtp_mail_from = airflow@example.com
```

2. Update DAG default_args:
```python
'email': ['your-email@example.com'],
'email_on_failure': True,
```

## Production Deployment

### Best Practices

1. **Use Linux/WSL2**: Airflow works best on POSIX systems
2. **Use CeleryExecutor**: For parallel task execution
3. **Use PostgreSQL**: Instead of SQLite for metadata DB
4. **Use Redis**: For message queue (Celery backend)
5. **Enable Remote Logging**: Store logs in S3/GCS
6. **Set up Monitoring**: Use Prometheus + Grafana

### Example Production Setup

```bash
# Install with PostgreSQL and Celery
pip install "apache-airflow[postgres,celery,redis]==2.10.4"

# Update airflow.cfg
executor = CeleryExecutor
sql_alchemy_conn = postgresql+psycopg2://user:pass@localhost/airflow
broker_url = redis://localhost:6379/0
result_backend = db+postgresql://user:pass@localhost/airflow

# Start workers
airflow celery worker
```

## Troubleshooting

### DAG Not Appearing in UI

**Check:**
```bash
# List all DAGs
airflow dags list

# Parse DAG file
airflow dags list-import-errors
```

**Fix:** Check Python syntax errors in DAG file

### Task Failing

**Check logs:**
```bash
# Via CLI
airflow tasks test movie_recommender_retraining task_name 2024-01-01

# Via UI
DAG → Task → Log button
```

### Training Takes Too Long

**Reduce dataset size:**
```python
max_movies=10000  # Instead of 50000
```

### Kaggle Download Fails

**Check:**
- `.env` file has correct credentials
- Internet connection is working
- Kaggle API key is not expired

## Advanced Features

### Add Slack Notifications

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

task_slack_notify = SlackWebhookOperator(
    task_id='slack_notification',
    http_conn_id='slack_webhook',
    message='Model retraining completed!',
    dag=dag
)
```

### Add Data Quality Checks

```python
from airflow.operators.python import BranchPythonOperator

def check_data_quality(**context):
    metrics = context['ti'].xcom_pull(key='validation_results')
    if metrics['total_movies'] < 100000:
        return 'send_alert_task'
    return 'continue_pipeline_task'

task_branch = BranchPythonOperator(
    task_id='check_quality',
    python_callable=check_data_quality,
    dag=dag
)
```

### Model A/B Testing

Add task to deploy to staging first, run A/B test, then promote to production.

## Benefits of Airflow Integration

✅ **Automation** - No manual intervention needed for retraining  
✅ **Reliability** - Automatic retries on failure  
✅ **Monitoring** - Track pipeline execution via UI  
✅ **Versioning** - Automatic model backups  
✅ **Scalability** - Easy to add more tasks/checks  
✅ **Observability** - Detailed logs for debugging  
✅ **Scheduling** - Run at optimal times (low traffic)  
✅ **MLOps** - Production-ready ML pipeline management  

## Interview Talking Points

When discussing this project:

1. **"I implemented Apache Airflow for automated ML pipeline orchestration"**
   - Shows MLOps knowledge
   - Demonstrates production thinking

2. **"Weekly automated retraining ensures model stays fresh with latest movie data"**
   - Addresses data drift
   - Production ML lifecycle

3. **"DAG includes data validation, model evaluation, and automated rollback"**
   - Quality assurance
   - Risk mitigation

4. **"Implemented backup system and cleanup for model versioning"**
   - Data governance
   - Storage optimization

5. **"Pipeline can be monitored via Airflow UI with detailed task logs"**
   - Observability
   - Debugging capability

## References

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DAG Writing Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/best-practices.html)

---

**Note:** For Windows users, consider using WSL2 or Docker for better Airflow compatibility in production.
