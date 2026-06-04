from app.services.scraper import scraper_service
from app.utils.logger import logger

class RAGScraper:
    @staticmethod
    async def scrape_url(url: str) -> dict:
        """
        Scrapes a URL utilizing the robust multi-viewport local stealth Playwright engine 
        and static fallback routes (Trafilatura, HTTPX + BS4) from the core scraper service.
        Normalizes output to RAG-standard formatting.
        """
        logger.info(f"RAGScraper: Scraping {url}")
        try:
            result = await scraper_service.scrape(url)
            if isinstance(result, dict) and "error" not in result:
                return {
                    "url": result.get("source_url") or url,
                    "title": result.get("title") or "Web Page",
                    "content": result.get("visible_text") or "",
                    "metadata": result.get("metadata") or {}
                }
            else:
                err_msg = result.get("error") if isinstance(result, dict) else str(result)
                logger.error(f"RAGScraper: Scraping failed for {url}: {err_msg}")
                return {
                    "url": url,
                    "title": "Error Page",
                    "content": f"Error scraping website: {err_msg}",
                    "metadata": {"error": err_msg}
                }
        except Exception as e:
            logger.error(f"RAGScraper: Exception occurred scraping {url}: {str(e)}")
            return {
                "url": url,
                "title": "Exception Page",
                "content": f"Exception occurred during scraping: {str(e)}",
                "metadata": {"error": str(e)}
            }
