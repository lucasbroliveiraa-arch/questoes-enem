# Questões ENEM — Plataforma de Estudo

API + frontend para praticar questões reais do ENEM (2009–2023), com banco de
dados próprio, estatísticas persistidas e visual inspirado no cartão-resposta
do ENEM.

> Este projeto evoluiu de um MVP em HTML autocontido para uma arquitetura
> com backend/API + banco. Veja `docs/04-arquitetura-v2.md` para o histórico
> completo dessa decisão.

## Estrutura

```
questoes-enem/
├── backend/
│   ├── app/            # aplicação FastAPI (models, schemas, routers, services)
│   ├── alembic/         # migrations do banco
│   ├── tests/           # pytest
│   ├── pipeline/        # consolida os CSVs de origem e popula o banco
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js        # consome a API via fetch
├── docker-compose.yml    # sobe backend + Postgres
├── docs/                 # histórico e decisões do projeto
└── dist/                 # (opcional) build estático do MVP anterior, se mantido
```

## Pré-requisitos

- Docker + Docker Compose
- Python 3.12+ (só necessário se for rodar o pipeline de seed fora do container)

## Como rodar do zero

### 1. Subir backend + banco

```bash
docker compose up -d
```

Isso sobe o Postgres (porta 5432) e a API FastAPI (porta 8000,
docs interativas em http://localhost:8000/docs).

### 2. Rodar as migrations

```bash
docker compose exec backend alembic upgrade head
```

### 3. Popular o banco com as questões

O pipeline de seed lê o repositório público de dados
[`gabriel-antonelli/extract-enem-data`](https://github.com/gabriel-antonelli/extract-enem-data)
(licença GPL-3.0). Clone-o localmente (fora do container, ele não precisa
entrar na imagem Docker):

```bash
git clone --depth 1 https://github.com/gabriel-antonelli/extract-enem-data.git data-source
```

Depois rode o seed (dentro do container, para já usar o Postgres do compose):

```bash
docker compose exec backend python -m pipeline.seed_db --source /app/../data-source/enem-data --reset
```

> Se preferir rodar o seed fora do Docker (ex.: apontando `DATABASE_URL` para
> `localhost`), instale as dependências com `pip install -r backend/requirements.txt`
> e rode `python -m pipeline.seed_db --source <caminho>/enem-data` de dentro
> de `backend/`.

### 4. Rodar o frontend

O frontend é estático — não precisa de build. Sirva a pasta `frontend/` com
qualquer servidor HTTP simples (abrir direto como `file://` pode esbarrar em
restrições de CORS do navegador):

```bash
cd frontend
python -m http.server 5500
```

Acesse http://localhost:5500. Por padrão, `js/app.js` aponta para a API em
`http://localhost:8000` (ajuste `API_BASE` se mudar a porta).

## Rodando os testes

```bash
cd backend
pip install -r requirements.txt
pytest
```

Os testes usam SQLite em memória (não precisam do Postgres rodando).

## Fonte dos dados

Questões e imagens vêm do repositório
[`gabriel-antonelli/extract-enem-data`](https://github.com/gabriel-antonelli/extract-enem-data)
(GPL-3.0): CSVs por ano/área e pastas de imagens por questão.

## Limitações conhecidas

- Não há campo de assunto fino (ex. "Genética", "Funções") no dataset de
  origem — só a área ampla do ENEM.
- 7 arquivos de imagem do repositório de origem estavam corrompidos e não
  puderam ser recuperados; essas questões ficam sem imagem.
- Sem autenticação de usuário no v1 — estatísticas são globais, não por
  pessoa (ver `docs/04-arquitetura-v2.md` para o plano de evolução).
