# 🎬 Movie Recommendation System

> AI-powered movie recommendation system with Django and Apache Airflow MLOps pipeline

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://djangoproject.com/)
[![Airflow](https://img.shields.io/badge/Airflow-2.10.4-orange.svg)](https://airflow.apache.org/)
[![Platform](https://img.shields.io/badge/Platform-GitHub%20Codespaces-blue.svg)](https://github.com/features/codespaces)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Overview

Content-based movie recommendation system using TF-IDF and SVD for similarity matching. Features automated MLOps pipeline with Apache Airflow for weekly model retraining.

**Tech Stack:** Django 6.0, scikit-learn, pandas, Apache Airflow 2.10.4  
**Platform:** Optimized for GitHub Codespaces (Ubuntu)

---

## ✨ Features

- 🔍 Smart movie search with real-time autocomplete
- 🎬 AI recommendations (TF-IDF + SVD)
- 📊 Handles 10K-1M+ movies efficiently
- 🔄 Automated retraining pipeline (Airflow)
- 💾 Dataset caching (saves 960MB/month bandwidth)
- 📡 REST API endpoints
- ⚡ Sub-50ms recommendation generation

---

## 🚀 Quick Start (GitHub Codespaces)

### Prerequisites
- GitHub account
- Kaggle account (free) - [kaggle.com](https://www.kaggle.com)

### Setup (15-20 minutes)

**1. Launch Codespace**
- Go to: [github.com/Rajdeep4050/movie-recommendation](https://github.com/Rajdeep4050/movie-recommendation)
- Click **Code** → **Codespaces** → **Create codespace on main**
- Wait 2-3 minutes for setup

**2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**3. Setup Kaggle Credentials**
- Get API key: [kaggle.com/settings](https://www.kaggle.com/settings) → API → Create New Token
- Create `.env` file:
```bash
cp .env.example .env
```
- Edit `.env` with your credentials:
```env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
DEBUG=True
SECRET_KEY=django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,*.github.dev
```

**4. Train Model (5-8 minutes)**
```bash
python scripts/quick_train.py
```

**5. Run Django**
```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**6. Access Application**
- Click **Ports** tab → Port **8000** → Globe icon 🌐
- Search for movies: "Inception", "Avatar", "The Dark Knight"

---

## 🔄 Airflow MLOps Pipeline

### Start Airflow (Optional)
```bash
# In new terminal
source venv/bin/activate
bash ./deployment/codespaces/start_codespaces.sh
```

Access Airflow UI: **Port 8080** (login: admin/admin)

### Pipeline Features
- **Schedule:** Weekly (Sunday 2 AM)
- **Tasks:** 10-task orchestration
- **Features:** Auto-download dataset, validate, backup, train, evaluate, deploy

**Manual trigger:**
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow dags trigger movie_recommender_retraining
```

---

## 💡 Usage

### Web Interface
1. Open: `http://localhost:8000`
2. Search for a movie
3. Get 15 AI-powered recommendations

### API Endpoints
```bash
# Get recommendations
curl http://localhost:8000/api/recommend/?movie=Inception

# Search movies
curl http://localhost:8000/api/search/?query=dark

# Model status
curl http://localhost:8000/api/model-status/
```

---

## 📁 Project Structure

```
movie-recommendation/
├── .devcontainer/          # Codespaces config
├── .env.example            # Environment template
├── airflow/                # Airflow DAGs & config
│   ├── dags/
│   │   └── movie_recommender_retrain_dag.py
│   └── airflow.cfg
├── deployment/             # Deployment configs
│   ├── codespaces/
│   ├── docker/
│   └── render/
├── docs/                   # Documentation
│   ├── CODESPACES_GUIDE.md
│   ├── PROJECT_GUIDE.md
│   └── CHANGELOG.md
├── movie_recommendation/   # Django project
├── recommender/            # Django app
├── scripts/                # Utility scripts
│   ├── quick_train.py      # Training (Codespaces)
│   ├── download_and_train.py
│   └── test_airflow_dag.py
├── training/               # ML training code
│   ├── train.py
│   └── models/             # Trained models (3.4GB)
├── manage.py
└── requirements.txt
```

---

## 🎓 Model Training

### Quick Training (Codespaces)
```bash
python scripts/quick_train.py
```
- **Dataset:** TMDB Movies 2023
- **Movies:** 10,000 (200+ votes)
- **Time:** 5-8 minutes
- **Components:** 300 SVD components

### Full Training (More movies)
```bash
python scripts/download_and_train.py
```
- **Movies:** 26,000 (50+ votes)
- **Time:** 15-20 minutes
- **Components:** 500 SVD components

---

## 📊 Dataset

**Source:** [TMDB Movies Dataset 2023](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies)  
**Size:** 240MB (compressed), 1.3M+ movies  
**Caching:** Enabled (30-day TTL)

---

## 🧪 Testing

```bash
# Test Airflow integration
python scripts/test_airflow_dag.py

# Check environment
python codespaces_check.py
```

---

## 📖 Documentation

- **[CODESPACES_GUIDE.md](docs/CODESPACES_GUIDE.md)** - Complete Codespaces setup
- **[PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md)** - Technical details & API reference
- **[CHANGELOG.md](docs/CHANGELOG.md)** - Version history

---

## 🔧 Configuration

### Environment Variables
```env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,*.github.dev
AIRFLOW_HOME=./airflow
MODEL_DIR=./training/models
```

### Airflow Configuration
- **Executor:** SequentialExecutor
- **Database:** SQLite
- **Scheduler:** Weekly (Sunday 2 AM)
- **Retries:** 2 per task
- **Timeout:** 2 hours per task

---

## 🚢 Deployment

### GitHub Codespaces (Recommended)
✅ Native Airflow support  
✅ Pre-configured environment  
✅ 60 hours/month free

### Docker
```bash
cd deployment/docker
docker-compose -f docker-compose-airflow.yml up
```

### Render.com
- Configuration: `deployment/render/render.yaml`
- Update environment variables in Render dashboard

---

## 🛠️ Troubleshooting

**Django "Forbidden" Error:**
- Ensure `ALLOWED_HOSTS` includes `*.github.dev`
- Check `.env` file exists

**Airflow "Referrer" Error:**
- Fixed automatically in Codespaces
- Config: `enable_proxy_fix = True` in `airflow.cfg`

**Model Not Found:**
- Run training: `python scripts/quick_train.py`
- Check: `training/models/movie_metadata.parquet` exists

**Memory Issues:**
- Use `quick_train.py` instead of `download_and_train.py`
- Reduces from 26K to 10K movies

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **TMDB** - Movie dataset
- **Kaggle** - Dataset hosting
- **Apache Airflow** - MLOps orchestration
- **Django** - Web framework

---

## 🔗 Links

- **Repository:** [github.com/Rajdeep4050/movie-recommendation](https://github.com/Rajdeep4050/movie-recommendation)
- **Issues:** [github.com/Rajdeep4050/movie-recommendation/issues](https://github.com/Rajdeep4050/movie-recommendation/issues)
- **TMDB Dataset:** [kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies)

---

**Built with ❤️ using Django, scikit-learn, and Apache Airflow**
