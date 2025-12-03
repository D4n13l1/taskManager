# taskManager

Projeto simples de organizador de tarefas (to‑do/project manager) construído com FastAPI + SQLModel. O objetivo é demonstrar padrões comuns como autenticação/login, uso de decorators (dependências), projetos, participantes e tarefas.

**Principais conceitos**

- Autenticação com JWT (login / refresh token).
- Modelagem: `User`, `Project`, `Task`, e tabela de associação `ProjectUserLink` para participantes.
- Separação clara entre schemas Pydantic (entrada/saída) e modelos de banco (SQLModel table=True).
- Boas práticas: hashing de senhas com Passlib, validações, e migrations via Alembic.

**Requisitos**

- Python 3.10+ (recomenda-se usar virtualenv/venv)
- PostgreSQL (ou SQLite para desenvolvimento rápido)
- Git, Docker (opcional)

**Como configurar o ambiente (PowerShell)**

1. Criar e ativar virtualenv

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

2. Instalar dependências

```powershell
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente

- Copie o arquivo de exemplo de ambiente e crie um `.env` na raiz:

```powershell
# se existir um .env.example
copy .env.example .env
# ou criar manualmente e editar
notepad .env
```

- Configure `DATABASE_URL` no `.env`. Exemplos:
  - PostgreSQL sem schema customizado:

```text
DATABASE_URL=postgresql://postgres:senha@localhost:5432/newjira
```

- PostgreSQL

```text
DATABASE_URL=postgresql://postgres:senha@localhost:5432/newjira
```

> NÃO use `?schema=newjira` na query string — psycopg2 não aceita `schema` como opção.

- Se usar Alembic, atualize também `alembic.ini` (a chave `sqlalchemy.url`) para apontar para a mesma URL do banco.

4. (Opcional) Rodar PostgreSQL via Docker (dev)

```powershell
docker run --name newjira-postgres -e POSTGRES_PASSWORD=1234 -e POSTGRES_USER=postgres -e POSTGRES_DB=newjira -p 5432:5432 -d postgres:15
```

**Aplicar migrations (Alembic)**

1. Verifique o `alembic/env.py` e confirme que `target_metadata` aponta para `SQLModel.metadata`.
2. Gerar/rodar migrations:

```powershell
& .\.venv\Scripts\Activate.ps1
alembic revision --autogenerate -m "init"
alembic upgrade head
```

> Antes de rodar `alembic upgrade head`, revise o arquivo gerado em `alembic/versions/*.py` para garantir que os tipos (ex.: UUID) e FKs estão corretos.

**Criar usuário admin (seed)**

Há um script de seed em `scripts/seed_admin.py` que cria/atualiza um admin com senha `123456` (apenas para desenvolvimento). Execute:

```powershell
& .\.venv\Scripts\Activate.ps1
# garantir que PYTHONPATH inclui a raiz (ou rode como módulo)
$env:PYTHONPATH = (Get-Location)
python .\scripts\seed_admin.py
```

Ou (se preferir) torne `scripts` um package e rode como módulo:

```powershell
# criar scripts\__init__.py (pode ser vazio) e então:
python -m scripts.seed_admin
```

**Rodar a aplicação**

```powershell
& .\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`. A documentação interativa está em `http://127.0.0.1:8000/docs`.
