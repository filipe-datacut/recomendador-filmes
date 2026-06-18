# Sistema de Recomendação de Filmes

Sistema de recomendação de filmes servido como API REST, conteinerizado com Docker.
Projeto da disciplina de Ciência de Dados (CEUB).

## Stack

- **Modelo:** filtragem colaborativa item-item (similaridade do cosseno) com fallback
  baseado em conteúdo (gêneros) para o caso de *cold-start* (usuário sem histórico).
- **API:** FastAPI (documentação automática via Swagger em `/docs`).
- **Persistência:** SQLite.
- **Dataset:** MovieLens `ml-latest-small`.
- **Containerização:** Docker.

## Decisões de design

- Filtragem colaborativa pura não recomenda nada para um usuário recém-criado (sem
  avaliações não há vizinhança). Por isso há um fallback baseado em conteúdo/popularidade
  para o *cold-start* — sem ele, o endpoint de recomendação quebraria no caso mais óbvio.

## Endpoints planejados

- `GET /health` — verificação de saúde do serviço.
- `GET /recommendations/{user_id}` — recomendações para um usuário.
- `POST /users` — adiciona um novo usuário.
- `POST /items` — adiciona um novo item (filme).
- `POST /preferences` — registra/atualiza uma avaliação de um usuário.

## Como rodar (local)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://localhost:8000/docs`.

## Status

- [x] Estrutura do projeto e API mínima
- [ ] Carga do dataset MovieLens
- [ ] Modelo de recomendação
- [ ] Endpoints completos
- [ ] Persistência (SQLite)
- [ ] Dockerfile
- [ ] Testes
