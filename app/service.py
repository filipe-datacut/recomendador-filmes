from app import db
from app.recommender import Recommender


class RecommenderService:
    """Estado persistido em SQLite. Mutacoes escrevem no banco e marcam o
    modelo como desatualizado; ele e reconstruido (relendo do banco) apenas
    na proxima recomendacao."""

    def __init__(self):
        db.init_db()
        self.users = set(db.read_ratings()["userId"].unique().tolist())
        self._model = None
        self._dirty = True

    def _model_atual(self) -> Recommender:
        if self._dirty or self._model is None:
            self._model = Recommender(db.read_ratings(), db.read_movies())
            self._dirty = False
        return self._model

    def recommend(self, user_id: int, n: int = 10):
        return self._model_atual().recommend(user_id, n)

    def add_user(self) -> int:
        novo = (max(self.users) + 1) if self.users else 1
        self.users.add(novo)
        return novo

    def add_item(self, title: str, genres: str = "(no genres listed)") -> int:
        novo = db.insert_movie(title, genres)
        self._dirty = True
        return novo

    def set_preference(self, user_id: int, movie_id: int, rating: float):
        if not db.movie_exists(movie_id):
            raise ValueError(f"filme {movie_id} nao existe")
        db.upsert_rating(user_id, movie_id, rating)
        self.users.add(user_id)
        self._dirty = True