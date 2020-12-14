import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from data import load_movies_rated, load_user_ratings, load_movies

def get_best_for_genre(genre, rated_movies=None, min_ratings=5, n=10):
    """
    Get the top movies for a given genre
    """
    rated_movies = rated_movies if rated_movies is not None else load_movies_rated()
    in_genre = rated_movies['genres'].map(lambda genres: genre in genres)
    enough_ratings = rated_movies['num_ratings'] > min_ratings
    valid = rated_movies[in_genre & enough_ratings]
    return valid.sort_values("rating", ascending=False)[:n]


def recommend_from_ratings(new_ratings, user_ratings=None, movies=None, num_users=100, n=10):
    """
    Get recommendations based on the user's ratings
    """
    user_ratings = user_ratings if user_ratings is not None else load_user_ratings()
    movies = movies if movies is not None else load_movies()
    mean_rating = sum(new_ratings.values())/len(new_ratings)
    new_vector = [new_ratings[str(col)]-mean_rating if col in new_ratings else 0
                  for col in user_ratings.columns]
    similarities = cosine_similarity(user_ratings, [new_vector])
    similar_users = [i for sim, i in sorted(zip(similarities[:,0], user_ratings.index), reverse=True)[:num_users]]
    movie_ratings = user_ratings.loc[similar_users].mean()
    ranked_movies = [i for s, i in sorted(zip(movie_ratings, movie_ratings.index), reverse=True)
                     if s > 0 and str(i) not in new_ratings][:n]
    return movies.loc[ranked_movies]