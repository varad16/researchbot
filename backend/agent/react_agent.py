"""ReAct-style research agent with tool-use loop."""
import os
import re
from typing import List, Dict, Any

from tools.wikipedia_tool import WikipediaTool
from tools.arxiv_tool import ArxivTool
from tools.web_tool import WebScrapeTool


class ResearchAgent:
    """
    Minimal ReAct loop:
      Thought -> Action(tool, input) -> Observation -> ... -> Final Answer

    In mock mode, returns deterministic canned reasoning + citations so the
    system is demo-able end-to-end without any API keys.
    """

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))
        self.tools = {
            "wikipedia": WikipediaTool(mock_mode=mock_mode),
            "arxiv": ArxivTool(mock_mode=mock_mode),
            "web": WebScrapeTool(mock_mode=mock_mode),
        }
        if not mock_mode:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
                temperature=0.1,
            )
        else:
            self.llm = None

    async def run(self, query: str, prior_context: List[Dict] = None) -> Dict[str, Any]:
        if self.mock_mode:
            return self._run_mock(query)
        return await self._run_real(query, prior_context or [])

    # ---------- MOCK ----------
    def _run_mock(self, query: str) -> Dict[str, Any]:
        """Walk through all three tools and build a fake-but-structured summary."""
        citations = []
        trace = []

        wiki = self.tools["wikipedia"].search(query)
        citations.append({"id": 1, "source": "wikipedia", "title": wiki["title"], "url": wiki["url"]})
        trace.append(f"Searched Wikipedia, found: {wiki['title']}")

        arxiv = self.tools["arxiv"].search(query)
        citations.append({"id": 2, "source": "arxiv", "title": arxiv["title"], "url": arxiv["url"]})
        trace.append(f"Searched ArXiv, found: {arxiv['title']}")

        web = self.tools["web"].scrape(query)
        citations.append({"id": 3, "source": "web", "title": web["title"], "url": web["url"]})
        trace.append(f"Scraped web, found: {web['title']}")

        summary = (
            f"Based on research into \"{query}\":\n\n"
            f"According to Wikipedia [1], {wiki['snippet']}\n\n"
            f"Recent academic work on ArXiv [2] suggests that {arxiv['snippet']}\n\n"
            f"Additional context from the web [3] indicates {web['snippet']}\n\n"
            f"Synthesis: The topic is multi-faceted, with foundational definitions in [1], "
            f"research directions in [2], and applied perspectives in [3]."
        )

        return {
            "summary": summary,
            "citations": citations,
            "iterations": 3,
            "trace": trace,
        }

    # ---------- REAL ----------
    async def _run_real(self, query: str, prior_context: List[Dict]) -> Dict[str, Any]:
        from langchain_core.messages import SystemMessage, HumanMessage

        system = (
            "You are a research agent. Use tools to gather evidence, then answer.\n"
            "Available tools: wikipedia, arxiv, web.\n"
            "Format each step exactly as:\n"
            "Thought: <your reasoning>\n"
            "Action: <tool_name>\n"
            "Action Input: <query>\n"
            "or, when done:\n"
            "Thought: I have enough information.\n"
            "Final Answer: <summary with [1], [2] style citations>"
        )

        scratchpad = ""
        citations: List[Dict] = []
        iterations = 0

        for i in range(self.max_iterations):
            iterations = i + 1
            prompt = (
                f"Question: {query}\n\n"
                f"{scratchpad}\n"
                "What is your next Thought and Action?"
            )
            resp = self.llm.invoke([SystemMessage(content=system), HumanMessage(content=prompt)])
            text = resp.content
            scratchpad += "\n" + text

            if "Final Answer:" in text:
                summary = text.split("Final Answer:", 1)[1].strip()
                return {
                    "summary": summary,
                    "citations": citations,
                    "iterations": iterations,
                    "trace": scratchpad.splitlines(),
                }

            action_match = re.search(r"Action:\s*(\w+)", text)
            input_match = re.search(r"Action Input:\s*(.+)", text)
            if not (action_match and input_match):
                break

            tool_name = action_match.group(1).strip().lower()
            tool_input = input_match.group(1).strip()
            tool = self.tools.get(tool_name)
            if not tool:
                scratchpad += f"\nObservation: unknown tool {tool_name}"
                continue

            if tool_name == "wikipedia":
                obs = tool.search(tool_input)
            elif tool_name == "arxiv":
                obs = tool.search(tool_input)
            else:
                obs = tool.scrape(tool_input)

            citations.append({
                "id": len(citations) + 1,
                "source": tool_name,
                "title": obs.get("title", ""),
                "url": obs.get("url", ""),
            })
            scratchpad += f"\nObservation: {obs.get('snippet', '')[:500]}"

        return {
            "summary": f"(Reached max iterations)\n\nPartial trace:\n{scratchpad}",
            "citations": citations,
            "iterations": iterations,
            "trace": scratchpad.splitlines(),
        }
