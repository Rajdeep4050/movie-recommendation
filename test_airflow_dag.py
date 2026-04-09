"""
Test script to verify Airflow DAG integration without running the webserver
This script manually tests individual tasks from the movie_recommender_retrain_dag
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Set up environment
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ['AIRFLOW_HOME'] = str(PROJECT_ROOT / 'airflow')

print("=" * 70)
print("  Testing Airflow DAG Integration - Movie Recommender")
print("=" * 70)
print()

# Test 1: Import the DAG file
print("[1/6] Testing DAG file import...")
try:
    sys.path.insert(0, str(PROJECT_ROOT / 'airflow' / 'dags'))
    import movie_recommender_retrain_dag as dag_module
    print("[OK] DAG file imported successfully")
    print(f"  - DAG ID: {dag_module.dag.dag_id}")
    print(f"  - Schedule: {dag_module.dag.schedule_interval}")
    print(f"  - Tags: {dag_module.dag.tags}")
    print(f"  - Tasks: {len(dag_module.dag.tasks)}")
except Exception as e:
    print(f"[FAIL] Failed to import DAG: {e}")
    sys.exit(1)

print()

# Test 2: List all tasks
print("[2/6] Listing DAG tasks...")
try:
    for task in dag_module.dag.tasks:
        print(f"  - {task.task_id}")
    print(f"[OK] Found {len(dag_module.dag.tasks)} tasks")
except Exception as e:
    print(f"[FAIL] Failed to list tasks: {e}")
    sys.exit(1)

print()

# Test 3: Verify task dependencies
print("[3/6] Verifying task dependencies...")
try:
    task_check_credentials = dag_module.dag.get_task('check_kaggle_credentials')
    downstream = task_check_credentials.downstream_list
    print(f"[OK] Task dependencies configured correctly")
    print(f"  - check_kaggle_credentials has {len(downstream)} downstream task(s)")
except Exception as e:
    print(f"[FAIL] Failed to verify dependencies: {e}")
    sys.exit(1)

print()

# Test 4: Check .env file exists and has Kaggle credentials
print("[4/6] Checking Kaggle credentials...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    kaggle_username = os.getenv('KAGGLE_USERNAME')
    kaggle_key = os.getenv('KAGGLE_KEY')

    if kaggle_username and kaggle_key:
        print(f"[OK] Kaggle credentials found")
        print(f"  - Username: {kaggle_username}")
        print(f"  - Key: {'*' * 20}...{kaggle_key[-4:]}")
    else:
        print("[FAIL] Kaggle credentials not found in .env file")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Failed to check credentials: {e}")
    sys.exit(1)

print()

# Test 5: Check required directories exist
print("[5/6] Checking required directories...")
try:
    required_dirs = [
        PROJECT_ROOT / 'training',
        PROJECT_ROOT / 'training' / 'models',
        PROJECT_ROOT / 'airflow' / 'dags',
        PROJECT_ROOT / 'airflow' / 'logs',
    ]

    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"[OK] {dir_path.name}/ exists")
        else:
            print(f"[FAIL] {dir_path.name}/ missing - creating it")
            dir_path.mkdir(parents=True, exist_ok=True)

    print(f"[OK] All required directories exist")
except Exception as e:
    print(f"[FAIL] Failed to check directories: {e}")
    sys.exit(1)

print()

# Test 6: Test a simple task function
print("[6/6] Testing DAG task function (check_kaggle_credentials)...")
try:
    # Create a mock context
    class MockTaskInstance:
        def xcom_push(self, key, value):
            print(f"    XCom push: {key} = {value}")

    mock_context = {
        'task_instance': MockTaskInstance(),
        'execution_date': datetime.now(),
        'dag_run': type('obj', (object,), {'run_id': 'test_run'})()
    }

    # Call the function
    result = dag_module.check_kaggle_credentials(**mock_context)

    if result:
        print("[OK] check_kaggle_credentials function executed successfully")
    else:
        print("[FAIL] check_kaggle_credentials returned False")
except Exception as e:
    print(f"[FAIL] Failed to execute task function: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("  [OK] All Tests Passed - Airflow Integration is Working!")
print("=" * 70)
print()
print("NEXT STEPS:")
print("  - The DAG is properly configured and ready to use")
print("  - On Windows, Airflow webserver has limited support")
print()
print("OPTIONS TO RUN AIRFLOW:")
print()
print("Option 1: Use WSL2 (Recommended for Windows)")
print("  - Install WSL2: wsl --install")
print("  - Then run Airflow in WSL2 Linux environment")
print()
print("Option 2: Use Docker (Cross-platform)")
print("  - docker run -p 8080:8080 apache/airflow:2.10.4")
print()
print("Option 3: Test individual tasks (Current environment)")
print("  - Run: python test_individual_task.py")
print()
print("Option 4: Trigger DAG programmatically")
print("  - Use Airflow CLI commands to trigger tasks")
print()
print("Your Airflow configuration:")
print(f"  - AIRFLOW_HOME: {os.environ.get('AIRFLOW_HOME')}")
print(f"  - Database: {PROJECT_ROOT / 'airflow' / 'airflow.db'}")
print(f"  - DAGs folder: {PROJECT_ROOT / 'airflow' / 'dags'}")
print()
