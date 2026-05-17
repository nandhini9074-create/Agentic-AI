from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from app.utils.logger import logger, log_execution_time
import asyncio
import time

class ScraperService:
    @log_execution_time
    async def scrape(self, url: str):
        # Run the synchronous scraping logic in a separate thread to avoid blocking the FastAPI event loop
        # and to avoid Windows ProactorEventLoop issues with Uvicorn.
        return await asyncio.to_thread(self._scrape_sync, url)

    def _scrape_sync(self, url: str):
        logger.info(f"Direct scraping: {url}")
        
        browser = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                Stealth().apply_stealth_sync(page)
                
                logger.info(f"Navigating to: {url}")
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                time.sleep(5)
                
                content = page.evaluate("() => document.body.innerText")
                clean_content = " ".join(content.split())
                
                # Check for Auth Wall
                if any(phrase in clean_content for phrase in ["Agree & Join", "Join LinkedIn", "Sign in", "Password (6+ characters)"]):
                    logger.warning("LinkedIn Auth Wall detected.")
                    return "Error scraping: LinkedIn is blocking access with an Auth Wall."
                
                logger.info(f"Successfully scraped {len(clean_content)} characters")
                return clean_content[:15000]
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return f"Error scraping: {str(e)}"

scraper_service = ScraperService()