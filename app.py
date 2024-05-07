from flask import Flask, render_template, request
import pickle
import requests
import pandas as pd

app = Flask(__name__)

Movies = pd.read_csv('TMDB_10000_Popular_Movies.csv')
movies = pickle.load(open('rec_movies.pkl', 'rb'))
simi = pickle.load(open('simi.pkl', 'rb'))


def cover(mov_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=09a1dc2a110331fbb2f90818ce713ec9&language=en-US".format(
        mov_id)
    data = requests.get(url)
    data = data.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def top_movies(movie):
    idx = movies[movies['Title'] == movie].index[0]
    mov = sorted(list(enumerate(simi[idx])), reverse=True, key=lambda vector_data: vector_data[1])
    movie_to_recommend = []
    poster_recommend = []
    for i in mov[1:6]:
        mov_id = movies.iloc[i[0]].TMDb_Id
        movie_to_recommend.append(movies.iloc[i[0]].Title)
        poster_recommend.append(cover(mov_id))
    return movie_to_recommend, poster_recommend


@app.route('/')
def home():
    list_movies = movies['Title'].values
    genres = Movies['Genres'].unique()
    return render_template('index.html', list_movies=list_movies, genres=genres)


@app.route('/recommend', methods=['POST'])
def recommend():
    selected_movie = request.form['selected_movie']
    name, mov_cover = top_movies(selected_movie)
    return render_template('recommendations.html', movies=zip(name, mov_cover))


@app.route('/recommend_by_genre', methods=['POST'])
def recommend_by_genre():
    selected_genre = request.form['selected_genre']
    genre_movies = Movies[Movies['Genres'] == selected_genre]
    genre_movie_titles = genre_movies['Title'].tolist()
    
    mov_covers = []
    for idx, row in genre_movies.iterrows():
        mov_id = row['TMDb_Id']
        mov_covers.append(cover(mov_id))
    
    movies_zipped = list(zip(genre_movie_titles, mov_covers))
    
    # Pass a variable to indicate genre recommendations are being displayed
    return render_template('genre_recommendations.html', movies=movies_zipped, display_genre_recommendations=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)  # Adjust the port as needed

