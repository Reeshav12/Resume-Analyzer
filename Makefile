.PHONY: help api-setup api-run web-install web-run

help:
	@printf "\nResuMate local commands\n\n"
	@printf "  make api-setup   Create the backend venv and install Python deps\n"
	@printf "  make api-run     Start the FastAPI server on http://127.0.0.1:8000\n"
	@printf "  make web-install Install frontend npm deps\n"
	@printf "  make web-run     Start the Vite dev server on http://127.0.0.1:5173\n\n"
	@printf "Run the API and web server in separate terminals.\n"

api-setup:
	cd resumate_api && python3 -m venv .venv_local
	find resumate_api/.venv_local -name '._*' -delete 2>/dev/null || true
	cd resumate_api && .venv_local/bin/pip install -r requirements.txt

api-run:
	cd resumate_api && .venv_local/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

web-install:
	bash -lc 'export NVM_DIR="$$HOME/.nvm"; [ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh"; cd resumate_web && npm install'

web-run:
	bash -lc 'export NVM_DIR="$$HOME/.nvm"; [ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh"; cd resumate_web && npm run dev -- --host 127.0.0.1'
