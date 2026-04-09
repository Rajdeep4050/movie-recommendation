# 🚀 Quick Start - GitHub Codespaces

## 3 Steps to Run Airflow with Full UI

### Step 1: Open Codespaces (2 min)
1. Go to: https://github.com/Rajdeep4050/movie-recommendation
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait for setup to complete

### Step 2: Add Kaggle Credentials (30 sec)
```bash
cat > .env << 'EOF'
KAGGLE_USERNAME=rajdeep4050
KAGGLE_KEY=your_key_here
DEBUG=True
SECRET_KEY=django-insecure-dev-key-12345
ALLOWED_HOSTS=localhost,127.0.0.1,*.github.dev
MODEL_DIR=./training/models
EOF
```

### Step 3: Start Everything (1 command)
```bash
chmod +x start_codespaces.sh && ./start_codespaces.sh
```

## Access URLs

**Airflow UI**: Ports tab → Port 8080 → Click globe icon  
**Login**: admin / admin

**Django App**: Ports tab → Port 8000 → Click globe icon

## That's It! 🎉

Your full Airflow MLOps pipeline is running with:
- ✅ Web UI (webserver)
- ✅ Scheduler 
- ✅ 10-task DAG ready to trigger
- ✅ Full Linux environment
- ✅ No Windows limitations

---

For detailed guide, see: [CODESPACES_GUIDE.md](./CODESPACES_GUIDE.md)
