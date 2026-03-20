# Config Agent

A full-stack configuration management platform with an AI agent for natural language interactions.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌────────┐
│   React UI  │─────▶│  Agent API   │─────▶│ Services API │─────▶│ SQLite │
│  (Vite)     │      │  (LangGraph) │      │  (FastAPI)   │      │   DB   │
│  :5173      │─────▶│  :8001       │      │  :8000       │      └────────┘
└─────────────┘      └──────────────┘      └──────────────┘
       │                    │
       │                    ▼
       │              ┌──────────┐
       └─────────────▶│  Ollama  │
                      │ llama3.1 │
                      └──────────┘
```

- **client/** — React + Vite + TypeScript + Tailwind. Config table with filters + agent chat sidebar.
- **services/** — FastAPI REST API. CRUD operations on configurations stored in SQLite.
- **agent/** — LangGraph ReAct agent using Ollama. Wraps the services API as tools.

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed with `llama3.1:8b` pulled:
  ```bash
  ollama pull llama3.1:8b
  ```

## Setup

### 1. Services API (port 8000)

```bash
cd services
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Seed the database with sample data
cd app && python seed.py && cd ..

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 2. Agent API (port 8001)

```bash
cd agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Make sure Ollama is running: ollama serve
# Start the agent server
uvicorn app.main:app --reload --port 8001
```

### 3. Client (port 5173)

```bash
cd client
npm install
npm run dev
```

Then open http://localhost:5173.

## Seeding the Database

The seed script populates 16 sample configs across 3 services and 3 environments:

```bash
cd services/app
python seed.py
```

Services: `auth-service`, `payment-service`, `order-service`
Environments: `dev`, `staging`, `prod`
Keys: `db_timeout`, `max_retries`, `cache_ttl`, `api_rate_limit`, `log_level`, `batch_size`

## Example Agent Conversations

**Check-then-create flow:**
```
User: Add cache_ttl=600 for auth-service in prod

Agent: Let me check if that config already exists.
       [uses search_config]
       That config doesn't exist yet. I'll create it now.
       [uses create_config]
       Done! Created cache_ttl=600 for auth-service in prod.
```

**Duplicate detection:**
```
User: Create db_timeout=5000 for auth-service in dev

Agent: [uses search_config]
       That config already exists with value "5000".
       Would you like me to update it?
```

**Listing and filtering:**
```
User: Show me all prod configs

Agent: [uses list_configs]
       Here are the production configurations:
       - auth-service/prod/db_timeout = 2000
       - auth-service/prod/log_level = warn
       - auth-service/prod/max_retries = 5
       - payment-service/prod/api_rate_limit = 1000
       - order-service/prod/batch_size = 200
       - order-service/prod/cache_ttl = 900
```

## Oracle Migration Notes

The SQLite schema is designed to be Oracle-compatible. When migrating:

- Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with a sequence + trigger pattern
- Replace `TEXT` with `VARCHAR2(n)`
- Replace `CURRENT_TIMESTAMP` with `SYSTIMESTAMP`
- Replace `?` parameter markers with `:param` named binds
- Swap `aiosqlite` for `oracledb` (async Oracle driver)
- The `CHECK` constraint on `environment` works identically in Oracle

## Environment Variables

See `.env.example` for all configurable values. Each service folder has its own `.env`.
