#!/usr/bin/env python3
"""
Quick training script for Codespaces (memory-constrained environment)
Trains on fewer movies to avoid memory issues
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print(" Movie Recommendation System - Quick Training (Codespaces)")
print("=" * 70)

# Load environment variables
load_dotenv()

# Get Kaggle credentials
kaggle_username = os.getenv('KAGGLE_USERNAME')
kaggle_key = os.getenv('KAGGLE_KEY')

if not kaggle_username or not kaggle_key:
    print("\n[ERROR] Kaggle credentials not found in .env file")
    sys.exit(1)

os.environ['KAGGLE_USERNAME'] = kaggle_username
os.environ['KAGGLE_KEY'] = kaggle_key

print(f"[OK] Kaggle credentials loaded for user: {kaggle_username}")

try:
    import kagglehub
    from datetime import datetime, timedelta
    import json
    import shutil

    # Cache configuration
    CACHE_DIR = Path(__file__).parent.parent / "datasets" / "kaggle" / "tmdb-movies"
    CACHE_METADATA = CACHE_DIR / ".cache_metadata.json"
    CACHE_TTL_DAYS = 30

    # Check cache validity
    cache_valid = False
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
                    cache_valid = True

    if not cache_valid:
        print("[CACHE MISS] Downloading dataset (may take several minutes)...")
        dataset_path = kagglehub.dataset_download("asaniczka/tmdb-movies-dataset-2023-930k-movies")

        # Find CSV file
        csv_files = list(Path(dataset_path).glob("*.csv"))
        if not csv_files:
            print("[ERROR] No CSV file found in dataset")
            sys.exit(1)

        csv_path = str(csv_files[0])

        # Copy to cache directory
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cached_csv = CACHE_DIR / Path(csv_path).name
        shutil.copy2(csv_path, cached_csv)
        csv_path = str(cached_csv)

        # Save metadata
        metadata = {
            'downloaded_at': datetime.now().isoformat(),
            'csv_path': csv_path,
            'original_path': dataset_path,
            'dataset_id': 'asaniczka/tmdb-movies-dataset-2023-930k-movies'
        }
        with open(CACHE_METADATA, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"[OK] Dataset cached for future use")

    print(f"[OK] Found dataset: {Path(csv_path).name}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)

# Step 2: Train model with reduced parameters
print("\n[Step 2/2] Training recommendation model (Codespaces optimized)...")
print("-" * 70)
print("Configuration:")
print("  - Quality: High (200+ votes) - FEWER movies for Codespaces")
print("  - Max movies: 10,000 - Memory-optimized")
print("  - SVD components: 300 - Reduced for speed")
print("  - Output: ./training/models/")
print("\nThis will take 5-8 minutes...")
print("-" * 70)

try:
    # Add training directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'training'))
    from train import MovieRecommenderTrainer

    trainer = MovieRecommenderTrainer(
        output_dir='./training/models',
        use_dimensionality_reduction=True,
        n_components=300  # Reduced from 500
    )

    df, sim_matrix = trainer.train(
        csv_path,
        quality_threshold='high',  # 200+ votes = fewer movies
        max_movies=10000  # Limit to 10k movies for Codespaces
    )

    print("\n" + "=" * 70)
    print(f"[OK] Training completed successfully!")
    print(f"[OK] Trained on {len(df)} movies")
    print(f"[OK] Models saved to: ./training/models/")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n[WARNING] Training interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
