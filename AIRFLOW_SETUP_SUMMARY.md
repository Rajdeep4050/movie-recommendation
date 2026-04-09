# Apache Airflow Integration - Setup Summary

## What Was Added

### 1. **Core Airflow Files**

#### `airflow/dags/movie_recommender_retrain_dag.py`
**Main retraining DAG** - 9-task automated pipeline
- Downloads latest TMDB dataset from Kaggle
- Validates data quality (100K+ movies, required columns)
- Backs up current production model
- Trains new model (26K movies, ~15 minutes)
- Evaluates model performance (sparsity, similarity checks)
- Deploys model if quality thresholds pass
- Sends completion notification
- Cleans up old backups (keeps last 5)

**Schedule:** Every Sunday at 2:00 AM

#### `airflow/airflow.cfg`
Airflow configuration file with:
- SQLite database for metadata
- SequentialExecutor for task execution
- Log directory configuration
- Web server settings (port 8080)
- Scheduler settings

#### `airflow/README.md`
Comprehensive documentation covering:
- Installation and setup
- Using the DAG
- Monitoring and debugging
- Production deployment
- Troubleshooting
- Interview talking points

#### `airflow/init_airflow.sh` & `airflow/init_airflow.bat`
Quick initialization scripts for:
- Setting up Airflow database
- Creating admin user
- Verifying DAG installation
- Platform-specific (Linux/Windows)

### 2. **Updated Files**

#### `requirements.txt`
Added: `apache-airflow==2.10.4`

#### `README.md`
- Added Airflow to Key Technologies
- New section: "Apache Airflow - MLOps Pipeline"
- Updated Table of Contents
- Quick start guide for Airflow

#### `rajdeep.md` (Technical Documentation)
- Added Airflow to core components
- Tech stack justification for Airflow
- Code structure section for DAG
- New interview Q&A about Airflow (Q9, Q10, Q11)
- Updated project achievements
- Added to potential improvements

## Directory Structure

```
airflow/
├── dags/
│   └── movie_recommender_retrain_dag.py  # Main DAG
├── logs/                                   # Execution logs (auto-created)
├── plugins/                                # Custom plugins
├── backups/                                # Model backups (auto-created)
├── airflow.cfg                             # Configuration
├── airflow.db                              # Metadata DB (created on init)
├── init_airflow.sh                         # Linux/Mac setup script
├── init_airflow.bat                        # Windows setup script
└── README.md                               # Comprehensive guide
```

## Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
cd airflow
chmod +x init_airflow.sh
./init_airflow.sh
```

**Windows:**
```cmd
cd airflow
init_airflow.bat
```

### Option 2: Manual Setup

```bash
# 1. Set Airflow home
export AIRFLOW_HOME=$(pwd)/airflow

# 2. Initialize database
airflow db init

# 3. Create user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# 4. Start Airflow
airflow standalone
```

### Access Airflow UI

Open browser: **http://localhost:8080**
- Username: `admin`
- Password: `admin`

## DAG Features

### Task Dependencies

```
check_kaggle_credentials
    ↓
download_dataset (2-5 min)
    ↓
validate_dataset (30s)
    ↓
backup_current_model (1 min)
    ↓
train_model (15-20 min)
    ↓
evaluate_model (30s)
    ↓
deploy_model (5s)
    ↓
send_notification + restart_django_server (5s each)
    ↓
cleanup_old_backups (10s)
```

**Total Duration:** ~20-30 minutes

### Quality Checks

**Data Validation:**
- ✅ Dataset has 100K+ movies
- ✅ Required columns present (title, genres, vote_count)
- ✅ Less than 100 null titles
- ✅ 50K+ movies with votes

**Model Evaluation:**
- ✅ Model has 20K+ movies
- ✅ Similarity matrix is 95%+ sparse
- ✅ Average similarity between 0.1 and 0.5

### Error Handling

- **Automatic Retries:** 2 retries with 5-minute delay
- **Execution Timeout:** 2 hours per task
- **Email Alerts:** On failure (configurable)
- **Backup System:** Previous model saved before new training

## Interview Talking Points

### Why Airflow?

1. **MLOps Best Practices**
   - Industry-standard workflow orchestration
   - Automated pipeline management
   - Production-ready deployment

2. **Reliability**
   - Automatic retries on failure
   - Health checks and monitoring
   - Task dependency management

3. **Observability**
   - Web UI for pipeline visualization
   - Detailed task logs
   - XCom for inter-task communication

4. **Scalability**
   - Easy to add new tasks
   - Parallel execution with CeleryExecutor
   - Kubernetes-ready for cloud deployment

### Key Features Demonstrated

- ✅ **DAG Design:** Sequential task flow with clear dependencies
- ✅ **Data Quality:** Validation checks before training
- ✅ **Error Handling:** Retries and error notifications
- ✅ **Versioning:** Automated backups with timestamp
- ✅ **Monitoring:** Airflow UI for execution tracking
- ✅ **Production-Ready:** Configurable for SMTP, Slack, etc.

## What This Shows to Employers

1. **MLOps Knowledge**
   - Understanding of ML lifecycle management
   - Automated retraining pipelines
   - Model versioning and deployment

2. **Production Thinking**
   - Automated workflows (no manual intervention)
   - Quality checks and validation
   - Backup and rollback capabilities

3. **Modern Tech Stack**
   - Apache Airflow (industry standard)
   - Python-based orchestration
   - Scalable architecture

4. **Best Practices**
   - Separation of concerns (DAG vs training code)
   - Configuration management
   - Comprehensive documentation

## Next Steps

### Test the Pipeline

1. **Trigger Manual Run:**
   ```bash
   airflow dags trigger movie_recommender_retraining
   ```

2. **Monitor Execution:**
   - Watch progress in Airflow UI
   - Check logs for each task
   - Verify model files created

3. **Verify Results:**
   - Check `training/models/` for new files
   - Review `deployment_info.json` for metrics
   - Check `airflow/backups/` for old model

### Production Deployment

For production, consider:

1. **Use PostgreSQL** instead of SQLite
2. **Use CeleryExecutor** for parallel execution
3. **Deploy on Kubernetes** for scalability
4. **Configure SMTP** for email notifications
5. **Set up Slack** for real-time alerts
6. **Use Redis** as message broker
7. **Enable remote logging** (S3/GCS)

See [airflow/README.md](airflow/README.md) for detailed production setup.

## Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DAG Writing Guide](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dags.html)
- [MLOps with Airflow](https://airflow.apache.org/use-cases/machine-learning/)

---

**Note:** This implementation demonstrates MLOps principles and makes your project significantly more impressive for job applications and interviews!
