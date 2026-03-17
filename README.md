# ResuMate (React + FastAPI)

This workspace contains the active ResuMate application:

- Frontend: `resumate_web/` (React + Vite)
- Backend: `resumate_api/` (FastAPI + Ollama Cloud analysis)

## Requirements

- Python 3.9+
- Node.js 20+ (`.nvmrc` is included)

## Local run

Open two terminals from the project root.

### 1) Start the API

```bash
make api-setup
make api-run
```

The API will run at `http://127.0.0.1:8000`.

Create `resumate_api/.env` from `resumate_api/.env.example` and add your Ollama key before using `/analyze`.

### 2) Start the React UI

```bash
make web-install
make web-run
```

The frontend will run at `http://127.0.0.1:5173`.
The dev server proxies `/api/*` to `http://127.0.0.1:8000`.

## Without make

If you prefer the direct commands:

```bash
cd resumate_api
python3 -m venv .venv_local
find .venv_local -name '._*' -delete 2>/dev/null || true
.venv_local/bin/pip install -r requirements.txt
cp .env.example .env
# add OLLAMA_API_KEY in resumate_api/.env
.venv_local/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd resumate_web
npm install
npm run dev -- --host 127.0.0.1
```

## Deploy on Render

The root `render.yaml` deploys:

- `resumate-api` (Python web service)
- `resumate-web` (static site)
- `resumate-db` (free Postgres database)

After the first deploy, verify `VITE_API_BASE_URL` points to the real API URL for your Render service.

Set these backend env vars on Render:

- `OLLAMA_API_KEY`
- `OLLAMA_BASE_URL` (`https://ollama.com/api` by default)
- `OLLAMA_MODEL` (`gpt-oss:120b` by default)
