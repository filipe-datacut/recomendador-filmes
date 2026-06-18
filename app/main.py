from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.service import RecommenderService

app = FastAPI(title="Sistema de Recomendacao de Filmes")
service = RecommenderService()


class NovoItem(BaseModel):
    title: str
    genres: str = "(no genres listed)"


class Preferencia(BaseModel):
    user_id: int
    movie_id: int
    rating: float = Field(ge=0.5, le=5.0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/recommendations/{user_id}")
def recomendar(user_id: int, n: int = 10):
    return {"user_id": user_id, "recommendations": service.recommend(user_id, n)}


@app.post("/users")
def adicionar_usuario():
    return {"userId": service.add_user()}


@app.post("/items")
def adicionar_item(item: NovoItem):
    movie_id = service.add_item(item.title, item.genres)
    return {"movieId": movie_id, "title": item.title, "genres": item.genres}


@app.post("/preferences")
def definir_preferencia(pref: Preferencia):
    try:
        service.set_preference(pref.user_id, pref.movie_id, pref.rating)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok", **pref.model_dump()}