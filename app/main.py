from fastapi import FastAPI

app = FastAPI(title="Sistema de Recomendação de Filmes")


@app.get("/health")
def health():
    return {"status": "ok"}
