"""
Movie Recommendation System - Automated Retraining Pipeline
This DAG automates the entire ML pipeline:
1. Downloads latest TMDB dataset from Kaggle
2. Validates data quality
3. Trains new recommendation model
4. Evaluates model performance
5. Deploys model if performance is acceptable
6. Backs up old model
7. Sends completion notification

Schedule: Weekly (every Sunday at 2 AM)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os
import sys
import json
import shutil
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Default arguments for the DAG
default_args = {
    'owner': 'rajdeep',
    'depends_on_past': False,
    'email': ['your-email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'movie_recommender_retraining',
    default_args=default_args,
    description='Automated weekly retraining of movie recommendation model',
    schedule_interval='0 2 * * 0',  # Every Sunday at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'recommendation', 'training', 'scheduled'],
)


def check_kaggle_credentials(**context):
    """
    Task 1: Verify Kaggle API credentials are available
    """
    from dotenv import load_dotenv

    load_dotenv()
    kaggle_username = os.getenv('KAGGLE_USERNAME')
    kaggle_key = os.getenv('KAGGLE_KEY')

    if not kaggle_username or not kaggle_key:
        raise ValueError("Kaggle credentials not found in .env file")

    print(f"[OK] Kaggle credentials verified for user: {kaggle_username}")

    # Push credentials to XCom for downstream tasks
    context['task_instance'].xcom_push(key='kaggle_username', value=kaggle_username)
    return True


def download_dataset(**context):
    """
    Task 2: Download latest TMDB dataset from Kaggle (with caching)
    """
    import kagglehub
    from dotenv import load_dotenv
    import json
    from datetime import datetime, timedelta
    import shutil

    load_dotenv()
    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

    # Cache configuration
    CACHE_DIR = PROJECT_ROOT / "datasets" / "kaggle" / "tmdb-movies"
    CACHE_METADATA = CACHE_DIR / ".cache_metadata.json"
    CACHE_TTL_DAYS = 30

    # Check cache validity
    if CACHE_METADATA.exists():
        with open(CACHE_METADATA, 'r') as f:
            metadata = json.load(f)
            cache_date = datetime.fromisoformat(metadata['downloaded_at'])
            cache_age = datetime.now() - cache_date

            if cache_age < timedelta(days=CACHE_TTL_DAYS):
                csv_path = metadata['csv_path']
                if Path(csv_path).exists():
                    print(f"[CACHE HIT] Using cached dataset from {cache_date.strftime('%Y-%m-%d')}")
                    print(f"Cache age: {cache_age.days} days (TTL: {CACHE_TTL_DAYS} days)")
                    context['task_instance'].xcom_push(key='dataset_path', value=csv_path)
                    return csv_path

    print("[CACHE MISS] Downloading fresh dataset from Kaggle...")
    dataset_path = kagglehub.dataset_download("asaniczka/tmdb-movies-dataset-2023-930k-movies")

    # Find CSV file
    csv_files = list(Path(dataset_path).glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV file found in downloaded dataset")

    csv_path = str(csv_files[0])

    # Copy to cache directory
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached_csv = CACHE_DIR / Path(csv_path).name
    shutil.copy2(csv_path, cached_csv)

    # Save metadata
    metadata = {
        'downloaded_at': datetime.now().isoformat(),
        'csv_path': str(cached_csv),
        'original_path': dataset_path,
        'dataset_id': 'asaniczka/tmdb-movies-dataset-2023-930k-movies'
    }
    with open(CACHE_METADATA, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"[OK] Dataset cached: {cached_csv}")
    context['task_instance'].xcom_push(key='dataset_path', value=str(cached_csv))
    return str(cached_csv)


def validate_dataset(**context):
    """
    Task 3: Validate dataset quality before training
    """
    import pandas as pd

    dataset_path = context['task_instance'].xcom_pull(task_ids='download_dataset', key='dataset_path')

    print(f"Validating dataset: {dataset_path}")
    df = pd.read_csv(dataset_path, low_memory=False)

    # Quality checks
    checks = {
        'total_movies': len(df),
        'required_columns': ['title', 'genres', 'vote_average', 'vote_count'],
        'null_titles': df['title'].isnull().sum(),
        'movies_with_votes': len(df[df['vote_count'] > 0]),
    }

    # Validation rules
    assert checks['total_movies'] > 100000, f"Dataset too small: {checks['total_movies']} movies"
    assert all(col in df.columns for col in checks['required_columns']), "Missing required columns"
    assert checks['null_titles'] < 100, f"Too many null titles: {checks['null_titles']}"
    assert checks['movies_with_votes'] > 50000, "Insufficient movies with votes"

    print("[OK] Dataset validation passed")
    print(f"  - Total movies: {checks['total_movies']:,}")
    print(f"  - Movies with votes: {checks['movies_with_votes']:,}")

    # Push validation results
    context['task_instance'].xcom_push(key='validation_results', value=checks)
    return True


def backup_current_model(**context):
    """
    Task 4: Backup current production model
    """
    import time

    model_dir = PROJECT_ROOT / 'training' / 'models'
    backup_dir = PROJECT_ROOT / 'airflow' / 'backups' / f"model_backup_{int(time.time())}"

    if model_dir.exists() and any(model_dir.iterdir()):
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copy all model files
        for file in model_dir.iterdir():
            if file.is_file():
                shutil.copy2(file, backup_dir / file.name)

        print(f"[OK] Current model backed up to: {backup_dir}")
        context['task_instance'].xcom_push(key='backup_path', value=str(backup_dir))
    else:
        print("No existing model to backup")

    return True


def train_model(**context):
    """
    Task 5: Train new recommendation model
    """
    sys.path.insert(0, str(PROJECT_ROOT / 'training'))
    from train import MovieRecommenderTrainer

    dataset_path = context['task_instance'].xcom_pull(task_ids='download_dataset', key='dataset_path')
    output_dir = PROJECT_ROOT / 'training' / 'models'

    print("Starting model training...")
    print(f"  - Dataset: {dataset_path}")
    print(f"  - Output: {output_dir}")

    # Initialize trainer
    trainer = MovieRecommenderTrainer(
        output_dir=str(output_dir),
        use_dimensionality_reduction=True,
        n_components=500
    )

    # Train model
    df, sim_matrix = trainer.train(
        dataset_path,
        quality_threshold='medium',  # 50+ votes
        max_movies=50000
    )

    # Training metrics
    metrics = {
        'movies_trained': len(df),
        'similarity_matrix_shape': sim_matrix.shape,
        'training_timestamp': datetime.now().isoformat(),
    }

    print(f"[OK] Model training completed")
    print(f"  - Movies: {len(df):,}")
    print(f"  - Matrix shape: {sim_matrix.shape}")

    # Push metrics
    context['task_instance'].xcom_push(key='training_metrics', value=metrics)
    return True


def evaluate_model(**context):
    """
    Task 6: Evaluate new model performance
    """
    import numpy as np
    from scipy.sparse import load_npz

    model_dir = PROJECT_ROOT / 'training' / 'models'

    # Load similarity matrix
    sim_matrix = load_npz(model_dir / 'similarity_matrix.npz')

    # Calculate evaluation metrics
    metrics = {
        'matrix_size_mb': (model_dir / 'similarity_matrix.npz').stat().st_size / (1024**2),
        'sparsity': 100 * (1 - sim_matrix.nnz / (sim_matrix.shape[0] * sim_matrix.shape[1])),
        'avg_similarity': sim_matrix.data.mean(),
        'num_movies': sim_matrix.shape[0],
    }

    # Quality thresholds
    assert metrics['num_movies'] >= 20000, "Too few movies in model"
    assert metrics['sparsity'] > 95, "Matrix not sparse enough"
    assert 0.1 < metrics['avg_similarity'] < 0.5, "Similarity values seem off"

    print("[OK] Model evaluation passed")
    print(f"  - Movies: {metrics['num_movies']:,}")
    print(f"  - Sparsity: {metrics['sparsity']:.2f}%")
    print(f"  - Avg similarity: {metrics['avg_similarity']:.4f}")

    context['task_instance'].xcom_push(key='evaluation_metrics', value=metrics)
    return True


def deploy_model(**context):
    """
    Task 7: Deploy new model (mark as production-ready)
    """
    model_dir = PROJECT_ROOT / 'training' / 'models'

    # Create deployment marker
    deployment_info = {
        'deployed_at': datetime.now().isoformat(),
        'deployed_by': 'airflow_dag',
        'dag_run_id': context['dag_run'].run_id,
        'training_metrics': context['task_instance'].xcom_pull(task_ids='train_model', key='training_metrics'),
        'evaluation_metrics': context['task_instance'].xcom_pull(task_ids='evaluate_model', key='evaluation_metrics'),
    }

    with open(model_dir / 'deployment_info.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print("[OK] Model deployed successfully")
    print(f"  - Deployment time: {deployment_info['deployed_at']}")
    print(f"  - Movies: {deployment_info['training_metrics']['movies_trained']:,}")

    return True


def send_notification(**context):
    """
    Task 8: Send completion notification (email/Slack/etc.)
    """
    training_metrics = context['task_instance'].xcom_pull(task_ids='train_model', key='training_metrics')
    evaluation_metrics = context['task_instance'].xcom_pull(task_ids='evaluate_model', key='evaluation_metrics')

    message = f"""
    [MOVIE] Movie Recommender Model Retraining Completed

    Status: SUCCESS [OK]
    Dag Run: {context['dag_run'].run_id}
    Execution Date: {context['execution_date']}

    Training Metrics:
    - Movies trained: {training_metrics['movies_trained']:,}
    - Matrix shape: {training_metrics['similarity_matrix_shape']}

    Evaluation Metrics:
    - Model size: {evaluation_metrics['matrix_size_mb']:.1f} MB
    - Sparsity: {evaluation_metrics['sparsity']:.2f}%
    - Avg similarity: {evaluation_metrics['avg_similarity']:.4f}

    Next Steps:
    - Restart Django server to load new model
    - Monitor application performance
    """

    print(message)
    print("[OK] Notification sent (simulated)")

    # In production, you would send via:
    # - Email (using EmailOperator)
    # - Slack (using SlackWebhookOperator)
    # - PagerDuty, etc.

    return True


def cleanup_old_backups(**context):
    """
    Task 9: Cleanup old model backups (keep last 5)
    """
    backup_base = PROJECT_ROOT / 'airflow' / 'backups'

    if not backup_base.exists():
        print("No backups directory found")
        return True

    # Get all backup directories
    backups = sorted([d for d in backup_base.iterdir() if d.is_dir()],
                     key=lambda x: x.stat().st_mtime, reverse=True)

    # Keep last 5, delete older ones
    for old_backup in backups[5:]:
        shutil.rmtree(old_backup)
        print(f"Deleted old backup: {old_backup.name}")

    print(f"[OK] Cleanup complete (kept {min(len(backups), 5)} recent backups)")
    return True


# Define task dependencies
task_check_credentials = PythonOperator(
    task_id='check_kaggle_credentials',
    python_callable=check_kaggle_credentials,
    dag=dag,
)

task_download = PythonOperator(
    task_id='download_dataset',
    python_callable=download_dataset,
    dag=dag,
)

task_validate = PythonOperator(
    task_id='validate_dataset',
    python_callable=validate_dataset,
    dag=dag,
)

task_backup = PythonOperator(
    task_id='backup_current_model',
    python_callable=backup_current_model,
    dag=dag,
)

task_train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

task_evaluate = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag,
)

task_deploy = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
)

task_notify = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag,
)

task_cleanup = PythonOperator(
    task_id='cleanup_old_backups',
    python_callable=cleanup_old_backups,
    dag=dag,
)

# Optional: Restart Django server (only if running in same environment)
task_restart_server = BashOperator(
    task_id='restart_django_server',
    bash_command='echo "Django server restart required - please restart manually"',
    dag=dag,
)

# Define task flow
task_check_credentials >> task_download >> task_validate >> task_backup >> task_train >> task_evaluate >> task_deploy >> [task_notify, task_restart_server] >> task_cleanup
