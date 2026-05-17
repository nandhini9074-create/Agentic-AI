from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from app.utils.logger import logger, log_execution_time
import asyncio
import time
import os

class ScraperService:
    @log_execution_time
    async def scrape(self, url: str):
        # Run the synchronous scraping logic in a separate thread to avoid blocking the FastAPI event loop
        # and to avoid Windows ProactorEventLoop issues with Uvicorn.
        return await asyncio.to_thread(self._scrape_sync, url)

    def _scrape_sync(self, url: str):
        logger.info(f"Direct scraping: {url}")
        
        browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
        browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        proxy_server = os.getenv("PROXY_URL") # E.g., Bright Data or Scrapeless
        li_at_cookie = os.getenv("LINKEDIN_LI_AT") # For cookie-based authentication
        
        browser = None
        try:
            with sync_playwright() as p:
                if browserbase_api_key and browserbase_project_id:
                    logger.info("Connecting to Browserbase Cloud instance...")
                    # Browserbase CDP connection format
                    cdp_url = f"wss://connect.browserbase.com?apiKey={browserbase_api_key}&projectId={browserbase_project_id}"
                    browser = p.chromium.connect_over_cdp(cdp_url)
                else:
                    logger.info("Launching local Chromium instance...")
                    launch_args = ["--disable-blink-features=AutomationControlled"]
                    proxy_config = {"server": proxy_server} if proxy_server else None
                    
                    if proxy_config:
                        logger.info("Using configured Proxy server for routing...")
                        
                    browser = p.chromium.launch(
                        headless=True, 
                        args=launch_args,
                        proxy=proxy_config
                    )
                    
                # Dynamic user agent and viewport selection
                is_linkedin = "linkedin.com" in url.lower()
                
                if is_linkedin and not li_at_cookie:
                    # Using a Googlebot user-agent is highly effective for bypassing auth walls when not logged in,
                    # as LinkedIn allows crawlers to view public profile pages for SEO indexing.
                    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
                    viewport = {'width': 1024, 'height': 768}
                    logger.info("Using SEO Googlebot User-Agent for LinkedIn public bypass...")
                else:
                    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                    viewport = {'width': 1920, 'height': 1080}
                
                context = browser.new_context(
                    user_agent=user_agent,
                    viewport=viewport
                )
                
                # Inject LinkedIn Session Cookie if present
                if is_linkedin and li_at_cookie:
                    logger.info("Injecting LINKEDIN_LI_AT cookie for authenticated scraping...")
                    context.add_cookies([{
                        "name": "li_at",
                        "value": li_at_cookie,
                        "domain": ".www.linkedin.com",
                        "path": "/"
                    }])
                
                page = context.new_page()
                Stealth().apply_stealth_sync(page)
                
                logger.info(f"Navigating to: {url}")
                page.goto(url, timeout=60000, wait_until="load") # Changed to 'load' to let primary redirects complete
                
                # Wait 2 seconds to let any client-side JavaScript redirects (e.g. to login page) settle down
                time.sleep(2)
                
                # Human-like scrolling to trigger lazy loading of profiles (wrapped defensively)
                logger.info("Executing human-like scroll interactions...")
                try:
                    for i in range(3):
                        # Ensure page is still alive and not navigating before evaluating
                        page.evaluate(f"window.scrollBy(0, {300 + i * 150})")
                        time.sleep(1.5)
                except Exception as eval_err:
                    logger.warning(f"Scrolling evaluate interrupted (likely redirected): {str(eval_err)}")
                    # Let redirects settle again
                    time.sleep(2)
                
                try:
                    content = page.evaluate("() => document.body.innerText")
                    clean_content = " ".join(content.split())
                except Exception as eval_err:
                    logger.error(f"Main content extraction failed during navigation: {str(eval_err)}")
                    return "Error scraping: The page underwent an unexpected redirection or navigation."
                
                # Check for Auth Wall
                if any(phrase in clean_content for phrase in ["Agree & Join", "Join LinkedIn", "Sign in", "Password (6+ characters)"]):
                    logger.warning("LinkedIn Auth Wall detected using primary strategy. Retrying with mobile user-agent...")
                    
                    # Retry strategy using a Mobile Web user-agent
                    page.close()
                    context.close()
                    
                    mobile_context = browser.new_context(
                        user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
                        viewport={'width': 375, 'height': 812},
                        is_mobile=True
                    )
                    mobile_page = mobile_context.new_page()
                    Stealth().apply_stealth_sync(mobile_page)
                    
                    mobile_page.goto(url, timeout=60000, wait_until="load")
                    time.sleep(3)
                    
                    try:
                        content = mobile_page.evaluate("() => document.body.innerText")
                        clean_content = " ".join(content.split())
                    except Exception as eval_err:
                        logger.error(f"Mobile retry content extraction failed: {str(eval_err)}")
                        return "Error scraping: LinkedIn mobile page underwent unexpected redirection."
                    
                    if any(phrase in clean_content for phrase in ["Agree & Join", "Join LinkedIn", "Sign in", "Password (6+ characters)"]):
                        logger.warning("LinkedIn Auth Wall detected on mobile retry as well.")
                        return "Error scraping: LinkedIn is blocking access with an Auth Wall."
                
                logger.info(f"Successfully scraped {len(clean_content)} characters")
                return clean_content[:15000]
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return f"Error scraping: {str(e)}"

scraper_service = ScraperService()