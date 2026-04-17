#!/usr/bin/env bash
set -e

echo "==> Setting up ResearchBot"

# Python venv + deps
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env (mock mode enabled by default)"
fi

# Frontend
cd frontend
npm install
cd ..

echo "==> Done. Next:"
echo "   cd backend && uvicorn main:app --reload"
echo "   cd frontend && npm run dev"
