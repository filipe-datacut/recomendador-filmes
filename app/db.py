import sqlite3
from pathlib import Path

import pandas as pd

from app.dataset import load_ratings, load_movies

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Cria as tabelas se nao existirem e popula com o MovieLens na 1a vez."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS movies "
                "(movieId INTEGER PRIMARY KEY, title TEXT, genres TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ratings "
                "(userId INTEGER, movieId INTEGER, rating REAL, "
                "PRIMARY KEY (userId, movieId))")
    conn.commit()

    vazio = cur.execute("SELECT COUNT(*) FROM ratings").fetchone()[0] == 0
    if vazio:
        load_movies()[["movieId", "title", "genres"]].to_sql(
            "movies", conn, if_exists="append", index=False)
        load_ratings()[["userId", "movieId", "rating"]].to_sql(
            "ratings", conn, if_exists="append", index=False)
        conn.commit()
    conn.close()


def read_ratings() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT userId, movieId, rating FROM ratings", conn)
    conn.close()
    return df


def read_movies() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT movieId, title, genres FROM movies", conn)
    conn.close()
    return df


def movie_exists(movie_id: int) -> bool:
    conn = get_conn()
    achou = conn.execute("SELECT 1 FROM movies WHERE movieId = ?",
                         (movie_id,)).fetchone() is not None
    conn.close()
    return achou


def insert_movie(title: str, genres: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO movies (title, genres) VALUES (?, ?)", (title, genres))
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


def upsert_rating(user_id: int, movie_id: int, rating: float):
    conn = get_conn()
    conn.execute(
        "INSERT INTO ratings (userId, movieId, rating) VALUES (?, ?, ?) "
        "ON CONFLICT(userId, movieId) DO UPDATE SET rating = excluded.rating",
        (user_id, movie_id, rating))
    conn.commit()
    conn.close()