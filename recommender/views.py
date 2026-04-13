"""
Movie Recommendation System Views
Integrates with advanced TMDB model training system
"""
import logging
import os
import threading
from pathlib import Path
from typing import Dict, List, Optional
from difflib import get_close_matches

import pandas as pd
import numpy as np
from scipy.sparse import load_npz
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# Global cache for recommender system
_RECOMMENDER = None
_MODEL_LOADING = False
_MODEL_LOAD_PROGRESS = 0
_LOADING_THREAD = None
_LOAD_ERROR = None


class MovieRecommender:
    """Integrated recommender system matching training/infer.py logic"""
    
    def __init__(self, model_dir='models', progress_callback=None):
        """Initialize with trained model directory"""
        self.model_dir = Path(model_dir)
        self.metadata = None
        self.similarity_matrix = None
        self.title_to_idx = None
        self.config = None
        self._load_models(progress_callback)
    
    def _load_models(self, progress_callback=None):
        """Load all model artifacts with progress tracking"""
        global _MODEL_LOAD_PROGRESS
        logger.info(f"Loading models from {self.model_dir}...")
        
        # Load metadata (25%)
        if progress_callback:
            progress_callback(10)
        self.metadata = pd.read_parquet(self.model_dir / 'movie_metadata.parquet')
        if progress_callback:
            progress_callback(25)
        
        # Load similarity matrix (sparse or dense) (50%)
        if progress_callback:
            progress_callback(40)
        if (self.model_dir / 'similarity_matrix.npz').exists():
            self.similarity_matrix = load_npz(self.model_dir / 'similarity_matrix.npz').toarray()
        else:
            self.similarity_matrix = np.load(self.model_dir / 'similarity_matrix.npy')
        if progress_callback:
            progress_callback(65)
        
        # Load title mapping (75%)
        with open(self.model_dir / 'title_to_idx.json', 'r') as f:
            self.title_to_idx = json.load(f)
        if progress_callback:
            progress_callback(80)
        
        # Load config (100%)
        with open(self.model_dir / 'config.json', 'r') as f:
            self.config = json.load(f)
        if progress_callback:
            progress_callback(100)
        
        logger.info(f"Loaded {self.config['n_movies']:,} movies successfully")
    
    def find_movie(self, title: str) -> Optional[str]:
        """Find closest matching movie title"""
        matches = get_close_matches(title, self.title_to_idx.keys(), n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    def search_movies(self, query: str, n: int = 20) -> List[str]:
        """Search movies by partial title"""
        query_lower = query.lower()
        return [title for title in self.title_to_idx.keys() 
                if query_lower in title.lower()][:n]
    
    def get_recommendations(
        self,
        movie_title: str,
        n: int = 15,
        min_rating: float = None,
        genre_filter: list = None,
        country_filter: str = None,
        language_filter: str = None,
        year_min: int = None,
        year_max: int = None,
        runtime_min: int = None,
        runtime_max: int = None,
        budget_min: int = None,
        budget_max: int = None,
        revenue_min: int = None,
        revenue_max: int = None
    ) -> Dict:
        """Get movie recommendations with optional filtering"""
        matched_title = self.find_movie(movie_title)
        if not matched_title:
            return {'error': f"Movie '{movie_title}' not found", 'suggestions': self.search_movies(movie_title, 5)}
        
        movie_idx = self.title_to_idx[matched_title]
        source_movie = self.metadata.iloc[movie_idx]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]  # Exclude self
        
        recommendations = []
        for idx, score in sim_scores:
            if len(recommendations) >= n:
                break
            
            movie = self.metadata.iloc[idx]
            
            # Rating filter
            if min_rating and movie['vote_average'] < min_rating:
                continue
            
            # Genre filter
            if genre_filter:
                movie_genres = movie['genres'] if isinstance(movie['genres'], list) else []
                if not any(g.lower() in [gf.lower() for gf in genre_filter] for g in movie_genres):
                    continue
            
            # Country filter
            if country_filter:
                movie_countries = movie['production_countries'] if isinstance(movie['production_countries'], list) else []
                if country_filter.lower() not in [c.lower() for c in movie_countries]:
                    continue
            
            # Language filter
            if language_filter:
                movie_languages = movie['spoken_languages'] if isinstance(movie['spoken_languages'], list) else []
                if language_filter.lower() not in [l.lower() for l in movie_languages]:
                    continue
            
            # Year filter
            if year_min or year_max:
                try:
                    release_str = str(movie['release_date'])
                    if len(release_str) >= 4:
                        year = int(release_str.split('-')[0]) if '-' in release_str else int(release_str[:4])
                        if year_min and year < year_min:
                            continue
                        if year_max and year > year_max:
                            continue
                except:
                    continue
            
            # Runtime filter
            if runtime_min and pd.notna(movie['runtime']) and movie['runtime'] < runtime_min:
                continue
            if runtime_max and pd.notna(movie['runtime']) and movie['runtime'] > runtime_max:
                continue
            
            # Budget filter
            if budget_min and pd.notna(movie['budget']) and movie['budget'] < budget_min:
                continue
            if budget_max and pd.notna(movie['budget']) and movie['budget'] > budget_max:
                continue
            
            # Revenue filter
            if revenue_min and pd.notna(movie['revenue']) and movie['revenue'] < revenue_min:
                continue
            if revenue_max and pd.notna(movie['revenue']) and movie['revenue'] > revenue_max:
                continue
            
            recommendations.append({
                'title': movie['title'],
                'release_date': movie['release_date'] if pd.notna(movie['release_date']) else 'Unknown',
                'production': movie['primary_company'] if pd.notna(movie['primary_company']) else 'Unknown',
                'genres': ', '.join(movie['genres'][:3]) if isinstance(movie['genres'], list) else 'N/A',
                'rating': f"{movie['vote_average']:.1f}/10" if pd.notna(movie['vote_average']) else 'N/A',
                'votes': f"{movie['vote_count']:,}" if pd.notna(movie['vote_count']) else 'N/A',
                'similarity_score': f"{score:.3f}",
                'runtime': f"{int(movie['runtime'])} min" if pd.notna(movie['runtime']) else 'N/A',
                'budget': f"${movie['budget']:,}" if pd.notna(movie['budget']) and movie['budget'] > 0 else 'N/A',
                'revenue': f"${movie['revenue']:,}" if pd.notna(movie['revenue']) and movie['revenue'] > 0 else 'N/A',
                'original_language': movie['original_language'] if pd.notna(movie['original_language']) else 'N/A',
                'imdb_id': movie['imdb_id'] if pd.notna(movie['imdb_id']) else None,
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if pd.notna(movie['poster_path']) else None,
                'google_link': f"https://www.google.com/search?q={'+'.join(movie['title'].split())}+movie",
                'imdb_link': f"https://www.imdb.com/title/{movie['imdb_id']}" if pd.notna(movie['imdb_id']) else None
            })
        
        return {
            'query_movie': matched_title,
            'source_movie': {
                'production': source_movie['primary_company'] if pd.notna(source_movie['primary_company']) else 'Unknown',
                'rating': f"{source_movie['vote_average']:.1f}/10" if pd.notna(source_movie['vote_average']) else 'N/A',
                'genres': ', '.join(source_movie['genres'][:3]) if isinstance(source_movie['genres'], list) else 'N/A'
            },
            'recommendations': recommendations
        }
    
    def search_by_genre(self, genre: str, n_results: int = 15) -> Dict:
        """
        Search for top movies by genre
        
        Args:
            genre: Genre to search for (required)
            n_results: Number of results to return
        
        Returns:
            Dictionary with search results
        """
        df = self.metadata
        
        # Filter by genre
        genre_movies = df[df['genres'].apply(
            lambda x: genre in x if isinstance(x, (list, np.ndarray)) else False
        )].copy()
        
        # Sort by rating and popularity
        genre_movies['quality_score'] = genre_movies['vote_average'] * np.log1p(genre_movies['vote_count'])
        genre_movies = genre_movies.sort_values('quality_score', ascending=False).head(n_results)
        
        results = []
        for idx, row in genre_movies.iterrows():
            results.append({
                'title': row['title'],
                'release_date': row['release_date'] if pd.notna(row['release_date']) else 'Unknown',
                'production': row['primary_company'] if pd.notna(row['primary_company']) else 'Unknown',
                'genres': ', '.join(row['genres'][:3]) if isinstance(row['genres'], list) else 'N/A',
                'rating': f"{row['vote_average']:.1f}/10" if pd.notna(row['vote_average']) else 'N/A',
                'votes': f"{row['vote_count']:,}" if pd.notna(row['vote_count']) else 'N/A',
                'runtime': f"{int(row['runtime'])} min" if pd.notna(row['runtime']) else 'N/A',
                'budget': f"${row['budget']:,}" if pd.notna(row['budget']) and row['budget'] > 0 else 'N/A',
                'revenue': f"${row['revenue']:,}" if pd.notna(row['revenue']) and row['revenue'] > 0 else 'N/A',
                'original_language': row['original_language'] if pd.notna(row['original_language']) else 'N/A',
                'imdb_id': row['imdb_id'] if pd.notna(row['imdb_id']) else None,
                'poster_url': f"https://image.tmdb.org/t/p/w500{row['poster_path']}" if pd.notna(row['poster_path']) else None,
                'google_link': f"https://www.google.com/search?q={'+'.join(row['title'].split())}+movie",
                'imdb_link': f"https://www.imdb.com/title/{row['imdb_id']}" if pd.notna(row['imdb_id']) else None
            })
        
        return {
            'search_type': 'genre',
            'genre': genre,
            'total_results': len(results),
            'results': results
        }


