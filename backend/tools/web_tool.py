"""Web scraping tool using requests + BeautifulSoup, with mock fallback."""
from typing import Dict


class WebScrapeTool:
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def scrape(self, query: str) -> Dict[str, str]:
        if self.mock_mode:
            return {
                "title": f"Guide to {query.title()} (mock web result)",
                "url": f"https://example.com/articles/{query.replace(' ', '-')}",
                "snippet": f"A practical overview of {query}, including applied examples. "
                           f"This is a mock web snippet used when MOCK_MODE=true.",
            }
        import requests
        from bs4 import BeautifulSoup
        # Use a simple DuckDuckGo HTML scrape for the top result, then fetch it.
        try:
            ddg = requests.get(
                "https://duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 ResearchBot"},
                timeout=10,
            )
            soup = BeautifulSoup(ddg.text, "html.parser")
            link = soup.select_one("a.result__a")
            if not link:
                return {"title": "", "url": "", "snippet": "No web results."}
            href = link.get("href")
            title = link.get_text(strip=True)

            page = requests.get(href, timeout=10, headers={"User-Agent": "Mozilla/5.0 ResearchBot"})
            page_soup = BeautifulSoup(page.text, "html.parser")
            text = " ".join(p.get_text(strip=True) for p in page_soup.find_all("p")[:5])
            return {"title": title, "url": href, "snippet": text[:800]}
        except Exception as e:
            return {"title": "", "url": "", "snippet": f"Web scrape error: {e}"}
