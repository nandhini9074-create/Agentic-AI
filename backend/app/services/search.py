import requests
import json
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from app.utils.logger import logger, log_execution_time

load_dotenv()

class SearchService:
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serper_key = os.getenv("SERPER_API_KEY")
        
        if not self.tavily_key and not self.serper_key:
            logger.warning("Neither TAVILY_API_KEY nor SERPER_API_KEY found in environment variables")
            
        self.tavily_client = TavilyClient(api_key=self.tavily_key) if self.tavily_key else None

    @log_execution_time
    def search(self, query: str):
        # Execute a targeted web search using Serper (if key is set) or Tavily to discover high-precision details
        if self.serper_key:
            logger.info(f"Searching web with Serper for: {query}")
            try:
                url = "https://google.serper.dev/search"
                payload = json.dumps({
                    "q": query,
                    "num": 20
                })
                headers = {
                    'X-API-KEY': self.serper_key,
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get('organic', []):
                        results.append({
                            "title": item.get("title"),
                            "url": item.get("link"),
                            "content": item.get("snippet")
                        })
                    logger.info(f"Serper successfully retrieved {len(results)} organic search results")
                    return results
                else:
                    logger.error(f"Serper API returned non-200 status: {response.status_code} {response.text}")
            except Exception as e:
                logger.error(f"Serper search failed: {str(e)}. Falling back to Tavily.")

        logger.info(f"Searching web with Tavily for: {query}")
        if not self.tavily_client:
            return "Error: Neither Serper nor Tavily Search is configured. Missing API keys."
            
        try:
            # Using search with 'search_depth ="advanced"' for deeper professional context
            response = self.tavily_client.search(query=query, search_depth="advanced", max_results=20)
            results = []
            for result in response.get('results', []):
                results.append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "content": result.get("content")
                })
            return results
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            return f"Error performing Tavily search: {str(e)}"

search_service = SearchService()