def _load_model_in_background():
    """Load model in background thread"""
    global _RECOMMENDER, _MODEL_LOADING, _MODEL_LOAD_PROGRESS, _LOAD_ERROR
    
    _MODEL_LOADING = True
    _MODEL_LOAD_PROGRESS = 0
    _LOAD_ERROR = None
    
    # Check for model directory (configurable via settings or environment)
    model_dir = getattr(settings, 'MODEL_DIR', os.environ.get('MODEL_DIR', 'models'))
    
    # Fallback to static directory if models directory doesn't exist
    if not Path(model_dir).exists():
        model_dir = 'static'
        logger.warning(f"Model directory not found, using static directory")
    
    try:
        def progress_callback(progress):
            global _MODEL_LOAD_PROGRESS
            _MODEL_LOAD_PROGRESS = progress
            logger.info(f"Model loading progress: {progress}%")
        
        _RECOMMENDER = MovieRecommender(model_dir, progress_callback)
        _MODEL_LOADING = False
        _MODEL_LOAD_PROGRESS = 100
        logger.info("Model loaded successfully")
    except Exception as e:
        _MODEL_LOADING = False
        _LOAD_ERROR = str(e)
        logger.error(f"Failed to load recommender: {e}")


def _start_model_loading():
    """Start model loading in background if not already started"""
    global _LOADING_THREAD, _RECOMMENDER, _MODEL_LOADING
    
    if _RECOMMENDER is None and not _MODEL_LOADING:
        if _LOADING_THREAD is None or not _LOADING_THREAD.is_alive():
            logger.info("Starting model loading in background...")
            _LOADING_THREAD = threading.Thread(target=_load_model_in_background, daemon=True)
            _LOADING_THREAD.start()


