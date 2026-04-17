"""Wikipedia search tool with mock fallback."""
from typing import Dict


class WikipediaTool:
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def search(self, query: str) -> Dict[str, str]:
        if self.mock_mode:
            return {
                "title": f"{query.title()} (mock Wikipedia entry)",
                "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                "snippet": f"{query} is a topic with a well-established definition and history. "
                           f"This is a mock snippet used when MOCK_MODE=true.",
            }
        import wikipedia
        try:
            results = wikipedia.search(query, results=3)
            if not results:
                return {"title": "", "url": "", "snippet": "No results."}
            page = wikipedia.page(results[0], auto_suggest=False)
            return {
                "title": page.title,
                "url": page.url,
                "snippet": page.summary[:800],
            }
        except Exception as e:
            return {"title": "", "url": "", "snippet": f"Wikipedia error: {e}"}
