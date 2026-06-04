from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from app.utils.logger import logger

class URLProcessor:
    @staticmethod
    def extract_links(html_content: str, base_url: str) -> list[str]:
        """
        Extract all hyperlinks from raw HTML content and resolve them into absolute paths.
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_links = []
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href'].strip()
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            # Normalize URL (strip fragments) but preserve query parameters (vital for YouTube videos/channels)
            parsed = urlparse(absolute_url)
            query_suffix = f"?{parsed.query}" if parsed.query else ""
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}{query_suffix}"
            
            if parsed.scheme in ('http', 'https'):
                extracted_links.append(normalized)
                
        # Remove duplicates while maintaining order
        seen = set()
        unique_links = []
        for link in extracted_links:
            if link not in seen and URLProcessor.is_valid_profile_link(link):
                seen.add(link)
                unique_links.append(link)
                
        logger.info(f"Extracted {len(unique_links)} sanitized links from {base_url}")
        return unique_links

    @staticmethod
    def is_valid_profile_link(url: str) -> bool:
        """
        Filters out invalid links like ads, login redirects, share buttons, and generic policies.
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Domains to ignore
        blacklisted_domains = [
            "google-analytics.com", "doubleclick.net", "facebook.com/sharer", 
            "twitter.com/intent", "linkedin.com/share", "pinterest.com/pin",
            "accounts.google.com", "login.live.com", "optimizely.com",
            "hotjar.com", "sentry.io", "ads.twitter.com", "ads.linkedin.com"
        ]
        
        for d in blacklisted_domains:
            if d in domain:
                return False
                
        # Paths to ignore
        blacklisted_paths = [
            "/privacy", "/cookie-policy", "/terms", "/legal", "/about",
            "/signup", "/login", "/register", "/contact", "/support"
        ]
        for p in blacklisted_paths:
            if path.rstrip('/') == p or path.startswith(p + "/"):
                return False
                
        return True

    @staticmethod
    def classify_url(url: str) -> str:
        """
        Classifies URLs into portfolio, blog, github, linkedin, resume, etc.
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        if "linkedin.com" in domain:
            return "linkedin"
        elif "github.com" in domain or "github.io" in domain:
            return "github"
        elif "twitter.com" in domain or "x.com" in domain:
            return "twitter"
        elif any(b in domain for b in ["medium.com", "dev.to", "hashnode.dev", "substack.com", "blogspot.com"]):
            return "blog"
        elif "youtube.com" in domain or "youtu.be" in domain:
            return "youtube"
        elif "facebook.com" in domain:
            return "facebook"
        elif "wikipedia.org" in domain:
            return "wikipedia"
        elif any(k in path or k in domain for k in ["resume", "cv", "portfolio", "vitae", "about-me"]):
            if "resume" in path or "cv" in path:
                return "resume"
            return "portfolio"
        elif any(k in domain for k in ["github.io", "vercel.app", "netlify.app", "pages.dev"]):
            return "portfolio"
        elif any(k in domain for k in ["google.com/company", "linkedin.com/company"]):
            return "company_profile"
        elif "project" in path or "work" in path:
            return "project_showcase"
        elif any(d in domain for d in ["google.com", "bing.com", "yahoo.com", "duckduckgo.com", "tavily.com"]):
            return "other"
        else:
            # All other valid, non-blacklisted domains (Britannica, news articles, custom blogs)
            return "general_web"

url_processor = URLProcessor()
