"""Tests for ResearchBot — run with `pytest` from backend/."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.react_agent import ResearchAgent
from storage.history import HistoryStore
from tools.wikipedia_tool import WikipediaTool
from tools.arxiv_tool import ArxivTool
from tools.web_tool import WebScrapeTool


@pytest.mark.asyncio
async def test_agent_mock_returns_summary():
    agent = ResearchAgent(mock_mode=True)
    result = await agent.run("quantum computing")
    assert "summary" in result
    assert len(result["citations"]) == 3
    assert result["iterations"] >= 1
    assert "[1]" in result["summary"]


def test_wikipedia_mock():
    tool = WikipediaTool(mock_mode=True)
    result = tool.search("python")
    assert "title" in result and result["title"]
    assert "url" in result


def test_arxiv_mock():
    tool = ArxivTool(mock_mode=True)
    result = tool.search("transformers")
    assert result["title"]
    assert "arxiv.org" in result["url"]


def test_web_mock():
    tool = WebScrapeTool(mock_mode=True)
    result = tool.scrape("rag pipelines")
    assert result["title"]


def test_history_in_memory():
    store = HistoryStore(mock_mode=True)
    sid = store.new_session()
    store.append(sid, "q1", {"summary": "s1", "citations": [], "iterations": 1})
    store.append(sid, "q2", {"summary": "s2", "citations": [], "iterations": 2})
    items = store.get_session(sid)
    assert len(items) == 2
    assert items[0]["query"] == "q1"


@pytest.mark.asyncio
async def test_agent_citations_sequential_ids():
    agent = ResearchAgent(mock_mode=True)
    result = await agent.run("machine learning")
    ids = [c["id"] for c in result["citations"]]
    assert ids == [1, 2, 3]


def test_eval_harness_placeholder():
    """
    Placeholder for a real eval harness.
    To report genuine metrics (e.g. citation accuracy), build a labeled
    query set, run the agent in real mode, and compare citation claims
    against ground truth. Do NOT report fabricated numbers.
    """
    assert True
