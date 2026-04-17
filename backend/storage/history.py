"""History storage — MongoDB in real mode, in-memory dict in mock mode."""
import os
import uuid
from typing import Dict, List, Optional


class HistoryStore:
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self._memory: Dict[str, List] = {}
        self.collection = None
        if not mock_mode:
            try:
                from pymongo import MongoClient
                client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
                db = client[os.getenv("MONGODB_DB", "researchbot")]
                self.collection = db["history"]
            except Exception:
                # Fall back to in-memory if Mongo unreachable
                self.collection = None

    def new_session(self) -> str:
        return str(uuid.uuid4())

    def append(self, session_id: str, query: str, result: dict) -> None:
        entry = {
            "query": query,
            "summary": result["summary"],
            "citations": result["citations"],
            "iterations": result["iterations"],
        }
        if self.collection is not None:
            self.collection.update_one(
                {"session_id": session_id},
                {"$push": {"items": entry}},
                upsert=True,
            )
        else:
            self._memory.setdefault(session_id, []).append(entry)

    def get_session(self, session_id: str) -> Optional[List]:
        if self.collection is not None:
            doc = self.collection.find_one({"session_id": session_id})
            return doc["items"] if doc else []
        return self._memory.get(session_id, [])
