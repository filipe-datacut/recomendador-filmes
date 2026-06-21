from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_recommendations_estrutura():
    r = client.get("/recommendations/1?n=5")
    assert r.status_code == 200
    body = r.json()
    assert "recommendations" in body
    assert isinstance(body["recommendations"], list)


def test_adicionar_usuario():
    r = client.post("/users")
    assert r.status_code == 200
    assert "userId" in r.json()


def test_adicionar_item():
    r = client.post("/items", json={"title": "Filme de Teste", "genres": "Acao"})
    assert r.status_code == 200
    assert "movieId" in r.json()


def test_preferencia_filme_inexistente_da_404():
    r = client.post("/preferences",
                    json={"user_id": 1, "movie_id": 999999, "rating": 5.0})
    assert r.status_code == 404


def test_preferencia_nota_invalida_da_422():
    r = client.post("/preferences",
                    json={"user_id": 1, "movie_id": 1, "rating": 9.0})
    assert r.status_code == 422