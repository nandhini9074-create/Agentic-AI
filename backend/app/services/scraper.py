from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import trafilatura
import httpx
import asyncio
import time
import os
from app.utils.logger import logger, log_execution_time
from app.services.url_processor import url_processor

class ScraperService:
    @log_execution_time
    async def scrape(self, url: str):
        # Run the synchronous scraping logic in a separate thread to avoid blocking the FastAPI event loop
        # and to avoid Windows ProactorEventLoop issues with Uvicorn.
        return await asyncio.to_thread(self._scrape_unified, url)

    def _scrape_unified(self, url: str) -> dict:
        source_type = url_processor.classify_url(url)
        logger.info(f"Scraping URL: {url} | Classified as: {source_type}")
        
        # Route 1: Blogs / Articles - Trafilatura (highly efficient)
        if source_type == "blog":
            logger.info("Using Trafilatura engine for blog content...")
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False)
                if text:
                    soup = BeautifulSoup(downloaded, 'html.parser')
                    title = soup.title.string.strip() if soup.title else "Blog Post"
                    meta = self._extract_meta_tags(soup)
                    links = url_processor.extract_links(downloaded, url)
                    return {
                        "source_url": url,
                        "source_type": source_type,
                        "title": title,
                        "visible_text": text[:25000],
                        "metadata": meta,
                        "discovered_links": links
                    }

        # Route 2: Static Portfolio / Simple Site - HTTPX + BeautifulSoup
        if source_type in ("portfolio", "resume", "other", "project_showcase", "wikipedia", "general_web") and not ("linkedin.com" in url or "github.com" in url):
            logger.info("Attempting static HTTPX + BeautifulSoup scraping...")
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                }
                with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title = soup.title.string.strip() if soup.title else "Web Page"
                        
                        is_sports_domain = any(domain in url.lower() for domain in ["wikidata.org", "wikipedia.org", "espncricinfo.com", "transfermarkt.com", "sofascore.com", "cricinfo.com"])
                        if is_sports_domain:
                            logger.info("Sports domain detected in static scrape! Using specialized parser...")
                            text = self._parse_sports_content(response.text)
                        else:
                            # Remove scripts and styles
                            for script in soup(["script", "style"]):
                                script.decompose()
                            text = " ".join(soup.get_text().split())
                            
                        meta = self._extract_meta_tags(soup)
                        links = url_processor.extract_links(response.text, url)
                        return {
                            "source_url": url,
                            "source_type": source_type,
                            "title": title,
                            "visible_text": text[:25000],
                            "metadata": meta,
                            "discovered_links": links
                        }
            except Exception as static_err:
                logger.warning(f"Static scrape failed for {url}: {str(static_err)}. Falling back to Playwright...")
 
        # Route 3: Dynamic / Secure Pages (LinkedIn, GitHub) - Playwright
        logger.info("Using Playwright browser automation...")
        return self._scrape_playwright(url, source_type)
 
    def _scrape_playwright(self, url: str, source_type: str) -> dict:
        browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
        browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        proxy_server = os.getenv("PROXY_URL")
        li_at_cookie = os.getenv("LINKEDIN_LI_AT")
        
        browser = None
        try:
            with sync_playwright() as p:
                if browserbase_api_key and browserbase_project_id:
                    logger.info("Connecting to Browserbase Cloud...")
                    cdp_url = f"wss://connect.browserbase.com?apiKey={browserbase_api_key}&projectId={browserbase_project_id}"
                    browser = p.chromium.connect_over_cdp(cdp_url)
                else:
                    logger.info("Launching local stealth Chromium...")
                    launch_args = ["--disable-blink-features=AutomationControlled"]
                    proxy_config = {"server": proxy_server} if proxy_server else None
                    browser = p.chromium.launch(headless=True, args=launch_args, proxy=proxy_config)
                    
                is_linkedin = "linkedin.com" in url.lower()
                if is_linkedin and not li_at_cookie:
                    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
                    viewport = {'width': 1024, 'height': 768}
                else:
                    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                    viewport = {'width': 1920, 'height': 1080}
                    
                context = browser.new_context(user_agent=user_agent, viewport=viewport)
                
                # Inject LinkedIn Cookie if applicable
                if is_linkedin and li_at_cookie:
                    context.add_cookies([{
                        "name": "li_at",
                        "value": li_at_cookie,
                        "domain": ".www.linkedin.com",
                        "path": "/"
                    }])
                    
                page = context.new_page()
                Stealth().apply_stealth_sync(page)
                
                page.goto(url, timeout=60000, wait_until="load")
                time.sleep(2)
                
                # Dynamic scrolling
                try:
                    for i in range(3):
                        page.evaluate(f"window.scrollBy(0, {300 + i * 150})")
                        time.sleep(1.5)
                except Exception as scroll_err:
                    logger.warning(f"Scroll evaluate interrupted: {str(scroll_err)}")
                    time.sleep(2)
                    
                # Fetch text and document properties
                title = page.title()
                html_content = page.content()
                
                try:
                    is_sports_domain = any(domain in url.lower() for domain in ["wikidata.org", "wikipedia.org", "espncricinfo.com", "transfermarkt.com", "sofascore.com", "cricinfo.com"])
                    if is_sports_domain:
                        logger.info("Sports domain detected in Playwright! Using specialized tables/infobox parser...")
                        clean_content = self._parse_sports_content(html_content)
                    else:
                        content = page.evaluate("() => document.body.innerText")
                        clean_content = " ".join(content.split())
                except Exception as content_err:
                    logger.error(f"Text content extraction failed: {str(content_err)}")
                    return {"error": "Error scraping: navigation or page error."}
                
                # Check for LinkedIn Auth Wall
                if is_linkedin and any(phrase in clean_content for phrase in ["Agree & Join", "Join LinkedIn", "Sign in", "Password"]):
                    logger.warning("LinkedIn Auth Wall detected. Trying Mobile viewport fallback...")
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
                    
                    content = mobile_page.evaluate("() => document.body.innerText")
                    clean_content = " ".join(content.split())
                    html_content = mobile_page.content()
                    title = mobile_page.title()
                    
                    if any(phrase in clean_content for phrase in ["Agree & Join", "Join LinkedIn", "Sign in"]):
                        return {"error": "Error scraping: LinkedIn is blocking access with an Auth Wall."}
                
                # Extract meta attributes
                metadata = page.evaluate("""() => {
                    const meta = {};
                    document.querySelectorAll('meta').forEach(el => {
                        const name = el.getAttribute('name') || el.getAttribute('property');
                        const content = el.getAttribute('content');
                        if (name && content) {
                            meta[name] = content;
                        }
                    });
                    return meta;
                }""")
                
                links = url_processor.extract_links(html_content, url)
                return {
                    "source_url": url,
                    "source_type": source_type,
                    "title": title,
                    "visible_text": clean_content[:25000],
                    "metadata": metadata,
                    "discovered_links": links
                }
        except Exception as err:
            logger.error(f"Playwright scraping failed: {str(err)}")
            return {"error": f"Error scraping: {str(err)}"}
 
    def _parse_sports_content(self, html_text: str) -> str:
        # Specialized parser for sports content to preserve tables and Wikipedia infobox structures
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Extract infobox data
        infobox_text = ""
        infobox = soup.find('table', class_=lambda c: c and 'infobox' in c)
        if infobox:
            rows = []
            for tr in infobox.find_all('tr'):
                th = tr.find(['th', 'td'], class_=lambda c: c and 'infobox-label' in c) or tr.find('th')
                td = tr.find(['td'], class_=lambda c: c and 'infobox-data' in c) or tr.find('td')
                if th and td:
                    rows.append(f"{th.get_text(strip=True)}: {td.get_text(strip=True)}")
            infobox_text = "\n[SPORTS INFOBOX DATA]\n" + "\n".join(rows) + "\n"
            
        # Convert all statistical tables to structured markdown-like tables to preserve runs, goals, averages
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in tr.find_all(['th', 'td'])]
                if cells:
                    rows.append(" | ".join(cells))
            if rows:
                table_text = "\n[SPORTS TABLE DATA]\n" + "\n".join(rows) + "\n"
                table.replace_with(table_text)
                
        # Strip script and style
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        text_lines = [line.strip() for line in text.splitlines() if line.strip()]
        return (infobox_text + "\n" + "\n".join(text_lines)).strip()
 
    def _extract_meta_tags(self, soup: BeautifulSoup) -> dict:
        meta = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                meta[name] = content
        return meta
 
scraper_service = ScraperService()