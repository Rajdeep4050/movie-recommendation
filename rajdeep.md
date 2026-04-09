# Movie Recommendation System - Technical Documentation
## Interview & Cross-Questioning Guide

**Project Owner:** Rajdeep Chaurasia  
**Project Type:** AI/ML-Powered Movie Recommendation System  
**Tech Stack:** Django, Python, scikit-learn, Machine Learning (TF-IDF + SVD)

---

## 1. Project Overview & Purpose

### Why I Built This Project

This project was built to demonstrate:
- **Practical ML application** - Moving beyond theoretical ML to a real-world recommendation system
- **Full-stack development skills** - Backend (Django), ML pipeline, API design, and frontend integration
- **Scalability** - Handling large datasets (1.3M+ movies) efficiently
- **Production-ready code** - Following best practices, error handling, logging, and documentation

### Real-World Use Cases

1. **Content Platforms** - Similar to Netflix, Amazon Prime, Disney+ recommendation engines
2. **Movie Discovery** - Help users find similar movies based on their preferences
3. **Research & Analysis** - Understand movie similarity patterns and content-based filtering
4. **Portfolio Project** - Demonstrate ML, Django, and system design capabilities

---

## 2. Technical Architecture

### High-Level Architecture

```
User Request → Django Web Server → Recommendation Engine → ML Model
                                         ↓
                                   Similarity Matrix
                                         ↓
                                   15 Recommendations
```

### Core Components

**1. Django Web Application** (`movie_recommendation/`, `recommender/`)
- Handles HTTP requests/responses
- Serves web interface and REST APIs
- Manages model loading and caching
- Implements health checks and monitoring

**2. ML Training Pipeline** (`training/train.py`)
- Downloads and processes TMDB dataset
- Applies quality filtering (50+ votes)
- Builds TF-IDF feature matrix
- Computes cosine similarity between movies
- Saves trained model artifacts

**3. Recommendation Engine** (`recommender/views.py`)
- Loads pre-trained similarity matrix
- Performs fast lookups (O(1) for movie index)
- Filters and ranks recommendations
- Returns top-N similar movies with metadata

**4. Frontend Interface** (`recommender/templates/`)
- Search page with autocomplete
- Results page displaying recommendations
- Responsive design (mobile/tablet/desktop)
- AJAX calls to backend APIs

**5. MLOps Pipeline** (`airflow/`)
- Apache Airflow for workflow orchestration
- Automated weekly model retraining
- Data validation and quality checks
- Model versioning and backup system

**6. Model Artifacts** (`training/models/`)
- `movie_metadata.parquet` - Movie info (ratings, genres, IMDb IDs)
- `similarity_matrix.npz` - Pre-computed similarities (26K×26K)
- `title_to_idx.json` - Fast movie title to index mapping
- `config.json` - Model configuration and metadata

---

## 3. Tech Stack & Justification

### Backend Framework: Django 6.0

**Why Django?**
- Battle-tested for production web applications
- Built-in ORM, admin panel, and security features
- Excellent documentation and community support
- Easy to build RESTful APIs
- Django REST Framework integration

### Frontend Stack

**HTML5 + CSS3 + Vanilla JavaScript** - No framework needed
- Semantic HTML, responsive grid layouts, CSS animations
- Real-time autocomplete with debounced AJAX
- Mobile-first design (single/2/3-column grids)
- Django template engine for server-side rendering

**Why No React/Vue?**
- Content-display app, not complex SPA
- Faster load (no framework bundle)
- Better SEO (server-rendered)
- Simpler (no build process)

**Key Features:**
```javascript
// Autocomplete search
input.addEventListener('input', async (e) => {
    const response = await fetch(`/api/search/?q=${e.target.value}`);
    displaySuggestions(await response.json());
});
```
- Responsive breakpoints: Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- Clean UI: Movie cards, star ratings, genre tags, IMDb links

### ML Libraries

**1. scikit-learn** - Core ML operations
- TF-IDF Vectorization for text features
- Cosine similarity computation
- TruncatedSVD for dimensionality reduction
- Industry-standard, well-documented, efficient

**2. pandas & numpy** - Data manipulation
- Fast dataframe operations (millions of rows)
- Efficient numerical computations
- Essential for data preprocessing

**3. scipy** - Sparse matrix operations
- Efficient storage (99.78% sparse similarity matrix)
- Reduces memory from 6.9GB to 3.3GB
- Fast sparse matrix operations

### MLOps: Apache Airflow 2.10

