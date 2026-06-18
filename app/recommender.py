import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:
    """Filtragem colaborativa item-item com protecoes contra esparsidade.

    - significance weighting: amortece similaridades de poucas co-avaliacoes;
    - suporte minimo: so recomenda itens com volume minimo de avaliacoes;
    - cold-start: usuario sem historico recebe os mais populares (nota
      ponderada bayesiana, robusta a poucas avaliacoes).
    """

    def __init__(self, ratings: pd.DataFrame, movies: pd.DataFrame,
                 min_support: int = 20, shrinkage: int = 25):
        self.movies = movies.set_index("movieId")
        self.matrix = ratings.pivot_table(index="userId", columns="movieId", values="rating")
        self.movie_ids = self.matrix.columns.to_numpy()
        self.min_support = min_support

        filled = self.matrix.fillna(0).to_numpy(dtype=np.float32)   # usuarios x itens
        sim = cosine_similarity(filled.T)

        seen = (filled > 0).astype(np.float32)
        co_counts = seen.T @ seen
        shrink = np.minimum(co_counts, shrinkage) / shrinkage
        self.item_sim = sim * shrink

        self.item_counts = seen.sum(axis=0)                         # avaliacoes por item

        # popularidade: nota ponderada bayesiana
        sums = filled.sum(axis=0)
        means = np.divide(sums, self.item_counts,
                          out=np.zeros_like(sums), where=self.item_counts > 0)
        C = sums.sum() / self.item_counts.sum()                     # media global
        m = float(min_support)
        v = self.item_counts
        self.weighted_rating = (v / (v + m)) * means + (m / (v + m)) * C
        self.weighted_rating[self.item_counts < min_support] = -np.inf  # so populares com volume real
        order = np.argsort(self.weighted_rating)[::-1]
        self._pop_order = [i for i in order if np.isfinite(self.weighted_rating[i])]

    def _format(self, i):
        mid = int(self.movie_ids[i])
        title = self.movies.loc[mid, "title"] if mid in self.movies.index else "?"
        return {"movieId": mid, "title": title,
                "n_avaliacoes": int(self.item_counts[i])}

    def popular(self, n: int = 10):
        out = []
        for i in self._pop_order[:n]:
            row = self._format(i)
            row["score"] = round(float(self.weighted_rating[i]), 3)
            row["estrategia"] = "popularidade"
            out.append(row)
        return out

    def recommend(self, user_id: int, n: int = 10):
        if user_id not in self.matrix.index or self.matrix.loc[user_id].notna().sum() == 0:
            return self.popular(n)                                  # cold-start

        user_row = self.matrix.loc[user_id]
        rated_mask = user_row.notna().to_numpy()
        ratings_vec = user_row.fillna(0).to_numpy(dtype=np.float32)

        sim_to_rated = self.item_sim[:, rated_mask]
        numer = sim_to_rated @ ratings_vec[rated_mask]
        denom = np.abs(sim_to_rated).sum(axis=1)
        scores = np.divide(numer, denom, out=np.zeros_like(numer), where=denom != 0)

        scores[rated_mask] = -np.inf
        scores[self.item_counts < self.min_support] = -np.inf

        order = np.argsort(scores)[::-1]
        order = [i for i in order if np.isfinite(scores[i])][:n]

        if not order:                                               # usuario existe mas sem base util
            return self.popular(n)

        out = []
        for i in order:
            row = self._format(i)
            row["score"] = round(float(scores[i]), 3)
            row["estrategia"] = "colaborativa"
            out.append(row)
        return out


if __name__ == "__main__":
    from app.dataset import load_ratings, load_movies

    rec = Recommender(load_ratings(), load_movies())
    print("=== usuario existente (1) ===")
    for r in rec.recommend(1, n=5):
        print(r)
    print("\n=== usuario novo (99999) -> cold-start ===")
    for r in rec.recommend(99999, n=5):
        print(r)