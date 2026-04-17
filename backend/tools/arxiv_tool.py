"""ArXiv search tool with mock fallback."""
from typing import Dict


class ArxivTool:
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def search(self, query: str) -> Dict[str, str]:
        if self.mock_mode:
            return {
                "title": f"A Survey of {query.title()} (mock paper)",
                "url": "https://arxiv.org/abs/0000.00000",
                "snippet": f"Recent research on {query} has explored multiple methodological directions. "
                           f"This is a mock abstract used when MOCK_MODE=true.",
            }
        import arxiv
        try:
            search = arxiv.Search(query=query, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
            for result in search.results():
                return {
                    "title": result.title,
                    "url": result.entry_id,
                    "snippet": result.summary[:800],
                }
            return {"title": "", "url": "", "snippet": "No results."}
        except Exception as e:
            return {"title": "", "url": "", "snippet": f"ArXiv error: {e}"}
