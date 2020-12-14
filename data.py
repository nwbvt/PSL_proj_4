import pandas as pd
from itertools import chain

def load_movies(loc="movies.dat"):
    movies = pd.read_csv(loc, sep="::", names=["id", "name", "genres"], index_col="id")
    movies['genres'] = movies['genres'].map(lambda g: g.split('|'))
    return movies

def load_users(loc="users.dat"):
    return pd.read_csv(loc, sep="::", names=["id", "gender", "age", "occupation", "zipcode"], index_col="id")

def load_ratings(loc="ratings.dat"):
    ratings = pd.read_csv(loc, sep="::", names=["user", "movie", "rating", "timestamp"])
    means = ratings.groupby('user')['rating'].mean()
    ratings = ratings.join(means, on="user", rsuffix="_mean")
    ratings['normalized'] = ratings["rating"] - ratings["rating_mean"]
    return ratings

def load_movies_rated(movies=None, ratings=None):
    movies = movies if movies is not None else load_movies()
    ratings = ratings if ratings is not None else load_ratings()
    grouped = ratings.groupby("movie")
    avg_ratings = grouped['normalized'].mean()
    rating_counts = grouped["movie"].count()
    return movies.join(pd.DataFrame({"rating": avg_ratings, "num_ratings": rating_counts}))

def load_genres(movies=None):
    movies = movies if movies is not None else load_movies()
    return set(chain.from_iterable(movies['genres'].values))