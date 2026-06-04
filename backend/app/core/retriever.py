from app.core.vectordb import vectordb_service
from app.utils.logger import logger

class RAGRetriever:
    @staticmethod
    def retrieve_chunks(query: str, k: int = 10, use_hybrid: bool = True, where: dict = None) -> list[dict]:
        """
        Retrieves top k semantically relevant chunks from the vector database.
        Optionally uses hybrid scoring (vector similarity + simple keyword frequency) 
        to ensure exact keyword matches (like specific technology names or locations) are boosted.
        """
        logger.info(f"RAGRetriever: Retrieving candidate chunks for '{query}' (filter={where})...")
        
        # Get semantic vector matches
        semantic_chunks = vectordb_service.similarity_search(query, k=k, where=where)
        if not semantic_chunks:
            return []

        if not use_hybrid:
            return semantic_chunks

        # Apply simple TF-IDF / keyword boost for hybrid search
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for chunk in semantic_chunks:
            content_lower = chunk["content"].lower()
            
            # Simple keyword matching score
            match_count = 0
            for word in query_words:
                if len(word) > 2: # Ignore tiny stop-words
                    # Give weight if word is found
                    match_count += content_lower.count(word)
            
            # Qdrant returns cosine similarity score (0.0 to 1.0, higher = more similar)
            # NOTE: ChromaDB used distance (0 to 2), but Qdrant uses similarity — use directly
            vector_similarity = chunk.get("distance", 0.0)  # "distance" key holds Qdrant's similarity score
            
            # Combine scores: hybrid = vector_similarity + keyword boost
            hybrid_score = vector_similarity + (0.05 * min(match_count, 5))
            
            chunk["hybrid_score"] = hybrid_score
            scored_chunks.append(chunk)

        # Sort by hybrid score in descending order
        scored_chunks.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        logger.info(f"RAGRetriever: Successfully reranked hybrid candidate list. Top chunk score: {scored_chunks[0]['hybrid_score']:.3f}")
        return scored_chunks
