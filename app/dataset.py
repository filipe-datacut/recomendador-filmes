from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "ml-latest-small"


def load_ratings() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ratings.csv")


def load_movies() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "movies.csv")


if __name__ == "__main__":
    ratings = load_ratings()
    movies = load_movies()
    print("ratings:", ratings.shape)
    print(ratings.head(), "\n")
    print("movies:", movies.shape)
    print(movies.head(), "\n")
    print("usuarios unicos:", ratings["userId"].nunique())
    print("filmes avaliados:", ratings["movieId"].nunique())