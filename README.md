# taskManager

Projeto simples de organizador de tarefas (to‑do/project manager) construído com FastAPI + SQLModel. O objetivo é demonstrar padrões comuns como autenticação/login, uso de decorators (dependências), projetos, participantes e tarefas.

**Principais conceitos**

- Autenticação com JWT (login / refresh token).
- Modelagem: `User`, `Project`, `Task`, e tabela de associação `ProjectUserLink` para participantes.
- Separação clara entre schemas Pydantic (entrada/saída) e modelos de banco (SQLModel table=True).
- Boas práticas: hashing de senhas com Passlib, validações, e migrations via Alembic.

**Requisitos**

- Python 3.10+
- PostgreSQL

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

- Configure `DATABASE_URL` no `.env`. 
- PostgreSQL

```text
DATABASE_URL=postgresql://postgres:senha@localhost:5432/newjira
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

**Inicializar o Alembic (quando necessário)**

Se o seu repositório ainda não tem a pasta `alembic/` (migrations), você pode inicializar o Alembic localmente e gerar as primeiras migrations:

```powershell
& .\.venv\Scripts\Activate.ps1
# inicializa a estrutura (cria pasta alembic/ e alembic.ini)
alembic init alembic

# editar alembic.ini para apontar para sua DATABASE_URL ou usar variáveis de ambiente
# e ajustar alembic/env.py para que `target_metadata` aponte para `SQLModel.metadata` do seu projeto

# gerar uma migration inicial (autogenerate usa target_metadata para comparar modelos)
alembic revision --autogenerate -m "init"

# aplicar migrations no banco
alembic upgrade head
```

Boas práticas com Alembic

- Sempre revise o arquivo de migration gerado em `alembic/versions/*.py` antes de aplicar (`alembic upgrade head`). Autogenerate pode inferir tipos incorretos (ex.: INTEGER vs UUID).
- Mantenha a pasta `alembic/` e os arquivos dentro de `alembic/versions/` versionados no Git — as migrations devem ser parte do histórico do código.
- Não ignore `alembic/` no Git: remover/ignorar as migrations impede que outros desenvolvedores apliquem as mesmas alterações e quebra o histórico do schema.
- É aceitável ignorar `alembic.ini` se ele contiver valores locais sensíveis, mas prefira mantê-lo com placeholders e controlar a URL do DB via `.env`.

---

## Executar com Docker

**Pré-requisitos**: Docker e Docker Compose instalados.

**Usando banco de dados local (PostgreSQL no host)**

Se você já tem um banco PostgreSQL rodando localmente no Windows e quer que o container acesse esse banco:

1. **Ajustar DATABASE_URL no `.env`**

Substitua `localhost` por `host.docker.internal` (funciona no Docker Desktop para Windows/Mac):

```env
DATABASE_URL=postgresql://postgres:senha@host.docker.internal:5432/newjira
```

2. **Build e run com docker-compose**

```powershell
docker-compose up --build
```

O container irá:
- Acessar o banco via `host.docker.internal`
- Rodar migrations automaticamente (`alembic upgrade head`)
- Iniciar a aplicação na porta 8000

3. **Acessar a aplicação**

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

**Hot-reload durante desenvolvimento**

O `docker-compose.yaml` já está configurado com volume mount (`.:/app`), então mudanças no código serão refletidas automaticamente.

**Parar os containers**

```powershell
docker-compose down
```

**Troubleshooting Docker**

- Se o container não conseguir conectar ao banco local, verifique:
  - PostgreSQL está aceitando conexões externas (escutando em `0.0.0.0` e não apenas `127.0.0.1`)
  - Firewall do Windows permite conexões na porta 5432
  - Use `host.docker.internal` no DATABASE_URL (não `localhost`)

- Para ver logs do container:
```powershell
docker-compose logs -f fastapi-app
```

