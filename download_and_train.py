#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download dataset and train model using existing train.py
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables from .env file
load_dotenv()

print("=" * 70)
print(" Movie Recommendation System - Dataset Download & Training")
print("=" * 70)

# Step 1: Download dataset
print("\n[Step 1/2] Downloading TMDB dataset from Kaggle...")
print("-" * 70)

# Set Kaggle credentials from environment variables
kaggle_username = os.getenv('KAGGLE_USERNAME')
kaggle_key = os.getenv('KAGGLE_KEY')

if not kaggle_username or not kaggle_key or \
   kaggle_username == 'your_kaggle_username_here' or \
   kaggle_key == 'your_kaggle_api_key_here':
    print("[ERROR] Error: Kaggle credentials not set in .env file")
    print("\nPlease update the .env file with your Kaggle credentials:")
    print("  1. Visit https://www.kaggle.com/settings")
    print("  2. Click 'Create New Token' in the API section")
    print("  3. Open the downloaded kaggle.json file")
    print("  4. Copy the 'username' and 'key' values to the .env file")
    print(f"\nEdit this file: {Path(__file__).parent / '.env'}")
    sys.exit(1)

# Set environment variables for kagglehub
os.environ['KAGGLE_USERNAME'] = kaggle_username
os.environ['KAGGLE_KEY'] = kaggle_key

print(f"[OK] Kaggle credentials loaded for user: {kaggle_username}")

try:
    import kagglehub

    print("Downloading dataset (may take several minutes)...")
    dataset_path = kagglehub.dataset_download("asaniczka/tmdb-movies-dataset-2023-930k-movies")
    print(f"\n[OK] Dataset downloaded to: {dataset_path}")
    
    # Find CSV file
    csv_files = list(Path(dataset_path).glob("*.csv"))
    if not csv_files:
        print("[ERROR] Error: No CSV file found in dataset")
        sys.exit(1)
    
    csv_path = str(csv_files[0])
    print(f"[OK] Found dataset: {Path(csv_path).name}")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    print("\nNote: Kaggle authentication required!")
    print("Please set up Kaggle API credentials:")
    print("  1. Visit https://www.kaggle.com/settings")
    print("  2. Create API token (downloads kaggle.json)")
    print("  3. Place in: ~/.kaggle/kaggle.json (Linux/Mac)")
    print("              %USERPROFILE%\.kaggle\kaggle.json (Windows)")
    sys.exit(1)

# Step 2: Train model
print("\n[Step 2/2] Training recommendation model...")
print("-" * 70)
print("Configuration:")
print("  - Quality: Medium (50+ votes)")
print("  - Max movies: 50,000")
print("  - SVD components: 500")
print("  - Output: ./training/models/")
print("\nThis will take 10-15 minutes...")
print("-" * 70)

try:
    sys.path.insert(0, str(Path(__file__).parent / 'training'))
    from train import MovieRecommenderTrainer
    
    trainer = MovieRecommenderTrainer(
        output_dir='./training/models',
        use_dimensionality_reduction=True,
        n_components=500
    )
    
    df, sim_matrix = trainer.train(
        csv_path,
        quality_threshold='medium',
        max_movies=50000
    )
    
    print("\n" + "=" * 70)
    print(" [OK] SUCCESS! Model ready for use!")
    print("=" * 70)
    print("\nNext: Restart server with: python manage.py runserver")
    
except Exception as e:
    print(f"\n[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
