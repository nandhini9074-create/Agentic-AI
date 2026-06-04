import uuid
from app.utils.logger import logger

class RAGChunker:
    @staticmethod
    def chunk_content(cleaned_data: dict) -> list[dict]:
        """
        Keeps the entire URL content as one single chunk, completely removing
        the granular 50-word split chunking.
        """
        url = cleaned_data.get("url", "")
        title = cleaned_data.get("title", "")
        content = cleaned_data.get("content", "")
        metadata = cleaned_data.get("metadata", {})

        if not content:
            return []

        logger.info(f"RAGChunker: Keeping entire content for {url} as one single chunk (removing 50-word splitting)...")

        # Helper to get word count
        def get_word_count(text: str) -> int:
            return len(text.split())

        chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
        chunks = [{
            "chunk_id": chunk_id,
            "source_url": url,
            "content": content,
            "metadata": {
                "title": title,
                "word_count": get_word_count(content),
                **metadata
            }
        }]

        logger.info(f"RAGChunker: Generated 1 single chunk for {url} (word count={get_word_count(content)})")
        return chunks
