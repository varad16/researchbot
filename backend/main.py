"""FastAPI entrypoint for ResearchBot."""
import os
from typing import Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.react_agent import ResearchAgent
from storage.history import HistoryStore

load_dotenv()

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = ResearchAgent(mock_mode=MOCK_MODE)
    app.state.history = HistoryStore(mock_mode=MOCK_MODE)
    yield


app = FastAPI(title="ResearchBot", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ResearchResponse(BaseModel):
    summary: str
    citations: list
    iterations: int
    session_id: str


@app.get("/")
def root():
    return {"status": "ok", "mock_mode": MOCK_MODE}


@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    if not req.query.strip():
        raise HTTPException(400, "query cannot be empty")

    session_id = req.session_id or app.state.history.new_session()
    prior = app.state.history.get_session(session_id)

    result = await app.state.agent.run(req.query, prior_context=prior)

    app.state.history.append(session_id, req.query, result)
    return ResearchResponse(
        summary=result["summary"],
        citations=result["citations"],
        iterations=result["iterations"],
        session_id=session_id,
    )


@app.get("/history/{session_id}")
def get_history(session_id: str):
    items = app.state.history.get_session(session_id)
    if items is None:
        raise HTTPException(404, "session not found")
    return {"session_id": session_id, "items": items}
