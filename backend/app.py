from flask import Flask, jsonify, request
from flask_cors import CORS
from recommendation.content_based import get_recommendations
import pandas as pd
import random
import requests

app = Flask(__name__)
CORS(app)
TMDB_API_KEY = '35e3a8b796443114fbc9d7a597482ef8'
TMDB_BASE_URL = 'https://www.themoviedb.org/3/movie/'
df = pd.read_csv("data/movies.csv")  # or wherever your dataset is
df2 = pd.read_csv("data/links.csv")

merged_df = pd.merge(df,df2,on="movieId")

def fetch_poster_url(tmdb_id):
    """Fetch poster URL from TMDb API using TMDb ID"""
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzNWUzYThiNzk2NDQzMTE0ZmJjOWQ3YTU5NzQ4MmVmOCIsIm5iZiI6MTc0NjczMDU1Mi4wOTIsInN1YiI6IjY4MWNmZTM4N2E1NTVkZWY4OGIxYzliNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fAcVnUPOvjEyciFgBuNlYYH2PCTSKjG5p5jMrOCj-ug"
    }
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images"
    response = requests.get(url,headers=headers)
    data = response.json()
    backdrops = data.get("backdrops", [])
    if backdrops:
        file_path = backdrops[0]["file_path"]  # Take the first image
        return f"https://image.tmdb.org/t/p/w780{file_path}"  # Choose appropriate width (e.g. w500, w780, original)
    return None


@app.route('/')
def home():
    data = {"genres": list({"Action", "Drama", "Comedy"})}  
    return jsonify(data)


@app.route('/recommend', methods=['GET'])
def recommend():
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Missing title"}), 400

    results = get_recommendations(title)
    return jsonify(results)

@app.route("/random-movies")
def random_movies():
    sample = merged_df.sample(n=10)
    movie_data = []

    # Loop through each movie in the random movie sample
    for _, row in sample.iterrows():
        movie_title = row['title']  # Replace with your column name
        tmdb_id = row['tmdbId']  # The tmdbId column from random movie dataset
        # Fetch poster URL using the tmdbId from links dataset
        poster_url = fetch_poster_url(tmdb_id)
        movie_data.append({
            "title": movie_title,
            "genre": row['genres'],  # Replace with your actual genre column name
            "poster_url": poster_url
        })

    return jsonify(movie_data)

if __name__ == '__main__':
    app.run(debug=True)




    

