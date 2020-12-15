import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from data import load_movies_rated, load_user_ratings, load_movies, load_movie_ratings

def get_best_for_genre(genre, rated_movies=None, min_ratings=5):
    """
    Get the top movies for a given genre
    """
    rated_movies = rated_movies if rated_movies is not None else load_movies_rated()
    in_genre = rated_movies['genres'].map(lambda genres: genre in genres)
    enough_ratings = rated_movies['num_ratings'] > min_ratings
    valid = rated_movies[in_genre & enough_ratings]
    return valid.sort_values("rating", ascending=False)


def user_based_collaborative(new_ratings, user_ratings=None, movies=None, num_users=100):
    """
    Get recommendations based on the user's ratings
    """
    user_ratings = user_ratings if user_ratings is not None else load_user_ratings()
    movies = movies if movies is not None else load_movies()
    rated_movies = [int(m) for m in new_ratings.keys() if int(m) in user_ratings.columns]
    relevant_ratings = user_ratings[rated_movies]
    mean_rating = sum(new_ratings.values())/len(new_ratings)
    new_vector = [rating-mean_rating for m, rating in new_ratings.items() if int(m) in user_ratings.columns]
    similarities = cosine_similarity(relevant_ratings, [new_vector])
    similar_users = [i for sim, i in sorted(zip(similarities[:,0], user_ratings.index), reverse=True)[:num_users]]
    movie_ratings = user_ratings.loc[similar_users].mean()
    movie_ratings.name = "rating"
    ranked_movies = movies.join(movie_ratings).sort_values('rating', ascending=False)
    return ranked_movies

def item_based_collaborative(new_ratings, movie_ratings=None, movies=None):
    """
    Get recommendations based on similar movies to the user's favorites
    """
    movie_ratings = movie_ratings if movie_ratings is not None else load_movie_ratings()
    movies = movies if movies is not None else load_movies()
    highest_rating = max(new_ratings.values())
    rated_movies = [int(movie) for movie in new_ratings if int(movie) in movie_ratings.index]
    index_list = movie_ratings.index.tolist()
    favorite_movies = [index_list.index(movie) for movie in rated_movies if new_ratings[str(movie)] == highest_rating]
    sims = cosine_similarity(movie_ratings)[favorite_movies,].mean(axis=0)
    ranked = movies.join(pd.DataFrame({"rating": sims}, index=index_list)).sort_values("rating", ascending=False)
    ranked.drop(rated_movies, axis=0, inplace=True)
    return ranked