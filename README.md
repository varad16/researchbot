# ResearchBot — Multi-Source Research Agent

A full-stack research agent that autonomously plans research strategies, searches multiple sources (Wikipedia, ArXiv, web), and synthesizes findings into structured summaries with inline citations.

## Architecture

- **Backend**: Python + FastAPI + LangChain (ReAct agent pattern)
- **Frontend**: React + Vite
- **Storage**: MongoDB (or in-memory for mock mode)
- **Sources**: Wikipedia API, ArXiv API, BeautifulSoup web scraping

## Features

- ReAct agent with tool-use loops (capped at 5 iterations)
- Three research tools: Wikipedia search, ArXiv search, web scraping
- Structured summaries with inline citations `[1]`, `[2]`, ...
- Research history with follow-up questions (conversation memory)
- Slack webhook notifications (optional)
- Mock mode — runs end-to-end with no API keys

## Quick Start

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd researchbot
./scripts/setup.sh

# 2. Configure mode
cp .env.example .env
# Edit .env: set MOCK_MODE=true to run without API keys

# 3. Run backend
cd backend
uvicorn main:app --reload --port 8000

# 4. Run frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Frontend at http://localhost:5173, backend at http://localhost:8000.

## Modes

### Mock mode (`MOCK_MODE=true`)
- No API keys needed
- Returns deterministic stub responses for LLM + sources
- Useful for demos, CI, and local dev

### Real mode (`MOCK_MODE=false`)
- Requires `OPENAI_API_KEY`
- Optional: `MONGODB_URI`, `SLACK_WEBHOOK_URL`
- Uses real Wikipedia + ArXiv APIs

## API

```
POST /research
Body: { "query": "your question", "session_id": "optional" }
Returns: { "summary": "...", "citations": [...], "iterations": N }

GET /history/{session_id}
Returns past queries + summaries for follow-ups
```

## Testing

```bash
cd backend
pytest tests/
```

## Project Structure

```
researchbot/
├── backend/
│   ├── main.py              # FastAPI entrypoint
│   ├── agent/               # ReAct agent + planner
│   ├── tools/               # Wikipedia, ArXiv, web scraping
│   ├── storage/             # MongoDB + in-memory
│   └── tests/
├── frontend/                # React + Vite dashboard
└── scripts/setup.sh
```

## Notes on Metrics

If you want to report metrics (citation accuracy, latency, etc.) on a resume, run the evaluation harness in `backend/tests/test_eval.py` against your own query set and report actual measured numbers.
