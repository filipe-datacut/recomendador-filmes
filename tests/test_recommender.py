import numpy as np
import pandas as pd
import pytest

from app.recommender import Recommender


@pytest.fixture
def rec():
    rng = np.random.default_rng(0)
    rows = []
    for u in range(1, 61):
        for m in range(1, 21):
            if rng.random() < 0.6:
                rows.append((u, m, float(rng.integers(1, 6))))
    ratings = pd.DataFrame(rows, columns=["userId", "movieId", "rating"])
    movies = pd.DataFrame({"movieId": list(range(1, 21)),
                           "title": [f"Filme {i}" for i in range(1, 21)],
                           "genres": ["Acao"] * 20})
    return Recommender(ratings, movies, min_support=5, shrinkage=10)


def test_recommend_retorna_lista_formatada(rec):
    recs = rec.recommend(1, n=5)
    assert isinstance(recs, list)
    assert len(recs) <= 5
    for r in recs:
        assert {"movieId", "title", "score", "estrategia"} <= r.keys()


def test_nao_recomenda_filme_ja_visto(rec):
    vistos = set(rec.matrix.loc[1].dropna().index)
    recs = rec.recommend(1, n=10)
    assert all(r["movieId"] not in vistos for r in recs)


def test_respeita_suporte_minimo(rec):
    recs = rec.recommend(1, n=10)
    assert all(r["n_avaliacoes"] >= rec.min_support for r in recs)


def test_cold_start_usa_popularidade(rec):
    recs = rec.recommend(999999, n=5)
    assert len(recs) > 0
    assert all(r["estrategia"] == "popularidade" for r in recs)