def _get_recommender():
    """Get or initialize the recommender singleton"""
    global _RECOMMENDER, _LOAD_ERROR
    
    if _RECOMMENDER is None:
        _start_model_loading()
        if _LOAD_ERROR:
            raise Exception(_LOAD_ERROR)
        return None
    
    return _RECOMMENDER


@require_http_methods(["GET", "POST"])
def main(request):
    """
    Main view for movie recommendation system.
    GET: Display search interface
    POST: Process search and display recommendations
    """
    # Start loading model if not already loading/loaded
    _start_model_loading()
    
    recommender = _get_recommender()
    
    # If model is still loading, show the page with loading state
    if recommender is None:
        if request.method == 'GET':
            return render(request, 'recommender/index.html', {
                'all_movie_names': [],
                'total_movies': 0,
            })
        else:
            # For POST requests, return error if model not ready
            return render(request, 'recommender/index.html', {
                'all_movie_names': [],
                'total_movies': 0,
                'error_message': 'Model is still loading. Please wait a moment and try again.',
            })
    
    # Model is loaded, proceed normally
    titles_list = list(recommender.title_to_idx.keys())
    
    if request.method == 'GET':
        return render(
            request,
            'recommender/index.html',
            {
                'all_movie_names': titles_list,
                'total_movies': len(titles_list),
            }
        )
    
    # POST request - process search
    search_type = request.POST.get('search_type', 'movie')
    
    if search_type == 'genre':
        # Genre search
        genre = request.POST.get('genre', '').strip()
        
        if not genre:
            return render(
                request,
                'recommender/index.html',
                {
                    'all_movie_names': titles_list,
                    'total_movies': len(titles_list),
                    'error_message': 'Please select a genre.',
                    'search_type': 'genre'
                }
            )
        
        # Get genre search results (no language filter)
        result = recommender.search_by_genre(genre, n_results=15)
        
        return render(
            request,
            'recommender/result.html',
            {
                'all_movie_names': titles_list,
                'search_result': result,
                'total_results': len(result['results']),
                'search_type': 'genre',
                'genre': genre,
                'recommended_movies': result['results'],
                'total_recommendations': len(result['results']),
            }
        )
    
    else:
        # Movie search (default)
        movie_name = request.POST.get('movie_name', '').strip()
        
        if not movie_name:
            return render(
                request,
                'recommender/index.html',
                {
                    'all_movie_names': titles_list,
                    'total_movies': len(titles_list),
                    'error_message': 'Please enter a movie name.',
                    'search_type': 'movie'
                }
            )
        
        # Get recommendations
        result = recommender.get_recommendations(movie_name, n=15)
        
        if 'error' in result:
            return render(
                request,
                'recommender/index.html',
                {
                    'all_movie_names': titles_list,
                    'total_movies': len(titles_list),
                    'input_movie_name': movie_name,
                    'error_message': result['error'],
                    'suggestions': result.get('suggestions', [])
                }
            )
        
        return render(
            request,
            'recommender/result.html',
            {
                'all_movie_names': titles_list,
                'input_movie_name': result['query_movie'],
                'source_movie': result['source_movie'],
                'recommended_movies': result['recommendations'],
                'total_recommendations': len(result['recommendations']),
                'search_type': 'movie',
            }
        )


