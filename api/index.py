import numpy as np
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
import pickle
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app)

reduced_data = pickle.load(open('reduced_movies.pkl', 'rb'))

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def get_poster_path(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=18801745663fe6b9442bb058ce026e76"
    response = requests.get(url).json()
    poster_path = response.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend/<string:movie>")
def predict(movie):
    movie_data = reduced_data.get(movie.title())

    if not movie_data:
        return abort(404, description="Movie not found")

    recommended_movies_posters = []
    
    for recommended_movie in movie_data['recommendations']:
        poster_url = get_poster_path(recommended_movie['movie_id'], TMDB_API_KEY)
        if poster_url:
            recommended_movies_posters.append(poster_url)
    
    return jsonify(recommended_movies_posters)

if __name__ == "__main__":
    app.run(debug=True)
