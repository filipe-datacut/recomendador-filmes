import pandas as pd

from app.dataset import load_ratings, load_movies
from app.recommender import Recommender


class RecommenderService:
    """Mantem o estado (avaliacoes, filmes, usuarios) e reconstroi o modelo
    de forma preguicosa: mutacoes marcam o modelo como desatualizado, e ele
    so e reconstruido na proxima recomendacao."""

    def __init__(self, ratings: pd.DataFrame = None, movies: pd.DataFrame = None):
        r = ratings if ratings is not None else load_ratings()
        m = movies if movies is not None else load_movies()
        self.ratings = r[["userId", "movieId", "rating"]].copy()
        self.movies = m[["movieId", "title", "genres"]].copy()
        self.users = set(self.ratings["userId"].unique().tolist())
        self._model = None
        self._dirty = True

    def _model_atual(self) -> Recommender:
        if self._dirty or self._model is None:
            self._model = Recommender(self.ratings, self.movies)
            self._dirty = False
        return self._model

    def recommend(self, user_id: int, n: int = 10):
        return self._model_atual().recommend(user_id, n)

    def add_user(self) -> int:
        novo = (max(self.users) + 1) if self.users else 1
        self.users.add(novo)
        return novo

    def add_item(self, title: str, genres: str = "(no genres listed)") -> int:
        novo = int(self.movies["movieId"].max()) + 1
        linha = pd.DataFrame([{"movieId": novo, "title": title, "genres": genres}])
        self.movies = pd.concat([self.movies, linha], ignore_index=True)
        self._dirty = True
        return novo

    def set_preference(self, user_id: int, movie_id: int, rating: float):
        if movie_id not in set(self.movies["movieId"]):
            raise ValueError(f"filme {movie_id} nao existe")
        self.users.add(user_id)
        mask = ~((self.ratings["userId"] == user_id) & (self.ratings["movieId"] == movie_id))
        nova = pd.DataFrame([{"userId": user_id, "movieId": movie_id, "rating": rating}])
        self.ratings = pd.concat([self.ratings[mask], nova], ignore_index=True)
        self._dirty = True