@require_http_methods(["GET"])
def search_movies(request):
    """API endpoint for searching movies (autocomplete)"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'movies': [], 'count': 0})
    
    try:
        recommender = _get_recommender()
        
        if recommender is None:
            return JsonResponse({'movies': [], 'count': 0, 'loading': True})
        
        matching_movies = recommender.search_movies(query, n=20)
        
        return JsonResponse({
            'movies': matching_movies,
            'count': len(matching_movies)
        })
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return JsonResponse({'error': 'Search failed'}, status=500)


@require_http_methods(["GET"])
def model_status(request):
    """API endpoint to check model loading status"""
    global _RECOMMENDER, _MODEL_LOADING, _MODEL_LOAD_PROGRESS, _LOAD_ERROR
    
    # Start loading if not already started
    _start_model_loading()
    
    if _LOAD_ERROR:
        return JsonResponse({
            'loaded': False,
            'progress': 0,
            'status': 'error',
            'error': _LOAD_ERROR
        })
    elif _RECOMMENDER is not None:
        return JsonResponse({
            'loaded': True,
            'progress': 100,
            'status': 'ready'
        })
    elif _MODEL_LOADING:
        return JsonResponse({
            'loaded': False,
            'progress': _MODEL_LOAD_PROGRESS,
            'status': 'loading'
        })
    else:
        return JsonResponse({
            'loaded': False,
            'progress': 0,
            'status': 'initializing'
        })


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        recommender = _get_recommender()
        return JsonResponse({
            'status': 'healthy',
            'movies_loaded': recommender.config['n_movies'],
            'model_dir': str(recommender.model_dir),
            'model_loaded': True
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
