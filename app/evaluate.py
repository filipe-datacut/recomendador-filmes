"""Avaliacao offline do recomendador (precision@k e recall@k).

Esconde uma fracao das avaliacoes de cada usuario (teste), treina o modelo no
restante e mede quantos itens relevantes escondidos aparecem nas top-k
recomendacoes.
"""
import numpy as np
import pandas as pd

from app.dataset import load_ratings, load_movies
from app.recommender import Recommender


def split_train_test(ratings, test_frac=0.2, min_ratings=10, seed=42):
    rng = np.random.default_rng(seed)
    treino, teste = [], []
    for _, grp in ratings.groupby("userId"):
        if len(grp) < min_ratings:
            treino.append(grp)
            continue
        idx = rng.permutation(len(grp))
        n_test = max(1, int(len(grp) * test_frac))
        teste_idx = grp.index[idx[:n_test]]
        teste.append(grp.loc[teste_idx])
        treino.append(grp.drop(teste_idx))
    vazio = ratings.iloc[0:0]
    treino_df = pd.concat(treino) if treino else vazio
    teste_df = pd.concat(teste) if teste else vazio
    return treino_df, teste_df


def evaluate(k=10, relevancia=4.0):
    ratings = load_ratings()
    movies = load_movies()
    treino, teste = split_train_test(ratings)
    rec = Recommender(treino, movies)

    relevantes_por_usuario = (teste[teste.rating >= relevancia]
                              .groupby("userId")["movieId"].apply(set))

    precisions, recalls = [], []
    for uid, relevantes in relevantes_por_usuario.items():
        if not relevantes:
            continue
        recs = rec.recommend(int(uid), n=k)
        recomendados = {r["movieId"] for r in recs}
        acertos = len(recomendados & relevantes)
        precisions.append(acertos / k)
        recalls.append(acertos / len(relevantes))

    if not precisions:
        print("Sem usuarios suficientes para avaliar.")
        return

    print(f"Usuarios avaliados: {len(precisions)}")
    print(f"Precision@{k}: {np.mean(precisions):.4f}")
    print(f"Recall@{k}:    {np.mean(recalls):.4f}")


if __name__ == "__main__":
    evaluate(k=10)