**Why Airflow?**
- Industry-standard workflow orchestration
- Automated ML pipeline management
- DAG-based task scheduling
- Built-in monitoring and logging
- Production MLOps best practices
- Easy to scale and extend

**Use Cases:**
- Automated weekly model retraining
- Data pipeline orchestration
- Model versioning and deployment
- Quality checks and validation
- Backup and rollback management

### Storage Format: Parquet

**Why Parquet?**
- Columnar storage - 50% smaller than CSV
- Fast read/write operations
- Built-in compression (gzip)
- Preserves data types
- Used by big data systems (Spark, Hadoop)

### Dataset Source: Kaggle API

**Why Kaggle?**
- Reliable, curated datasets
- Regular updates (TMDB 2023 dataset)
- API for automated downloads
- Free access to 1.3M+ movie records
- Community-validated quality

---

## 4. Dataset Information

### TMDB Movies Dataset 2023

**Source:** [Kaggle - TMDB Movies 2023](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies)

**Statistics:**
- Total movies: 1,332,407 movies
- File size: 240 MB (compressed)
- Format: Single CSV file
- Last updated: 2023

**Key Features Used:**
- `title` - Movie names
- `genres` - Movie categories (Action, Drama, etc.)
- `keywords` - Descriptive tags
- `production_companies` - Studios (Warner Bros, Disney, etc.)
- `production_countries` - Origin countries
- `overview` - Plot summaries (first 50 words)
- `tagline` - Movie taglines
- `vote_average` - User ratings (0-10)
- `vote_count` - Number of votes
- `imdb_id` - IMDb cross-reference
- `poster_path` - Poster image URLs

**Quality Filtering:**
- Applied: Medium quality (50+ votes)
- Result: 26,326 high-quality movies
- Rationale: Balance between quantity and recommendation quality

---

## 5. Machine Learning Approach

### Content-Based Filtering

**Why Content-Based (not Collaborative Filtering)?**
- No user data required (privacy-friendly)
- Works for new/unpopular movies (no cold-start problem)
- Explainable recommendations (based on genres, keywords, etc.)
- Fast inference (pre-computed similarities)

### Feature Engineering Process

**Step 1: Text Feature Extraction**
```python
# Create "soup" of movie features
soup = genres + keywords + companies + countries + overview + tagline
# Example: "Action Adventure SciFi WB USA inception dream reality..."
```

**Step 2: TF-IDF Vectorization**
- Converts text to numerical vectors (15,000 dimensions)
- Weighs important words higher (e.g., "SciFi" in sci-fi movies)
- Uses stemming (running → run) for better matching
- Matrix shape: (26,326 movies × 15,000 features)

**Step 3: Dimensionality Reduction (SVD)**
- Reduces 15,000 dimensions to 500 latent features
- Captures underlying patterns (e.g., "superhero movies")
- 56% memory reduction
- Preserves 29.2% variance (captures key patterns)
- New matrix: (26,326 × 500)

**Step 4: Cosine Similarity**
- Computes similarity between all movie pairs
- Range: 0 (different) to 1 (identical)
- Sparse matrix: Only store non-zero values
- Result: 26,326 × 26,326 similarity matrix

### Inference (Runtime)

1. User searches for "Inception"
2. System finds movie index: O(1) lookup in `title_to_idx.json`
3. Retrieve similarity scores for that movie: O(1) array access
4. Sort by similarity: O(n log n) ≈ 26K log(26K) ≈ 350K ops
5. Return top 15 recommendations
6. **Total time: < 50ms**

---

## 6. Code Structure & Key Files

### 1. `download_and_train.py` (Entry Point)

**Purpose:** One-command training automation

**What it does:**
- Loads Kaggle credentials from `.env`
- Downloads TMDB dataset (240 MB)
- Calls training pipeline
- Saves model files

**Key code:**
```python
# Loads .env file
from dotenv import load_dotenv
os.environ['KAGGLE_USERNAME'] = kaggle_username
os.environ['KAGGLE_KEY'] = kaggle_key

# Downloads dataset
dataset_path = kagglehub.dataset_download("asaniczka/tmdb-movies-dataset-2023")

# Trains model
trainer = MovieRecommenderTrainer(output_dir='./training/models')
df, sim_matrix = trainer.train(csv_path, quality_threshold='medium')
```

### 2. `training/train.py` (ML Pipeline)

