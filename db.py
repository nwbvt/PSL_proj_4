import math
import sys
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, ForeignKey, Float, Enum

METADATA = MetaData()
MOVIES = Table('movies', METADATA,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False))
GENRES = Table('genres', METADATA,
    Column('movie', None, ForeignKey('movies.id')),
    Column('genre', String, nullable=False))
USERS = Table('users', METADATA,
    Column('id', Integer, primary_key=True),
    Column('gender', Enum('M', 'F')),
    Column('age', Integer),
    Column('occupation', Integer),
    Column('zipcode', Integer))
RATINGS = Table('ratings', METADATA,
    Column('user', None, ForeignKey('users.id')),
    Column('movie', None, ForeignKey('movies.id')),
    Column('rating', Float),
    Column('timetamp', Integer))

def init_db(loc="movies.db"):
    db = create_engine(f"sqlite:///{loc}")
    return db

MAX_ROWS = 10000

def load_data(db):
    METADATA.create_all(db)
    with open('movies.dat', 'rb') as f:
        movies_and_genres = [line.decode("latin").strip().split("::") for line in f.readlines()]
    movies = [(movie_id, title) for movie_id, title, genres in movies_and_genres]
    genres = [(movie_id, genre) for movie_id, title, genres in movies_and_genres for genre in genres.split("|")]
    with open('users.dat', 'rb') as f:
        users = [line.decode("latin").strip().split("::") for line in f.readlines()]
    with open('ratings.dat', 'rb') as f:
        ratings = [line.decode("latin").strip().split("::") for line in f.readlines()]
    with db.connect() as conn:
        conn.execute(MOVIES.insert().values(movies))
        conn.execute(GENRES.insert().values(genres))
        conn.execute(USERS.insert().values(users))
        for i in range(math.ceil(len(ratings)/MAX_ROWS)):
            conn.execute(RATINGS.insert().values(ratings[i*MAX_ROWS:(i+1)*MAX_ROWS]))

def run_init():
    db = init_db()
    load_data(db)

if __name__ == "__main__":
    run_init()