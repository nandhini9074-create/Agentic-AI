import os
import httpx
from app.utils.logger import logger, log_execution_time
from dotenv import load_dotenv

load_dotenv()

class EnrichmentService:
    def __init__(self):
        self.apify_api_key = os.getenv("APIFY_API_KEY")
        self.apify_actor_id = os.getenv("APIFY_ACTOR_ID")
        self.clay_api_key = os.getenv("CLAY_API_KEY")

    @log_execution_time
    def apify_extract(self, url: str) -> str:
        # Apify LinkedIn Profile Scraper API (Disabled)
        logger.info(f"Apify extraction requested for: {url} (Currently Disabled)")
        return "Error: Apify extraction is currently disabled in the configuration. Falling back to other tools."

    @log_execution_time
    def clay_enrich(self, query: str) -> str:
        # Placeholder for Clay AI enrichment API
        logger.info(f"Using Clay for person enrichment: {query}")
        
        if not self.clay_api_key:
            return "Error: CLAY_API_KEY is not configured. Fallback to standard web_search."
            
        try:
            # Clay API to enrich a person
            # You can adapt this endpoint based on your specific Clay workflow / table
            headers = {
                "Authorization": f"Bearer {self.clay_api_key}",
                "Content-Type": "application/json"
            }
            
            # Using the Clay person search endpoint as an example
            api_url = "https://api.clay.com/v3/search/person"
            payload = {
                "query": query
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # You can filter the data here to only return necessary fields to the LLM
                return str(data)
                
        except httpx.HTTPError as e:
            logger.error(f"Clay HTTP error: {str(e)}")
            return f"Error enriching via Clay: {str(e)}"
        except Exception as e:
            logger.error(f"Clay enrichment failed: {str(e)}")
            return f"Error enriching via Clay: {str(e)}"

enrichment_service = EnrichmentService()
