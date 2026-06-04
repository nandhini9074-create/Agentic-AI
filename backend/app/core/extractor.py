from app.utils.helpers import clean_text
from app.utils.logger import logger

class RAGExtractor:
    @staticmethod
    def extract_and_clean(scraped_data: dict) -> dict:
        """
        Extracts and cleans raw text from scraped payload, normalizing whitespace,
        stripping out menus, boilerplate footer/header strings, and duplicate lines.
        """
        url = scraped_data.get("url", "")
        title = scraped_data.get("title", "")
        raw_content = scraped_data.get("content", "")
        metadata = scraped_data.get("metadata", {})

        logger.info(f"RAGExtractor: Cleaning content for {url} (Length: {len(raw_content)})")
        
        cleaned_content = clean_text(raw_content)
        
        logger.info(f"RAGExtractor: Cleaning finished. New Length: {len(cleaned_content)}")

        return {
            "url": url,
            "title": title,
            "content": cleaned_content,
            "metadata": metadata
        }
