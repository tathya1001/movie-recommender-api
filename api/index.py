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

model = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
similarity_list = similarity.tolist()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def get_poster_path(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
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
    try:
        movie_index = model[model['title'].str.lower() == movie.lower()].index[0]
    except IndexError:
        return abort(404, description="Movie not found")

    distances = similarity_list[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[0:11]
    
    recommended_movies_posters = []
    
    for i in movies_list:
        movie_id = int(model.iloc[i[0]]['movie_id'])
        poster_url = get_poster_path(movie_id, '18801745663fe6b9442bb058ce026e76')
        if poster_url:
            recommended_movies_posters.append(poster_url)
    
    return jsonify(recommended_movies_posters)

if __name__ == "__main__":
    app.run(debug=True)
