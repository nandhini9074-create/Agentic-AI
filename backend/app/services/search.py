from tavily import TavilyClient
import os
from dotenv import load_dotenv
from app.utils.logger import logger, log_execution_time
# from ddgs import DDGS

load_dotenv()

class SearchService:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found in environment variables")
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None

    @log_execution_time
    def search(self, query: str):
        # Execute a targeted web search using Tavily to discover high-precision professional details
        logger.info(f"Searching web with Tavily for: {query}")
        
        if not self.client:
            return "Error: Tavily Search is not configured. Missing API key."
            
        try:
            # Using search with 'search_depth="advanced"' for deeper professional context
            response = self.client.search(query=query, search_depth="advanced", max_results=5)
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

        # # Execute a targeted web search using DuckDuckGo to discover high-precision professional details
        # logger.info(f"Searching web with DuckDuckGo for: {query}")
        # 
        # try:
        #     results = []
        #     with DDGS() as ddgs:
        #         ddgs_results = list(ddgs.text(query, max_results=5))
        #         for result in ddgs_results:
        #             results.append({
        #                 "title": result.get("title"),
        #                 "url": result.get("href"),
        #                 "content": result.get("body")
        #             })
        #     return results
        # except Exception as e:
        #     logger.error(f"DuckDuckGo search failed: {str(e)}")
        #     return f"Error performing DuckDuckGo search: {str(e)}"

search_service = SearchService()
