# backend/search/providers/duckduckgo.py
"""DuckDuckGo 搜索 Provider（免费，无需 API Key）"""

from typing import Optional
import httpx
from bs4 import BeautifulSoup

from backend.utils.logger import logger


class DuckDuckGoProvider:
    """DuckDuckGo 搜索"""

    def __init__(self):
        self.url = "https://html.duckduckgo.com/html/"

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """搜索"""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    self.url,
                    data={"q": query, "b": ""},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    },
                )
                response.raise_for_status()

            return self._parse_results(response.text, limit)

        except Exception as e:
            logger.error(f"DuckDuckGo 搜索失败: {e}")
            return []

    def _parse_results(self, html: str, limit: int) -> list[dict]:
        """解析搜索结果"""
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select(".result__body")

            for item in items[:limit]:
                title_el = item.select_one(".result__a")
                snippet_el = item.select_one(".result__snippet")
                url_el = item.select_one(".result__url")

                if title_el:
                    title = title_el.get_text(strip=True)
                    url = title_el.get("href", "")
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                    # 清理 URL
                    if "uddg=" in url:
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                        url = parsed.get("uddg", [url])[0]

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    })

        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")

        return results
