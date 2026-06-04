import math
from app.utils.logger import logger

try:
    from sentence_transformers import CrossEncoder
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False

def sigmoid(x: float) -> float:
    """Maps any raw logit strictly to the range [0.0, 1.0]."""
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0

class RAGReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

        if HAS_CROSS_ENCODER:
            try:
                logger.info(f"RAGReranker: Loading CrossEncoder model: {model_name}...")
                self._model = CrossEncoder(model_name)
                logger.info("RAGReranker: CrossEncoder loaded successfully.")
            except Exception as e:
                logger.error(f"RAGReranker: Failed to load CrossEncoder model locally: {str(e)}. Using fallback reranking.")
                self._model = None
        else:
            logger.warning("RAGReranker: sentence-transformers/cross-encoder not available. Using keyword-density semantic fallback.")

    def rerank(self, query: str, chunks: list[dict], top_n: int = 3) -> list[dict]:
        """
        Reranks retrieved candidate chunks based on the user's semantic query.
        Returns the top_n absolute most relevant chunks, normalized between 0.0 and 1.0.
        """
        if not chunks:
            return []

        logger.info(f"RAGReranker: Reranking {len(chunks)} candidate chunks for query: '{query}'...")

        if self._model:
            try:
                # Format pairs: [[query, doc1], [query, doc2], ...]
                pairs = [[query, chunk["content"]] for chunk in chunks]
                scores = self._model.predict(pairs)
                
                # Assign Sigmoid-normalized scores to chunks
                for idx, score in enumerate(scores):
                    chunks[idx]["rerank_score"] = sigmoid(float(score))
                
                # Sort descending
                chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
                logger.info(f"RAGReranker: Local CrossEncoder completed. Top score: {chunks[0]['rerank_score']:.4f}")
            except Exception as e:
                logger.error(f"RAGReranker: Prediction error: {str(e)}. Using fallback rerank.")
                self._apply_fallback_rerank(query, chunks)
        else:
            self._apply_fallback_rerank(query, chunks)

        # Apply score adjustments for namesake conflicts and skill boosts
        self._apply_score_adjustments(query, chunks)

        # Re-sort after adjustments
        chunks.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Select top_n
        top_chunks = chunks[:top_n]
        logger.info(f"RAGReranker: Selected top {len(top_chunks)} chunks for LLM context. Top score: {top_chunks[0]['rerank_score']:.4f}" if top_chunks else "RAGReranker: No chunks selected.")
        return top_chunks

    def _apply_score_adjustments(self, query: str, chunks: list[dict]):
        """
        Applies a strong namesake conflict penalty and skill match boosts to candidates.
        """
        target_name = chunks[0].get("metadata", {}).get("target_name", "") if chunks else ""
        
        # Parse target skills from RAG query
        import re
        skills_match = re.search(r"skills:\s*'([^']+)'", query.lower())
        if not skills_match:
            skills_match = re.search(r"skills:\s*\"([^\"]+)\"", query.lower())
        if not skills_match:
            skills_match = re.search(r"skills:\s*([a-zA-Z0-9,\s]+)", query.lower())
            
        target_skills = []
        if skills_match:
            target_skills = [s.strip() for s in skills_match.group(1).replace(",", " ").split() if len(s.strip()) > 1]

        logger.info(f"RAGReranker Heuristics: Target Name: '{target_name}' | Extracted Skills: {target_skills}")

        for chunk in chunks:
            orig_score = chunk.get("rerank_score", 0.5)
            adjustment = 0.0
            
            title_lower = chunk.get("metadata", {}).get("title", "").lower()
            content_lower = chunk.get("content", "").lower()
            
            # --- SKILL MATCH BOOST ---
            for skill in target_skills:
                if skill in title_lower:
                    adjustment += 0.20
                    logger.info(f"RAGReranker: Boosted +0.20 for skill '{skill}' in title: '{chunk.get('metadata', {}).get('title')}'")
                elif skill in content_lower:
                    adjustment += 0.05
                    logger.info(f"RAGReranker: Boosted +0.05 for skill '{skill}' in content of: '{chunk.get('metadata', {}).get('title')}'")
                    
            # --- NAMESAKE CONFLICT PENALTY ---
            if target_name:
                t_name_lower = target_name.lower().strip()
                parts = [p for p in t_name_lower.split() if len(p) > 0]
                if len(parts) >= 2:
                    first_name = parts[0]
                    last_name = parts[-1]
                    
                    if first_name in title_lower or first_name in content_lower:
                        # Find what follows the first name
                        pattern = re.compile(rf"{re.escape(first_name)}\s+(\w+)")
                        matches = pattern.findall(title_lower + " " + content_lower)
                        
                        conflict_found = False
                        for match in matches:
                            if match != last_name:
                                # Target initial 's', match 'sitharthan' -> compatible (e.g. initial matches first letter of match)
                                if len(last_name) == 1 and match.startswith(last_name):
                                    pass
                                # Target 'sitharthan', match 's' -> compatible
                                elif len(match) == 1 and last_name.startswith(match):
                                    pass
                                else:
                                    conflict_found = True
                                    logger.warning(f"RAGReranker Namesake Conflict: Candidate '{match}' conflicts with target '{last_name}' (First Name: '{first_name}')")
                                    
                        if conflict_found:
                            adjustment -= 0.50
                            logger.warning(f"RAGReranker: Penalized -0.50 namesake conflict for title: '{chunk.get('metadata', {}).get('title')}'")
            
            # Update and clamp
            chunk["rerank_score"] = max(0.0, min(1.0, orig_score + adjustment))

    def _apply_fallback_rerank(self, query: str, chunks: list[dict]):
        """
        Smart Python fallback: Uses intersection words, title overlap, and distance metrics
        to assign a deterministic relevance score, normalized to [0.0, 1.0] via Sigmoid.
        """
        query_words = set(query.lower().split())
        # Strip simple common words
        stopwords = {"show", "generate", "display", "list", "get", "portfolio", "technical", "skills", "experience", "and", "the", "for", "with"}
        filtered_query_words = query_words - stopwords
        if not filtered_query_words:
            filtered_query_words = query_words

        for chunk in chunks:
            content_lower = chunk["content"].lower()
            title_lower = chunk.get("metadata", {}).get("title", "").lower()
            
            # Count match densities
            content_matches = sum(1 for word in filtered_query_words if word in content_lower)
            title_matches = sum(2 for word in filtered_query_words if word in title_lower)
            
            # Length normalization
            words_count = len(content_lower.split())
            density = (content_matches + title_matches) / max(words_count, 1)
            
            # Integrate original vector hybrid score
            hybrid_score = chunk.get("hybrid_score", 0.5)
            
            # Final fallback score scaled with Sigmoid
            raw_score = hybrid_score + (density * 5.0) - 2.0  # Centered around 0 for natural Sigmoid distribution
            chunk["rerank_score"] = sigmoid(raw_score)

        # Sort descending
        chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
        logger.info(f"RAGReranker: Fallback scoring complete. Top fallback score: {chunks[0]['rerank_score']:.4f}")

# Global instance for workspace reuse
reranker_service = RAGReranker()

