# Airflow Movie Recommendation System - Codespaces Setup

> **Platform**: This project is optimized for **GitHub Codespaces (Ubuntu)** where Airflow runs natively with full features.

---

## Quick Start (3 Steps)

1. **Launch Codespace**
   - Go to https://github.com/Rajdeep4050/movie-recommendation
   - Click "Code" → "Codespaces" → "Create codespace on main"
   - Wait 2-3 minutes for automatic environment setup

2. **Configure Credentials**
   ```bash
   cp .env.example .env
   # Edit .env and add your Kaggle credentials
   # Get from: https://www.kaggle.com/settings → API → Create New Token
   ```

3. **Start Everything**
   ```bash
   bash deployment/codespaces/start_codespaces.sh
   # Airflow UI: Port 8080 → Login: admin/admin
   # Django App: Port 8000
   ```

---

## Full Airflow Features in Codespaces

Unlike Windows, Codespaces provides:
- ✅ Native Airflow webserver (no workarounds)
- ✅ Airflow scheduler running natively
- ✅ Full task orchestration with 10-task DAG
- ✅ Complete UI access with visual pipeline monitoring
- ✅ Production-grade deployment

## Why Codespaces?

- ✅ **Full Linux Environment** - Airflow runs natively (no Windows limitations)
- ✅ **Free Tier** - 60 hours/month free for personal accounts
- ✅ **Pre-configured** - Everything installs automatically via `.devcontainer`
- ✅ **Cloud-based** - Access from anywhere with browser
- ✅ **No Local Setup** - No need to install Python, Git, or dependencies locally

---

## Detailed Setup Instructions

### Step 1: Open in Codespaces

1. Go to your repository: https://github.com/Rajdeep4050/movie-recommendation
2. Click the **Code** button (green button)
3. Click **Codespaces** tab
4. Click **Create codespace on main**

**Wait 2-3 minutes** for the environment to set up automatically.

---

## Step 2: Configure Kaggle Credentials

Once Codespaces opens, create a `.env` file:

```bash
# Create .env file
cat > .env << 'EOF'
# Kaggle API Credentials
KAGGLE_USERNAME=rajdeep4050
KAGGLE_KEY=your_kaggle_api_key_here

# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production-12345
ALLOWED_HOSTS=localhost,127.0.0.1,*.github.dev

# Model Configuration
MODEL_DIR=./training/models
EOF
```

**Replace `your_kaggle_api_key_here`** with your actual Kaggle API key.

---

## Step 3: Start Airflow (Option A - All-in-One)

Run the automated startup script:

```bash
chmod +x start_codespaces.sh
./start_codespaces.sh
```

**This will:**
- Initialize Airflow database
- Create admin user (username: `admin`, password: `admin`)
- Run Django migrations
- Start Airflow webserver + scheduler

**Airflow UI**: Click the **Ports** tab → Find port `8080` → Click globe icon
**Login**: Username: `admin` | Password: `admin`

---

## Step 4: Start Django (In New Terminal)

Open a **new terminal** (while Airflow is running):

```bash
python manage.py runserver 0.0.0.0:8000
```

**Django App**: Click **Ports** tab → Find port `8000` → Click globe icon

---

## Option B: Manual Step-by-Step Setup

If you prefer manual control:

### 1. Set Airflow Home
```bash
export AIRFLOW_HOME=$(pwd)/airflow
```

### 2. Initialize Airflow
```bash
airflow db init
```

### 3. Create Admin User
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 4. Start Airflow Webserver (Terminal 1)
```bash
airflow webserver --port 8080
```

### 5. Start Airflow Scheduler (Terminal 2)
```bash
airflow scheduler
```

### 6. Start Django (Terminal 3)
```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

---

## Step 5: Access the Applications

### Airflow UI
1. Click **Ports** tab at bottom of VS Code
2. Find port **8080** (Airflow UI)
3. Click the **globe icon** to open
4. Login: `admin` / `admin`

### Django Application
1. Click **Ports** tab
2. Find port **8000** (Django App)
3. Click the **globe icon** to open
4. Start searching for movies!

---

## Step 6: Trigger Airflow DAG

In the Airflow UI:

1. Find DAG: `movie_recommender_retraining`
2. Toggle it **ON** (unpause)
3. Click **Trigger DAG** (play button)
4. Watch the pipeline execute:
   - check_kaggle_credentials
   - download_dataset
   - validate_dataset
   - backup_current_model
   - train_model
   - evaluate_model
   - deploy_model
   - send_notification
   - cleanup_old_backups
   - restart_django_server

---

## Quick Commands Reference

### Airflow Commands
```bash
# List all DAGs
airflow dags list

# Trigger DAG manually
airflow dags trigger movie_recommender_retraining

# View DAG runs
airflow dags list-runs -d movie_recommender_retraining

# Test individual task
airflow tasks test movie_recommender_retraining check_kaggle_credentials 2024-01-01
```

### Django Commands
```bash
# Start server
python manage.py runserver 0.0.0.0:8000

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## Troubleshooting

### Port Not Showing?
```bash
# Check if service is running
ps aux | grep -E "(airflow|python)"

# Check ports
lsof -i :8080  # Airflow
lsof -i :8000  # Django
```

### Airflow Database Issues?
```bash
# Reset database
rm airflow/airflow.db
airflow db init
```

### Models Not Found?
```bash
# Train models (first time only)
python download_and_train.py
```

---

## Benefits of Codespaces

✅ **No Windows Limitations** - Full Airflow UI with webserver & scheduler  
✅ **Full Linux Environment** - All features work natively  
✅ **Automatic Setup** - Dependencies install automatically  
✅ **Port Forwarding** - Easy access to web interfaces  
✅ **Free Tier** - 60 hours/month for personal accounts  
✅ **Persistent Storage** - Your work is saved  
✅ **Cloud Access** - Work from any device  

---

## Cost Optimization

**Free Tier (60 hours/month):**
- Stop Codespace when not in use
- Default timeout: 30 minutes of inactivity
- Manual stop: Codespaces menu → Stop codespace

**Pricing after free tier:**
- 2-core: $0.18/hour
- 4-core: $0.36/hour

**Tip:** Use 2-core for development, 4-core only for heavy model training.

---

## Next Steps

1. ✅ Open Codespace
2. ✅ Configure .env file
3. ✅ Run start_codespaces.sh
4. ✅ Access Airflow UI (port 8080)
5. ✅ Access Django App (port 8000)
6. ✅ Trigger DAG and watch pipeline execute

**Your movie recommendation system with full Airflow MLOps is ready!** 🎉
