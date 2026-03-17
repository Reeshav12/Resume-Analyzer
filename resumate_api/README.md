# ResuMate API

FastAPI backend for the React UI, with Ollama Cloud powering resume parsing and ATS analysis.

## Local run

```bash
python3 -m venv .venv_local
find .venv_local -name '._*' -delete 2>/dev/null || true
.venv_local/bin/pip install -r requirements.txt
cp .env.example .env
# add your OLLAMA_API_KEY to .env
.venv_local/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Environment variables:

```env
DATABASE_URL=postgres://...
DATABASE_PATH=resumate_api.db
CORS_ORIGINS=http://localhost:5173
OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_BASE_URL=https://ollama.com/api
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_TIMEOUT_SECONDS=180
```