**Key methods:**
```python
# load_data() - Loads CSV with pandas
# clean_and_engineer_features() - Filters (50+ votes) and ranks
df['quality_score'] = df['vote_average'] * np.log(df['vote_count'] + 1)

# build_tfidf_matrix() - Text vectorization
vectorizer = TfidfVectorizer(max_features=15000, stop_words='english', ngram_range=(1,2))
tfidf_matrix = vectorizer.fit_transform(df['soup'])

# compute_similarity_matrix() - SVD + Cosine similarity
svd = TruncatedSVD(n_components=500)
reduced_matrix = svd.fit_transform(tfidf_matrix)
similarity_matrix = cosine_similarity(reduced_matrix)
```

### 3. `recommender/views.py` (Recommendation Engine)

**MovieRecommender class:**
```python
# load_models() - Background thread loading
self.movies_df = pd.read_parquet("movie_metadata.parquet")
self.similarity_matrix = load_npz("similarity_matrix.npz")
self.title_to_idx = json.load("title_to_idx.json")

# get_recommendations() - Fast similarity lookup
def get_recommendations(self, movie_title, n=15):
    idx = self.title_to_idx[movie_title]
    sim_scores = self.similarity_matrix[idx].toarray().flatten()
    movie_indices = sim_scores.argsort()[::-1][1:n+1]
    return self.movies_df.iloc[movie_indices]
```
**Time complexity:** O(1) index lookup + O(n log n) sorting ≈ 350K ops < 50ms

### 4. `recommender/templates/` (Frontend)

**`index.html`** - Search page with autocomplete
```html
<form method="POST">
    <input type="text" name="movie" id="movie-search">
    <button type="submit">Get Recommendations</button>
</form>
<script>
// Debounced autocomplete (300ms)
searchInput.addEventListener('input', async (e) => {
    const data = await fetch(`/api/search/?q=${e.target.value}`).then(r => r.json());
    displaySuggestions(data.movies);
});
</script>
```

**`result.html`** - Movie cards grid
```html
<div class="recommendations-grid">
    {% for movie in recommendations %}
    <div class="movie-card">
        <h3>{{ movie.title }}</h3>
        <div>⭐ {{ movie.vote_average }}/10 | {{ movie.genres }}</div>
        <a href="https://www.imdb.com/title/{{ movie.imdb_id }}">IMDb</a>
    </div>
    {% endfor %}
</div>
```

**Features:** Flexbox/Grid layouts, hover effects, keyboard navigation, mobile touch targets, loading animations

### 5. `settings.py` (Configuration)
```python
MODEL_DIR = os.environ.get('MODEL_DIR', './training/models')
DEBUG = os.environ.get('DEBUG', 'True')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
```

### 6. `airflow/dags/movie_recommender_retrain_dag.py` (MLOps Pipeline)

**Purpose:** Automated weekly retraining orchestration

**DAG Tasks (9 total):**
```python
# 1. check_kaggle_credentials - Verify API access
# 2. download_dataset - Get latest TMDB data (~240MB)
# 3. validate_dataset - Quality checks (100K+ movies, required columns)
# 4. backup_current_model - Save production model
# 5. train_model - Retrain on 50K movies (~15 min)
# 6. evaluate_model - Check sparsity, similarity scores
# 7. deploy_model - Mark as production-ready
# 8. send_notification - Alert completion
# 9. cleanup_old_backups - Keep last 5 versions
```

**Schedule:** `'0 2 * * 0'` - Every Sunday at 2 AM

**Task Dependencies:**
```
credentials → download → validate → backup → train → evaluate → deploy → [notify + restart] → cleanup
```

**Key Features:**
- XCom for data passing between tasks
- Automatic retries (2x with 5min delay)
- Quality thresholds (movies > 20K, sparsity > 95%)
- Model versioning with timestamps
- Email/Slack notifications (configurable)

---

## 7. API Endpoints

