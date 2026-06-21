# Sistema de Recomendação de Filmes

API REST de recomendação de filmes, com modelo de filtragem colaborativa,
persistência em SQLite e empacotamento em Docker. Projeto da disciplina de
Ciência de Dados — CEUB.

## Visão geral

- **Modelo:** filtragem colaborativa item-item (similaridade do cosseno) com
  fallback de cold-start.
- **API:** FastAPI, com documentação automática (Swagger) em `/docs`.
- **Persistência:** SQLite.
- **Dataset:** MovieLens `ml-latest-small` (~100 mil avaliações, 610 usuários,
  9.742 filmes).
- **Containerização:** Docker.

## Como obter os dados

O dataset não é versionado (é externo). Baixe e posicione:

1. Baixe `https://files.grouplens.org/datasets/movielens/ml-latest-small.zip`
2. Extraia e mova a pasta `ml-latest-small` para `data/`, de forma que exista
   `data/ml-latest-small/ratings.csv`.

Na primeira execução, esses CSVs são carregados para um banco SQLite
(`data/app.db`), que passa a ser a fonte de dados. O banco não é versionado e se
regenera sozinho a partir do CSV.

## Como executar

### Local (Python)

```bash
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://localhost:8000/docs`.

### Docker

```bash
docker build -t recomendador .
docker run -p 8000:8000 recomendador
```

Acesse `http://localhost:8000/docs`.

## Endpoints

- `GET /health` — verificação de saúde do serviço.
- `GET /recommendations/{user_id}?n=10` — recomendações para um usuário.
- `POST /users` — adiciona um novo usuário (retorna o id).
- `POST /items` — adiciona um novo filme (`title`, `genres`).
- `POST /preferences` — registra/atualiza a avaliação de um usuário
  (`user_id`, `movie_id`, `rating`).

## Modelo e decisões de design

### Filtragem colaborativa item-item

Cada filme é representado pelo vetor de notas que recebeu dos usuários; a
similaridade entre dois filmes é a similaridade do cosseno entre esses vetores.
A nota prevista de um filme para um usuário é a média das notas que ele deu,
ponderada pela similaridade entre o candidato e os filmes que ele já avaliou.

### Proteção contra a patologia de esparsidade

A versão ingênua do modelo sofre de um problema conhecido: filmes avaliados por
pouquíssimos usuários ganham similaridade degenerada (próxima de 1) e nota
prevista perfeita (5.0), dominando o topo com títulos obscuros. Duas correções
foram aplicadas:

- **Significance weighting:** cada similaridade é amortecida por um fator
  proporcional ao número de usuários que avaliaram ambos os filmes —
  similaridades calculadas a partir de poucas co-avaliações valem menos.
- **Suporte mínimo:** um filme só pode ser recomendado se tiver um número
  mínimo de avaliações (padrão: 20).

### Cold-start

Filtragem colaborativa não consegue recomendar nada para um usuário sem
histórico (sem avaliações, não há vizinhança a calcular). Nesse caso, o sistema
usa um fallback de popularidade baseado em **nota ponderada bayesiana** (no
estilo do ranking do IMDb): a média de cada filme é puxada em direção à média
global na proporção de quão poucas avaliações ele tem, evitando que um filme de
uma única nota 5 vença um clássico com centenas de avaliações. O suporte mínimo
também se aplica aqui. Cada recomendação informa qual estratégia a gerou
(`colaborativa` ou `popularidade`).

### Reconstrução preguiçosa do modelo

Reconstruir a matriz de similaridade a cada nova avaliação seria caro. As
mutações (novo usuário, novo filme, nova avaliação) apenas marcam o modelo como
desatualizado; ele é reconstruído (relendo do banco) somente na próxima
recomendação. Adicionar dados é instantâneo, e o custo da reconstrução ocorre
uma única vez após uma mudança.

### Persistência e configuração

Os dados ficam em SQLite. O caminho do banco é configurável pela variável de
ambiente `RECOMMENDER_DB`, o que permite que os testes usem um banco temporário
descartável sem tocar no banco real.

### Validação

As requisições são validadas automaticamente pelo FastAPI/Pydantic: a nota é
restrita ao intervalo do MovieLens (0.5–5.0; fora disso a API retorna 422), e
avaliar um filme inexistente retorna 404.

## Testes

```bash
pip install pytest httpx
python -m pytest -q
```

Inclui testes unitários do recomendador (não recomenda itens já vistos, respeita
o suporte mínimo, cold-start usa popularidade) e testes de integração da API
(contratos dos endpoints e códigos de status). Os testes rodam contra um banco
temporário, sem afetar o banco real.

## Estrutura do projeto

```
app/
  dataset.py      # carga dos CSVs do MovieLens
  recommender.py  # modelo de recomendacao (CF item-item + cold-start)
  db.py           # persistencia em SQLite
  service.py      # estado + reconstrucao preguicosa do modelo
  main.py         # API FastAPI
tests/            # testes unitarios e de integracao
data/             # dataset e banco (nao versionados)
Dockerfile
.dockerignore
requirements.txt
```

## Avaliação offline

O recomendador foi avaliado com um protocolo de hold-out: 20% das avaliações de
cada usuário (com 10+ avaliações) foram escondidas como conjunto de teste, o
modelo treinado no restante, e mediu-se quantos itens relevantes (nota >= 4)
escondidos aparecem nas top-10 recomendações.

Resultados (603 usuários, via `python -m app.evaluate`):

- **Precision@10:** 0.0181
- **Recall@10:** 0.0106

Os valores são modestos por construção. O suporte mínimo torna o modelo
deliberadamente conservador — ele se recusa a recomendar itens com poucas
avaliações, que é justamente a proteção que elimina o lixo de nicho do topo.
Há, portanto, um tradeoff explícito entre confiabilidade e cobertura: muitos
itens relevantes escondidos têm pouco suporte no conjunto de treino e nunca
entram como candidatos, o que limita o recall. Reportar a métrica torna esse
comportamento mensurável em vez de suposto.