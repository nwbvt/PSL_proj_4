from data import load_movies_rated

def get_best_for_genre(genre, rated_movies=None, min_ratings=5, n=10):
    """
    Get the top movies for a given genre
    """
    rated_movies = rated_movies if rated_movies is not None else load_movies_rated()
    in_genre = rated_movies['genres'].map(lambda genres: genre in genres)
    enough_ratings = rated_movies['num_ratings'] > min_ratings
    valid = rated_movies[in_genre & enough_ratings]
    return valid.sort_values("rating", ascending=False)[:n]