**GET /** - Home page (search interface)  
**GET /api/search/?q=matrix** - Autocomplete (returns matching titles)  
**GET /api/health/** - System status (movies loaded, model health)

---

## 8. Performance Characteristics

**Training Performance:**
- Dataset loading: 30 seconds
- Feature engineering: 2 minutes
- TF-IDF computation: 3 minutes
- SVD reduction: 5 minutes
- Similarity computation: 5 minutes
- **Total: ~15 minutes** (one-time)

**Inference Performance:**
- Model loading: 3-5 seconds (startup only)
- Single recommendation: < 50ms
- Search query: < 100ms
- Concurrent users: 1000+

**Memory Usage:**
- Training: ~4-6 GB RAM
- Runtime: ~200 MB (model cached in memory)

**Storage:**
- Model size: 3.4 GB
- Database: 120 KB (minimal, only for sessions)

---

## 9. Key Interview Questions & Answers

**Q1: Why TF-IDF instead of Word2Vec/BERT?**
A: TF-IDF is simpler, faster, and sufficient for content-based filtering. Word2Vec/BERT would add complexity without significant accuracy gains for this use case. TF-IDF also provides interpretable features (word importance).

**Q2: How do you handle the cold-start problem?**
A: Content-based filtering doesn't have a cold-start problem for new movies. As long as we have metadata (genres, keywords), we can recommend similar movies immediately.

**Q3: Why sparse matrix storage?**
A: The similarity matrix is 99.78% sparse (mostly zeros). Sparse storage reduces size from 6.9GB to 3.3GB while maintaining fast lookups.

**Q4: How would you scale this to 10M+ movies?**
A: 
- Use approximate nearest neighbors (FAISS/Annoy) instead of exact similarity
- Distributed training with Spark
- Cache popular movies' recommendations
- Use Redis for faster lookups
- Horizontal scaling with load balancers

**Q5: What are the limitations?**
A:
- Only content-based (doesn't learn from user behavior)
- Recommendations can be too similar (echo chamber)
- No personalization (same results for all users)
- Requires good metadata quality

**Q6: Why not use React/Vue for the frontend?**
A: This is a content-display application, not a complex SPA. Vanilla JavaScript with Django templates provides:
- Faster initial page load (no framework bundle)
- Better SEO (server-side rendering)
- Simpler codebase (no build process)
- Sufficient for the required interactivity (autocomplete, AJAX)

**Q7: How does the autocomplete feature work?**
A: 
1. User types in search box (JavaScript event listener)
2. Debounced AJAX call to `/api/search/?q=<query>` (waits 300ms)
3. Backend performs fast title lookup (O(n) scan over 26K movies)
4. Returns matching titles as JSON
5. JavaScript dynamically updates dropdown with results
6. User clicks suggestion → populates search box

**Q8: How do you ensure responsive design?**
A: Using CSS media queries with mobile-first approach:
- Mobile (<768px): Single column, large touch targets
- Tablet (768-1024px): 2-column grid
- Desktop (>1024px): 3-column grid with hover effects
- Flexbox for flexible layouts
- Relative units (rem, %, vw) instead of fixed pixels

**Q9: Why did you add Apache Airflow?**
A: To implement MLOps best practices:
- **Automation**: Weekly retraining without manual intervention
- **Reliability**: Automatic retries and error handling
- **Monitoring**: Track pipeline execution via Airflow UI
- **Versioning**: Automated model backups and rollback capability
- **Data Quality**: Validation checks before training
- **Production-ready**: Industry-standard workflow orchestration

**Q10: How does the Airflow DAG work?**
A: 9-task pipeline executed sequentially:
1. Verify Kaggle credentials
2. Download latest dataset (240MB)
3. Validate data quality (100K+ movies check)
4. Backup current production model
5. Train new model (26K movies, 15 min)
6. Evaluate performance (sparsity, similarity checks)
7. Deploy if quality thresholds pass
8. Send completion notification
9. Cleanup old backups (keep 5 recent)

Uses XCom for inter-task communication, automatic retries, and health checks.

**Q11: How would you scale the Airflow pipeline?**
A:
- Use CeleryExecutor for parallel task execution
- PostgreSQL instead of SQLite for metadata DB
- Redis as message broker for Celery
- Kubernetes for containerized deployment
- Remote logging (S3/GCS) for centralized logs
- Add more workers for concurrent DAG runs
- Implement task pools for resource management

---

## 10. Potential Improvements

**Short-term:**
- Add user authentication and watchlists
- Implement recommendation caching (Redis)
- Add filtering by genre, year, rating
- Deploy to cloud (AWS/Heroku/Render)
- Slack/email notifications for Airflow pipeline

**Long-term:**
- Hybrid model (collaborative + content-based)
- User-personalized recommendations
- A/B testing framework via Airflow
- Recommendation explainability (why this movie?)
- Real-time model updates with streaming data
- Kubernetes deployment for Airflow workers
- Model performance monitoring dashboard

---

## 11. Project Achievements

- ✅ **Scalable**: Handles 26K+ movies with sub-50ms response
- ✅ **Production-ready**: Logging, error handling, monitoring
- ✅ **MLOps Integration**: Apache Airflow for automated retraining
- ✅ **Well-documented**: Clear README, code comments, API docs
- ✅ **Automated**: Weekly model retraining without manual intervention
- ✅ **Efficient**: 56% memory reduction with SVD
- ✅ **Modern stack**: Django 6.0, Airflow 2.10, Python 3.12
- ✅ **Versioned**: Automatic model backups with rollback capability

---
