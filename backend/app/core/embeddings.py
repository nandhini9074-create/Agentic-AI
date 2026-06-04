from app.utils.logger import logger

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class RAGEmbeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"RAGEmbeddings: Loading SentenceTransformer model: {model_name}...")
                self._model = SentenceTransformer(model_name)
                logger.info("RAGEmbeddings: Model loaded successfully.")
            except Exception as e:
                logger.error(f"RAGEmbeddings: Error loading model locally: {str(e)}. Falling back to API/Mock.")
                self._model = None
        else:
            logger.warning("RAGEmbeddings: sentence-transformers library not installed. Using local numeric vectorization fallback.")

    def get_embedding(self, text: str) -> list[float]:
        """
        Generates embedding vector for a single string.
        """
        if not text:
            return [0.0] * 384 # MiniLM dimension size is 384

        if self._model:
            try:
                # encode returns numpy array, convert to standard Python float list
                vector = self._model.encode(text, show_progress_bar=False)
                return vector.tolist()
            except Exception as e:
                logger.error(f"RAGEmbeddings: Encoding error: {str(e)}")
                return self._fallback_vector(text)
        else:
            return self._fallback_vector(text)

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generates embedding vectors for a list of strings.
        """
        if not texts:
            return []

        if self._model:
            try:
                vectors = self._model.encode(texts, show_progress_bar=False)
                return vectors.tolist()
            except Exception as e:
                logger.error(f"RAGEmbeddings: Bulk encoding error: {str(e)}")
                return [self._fallback_vector(t) for t in texts]
        else:
            return [self._fallback_vector(t) for t in texts]

    def _fallback_vector(self, text: str) -> list[float]:
        """
        Fallback simple numeric representation if sentence-transformers is unavailable.
        Uses a deterministic hash-based character frequency bag-of-words mapped to 384 dimensions.
        """
        vector = [0.0] * 384
        if not text:
            return vector
            
        words = text.lower().split()
        for idx, word in enumerate(words):
            # Compute a deterministic hash for the word to map it to a specific dimension
            h = hash(word) % 384
            # Add frequency weighting
            vector[h] += 1.0
            
        # Normalize vector
        magnitude = sum(x**2 for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
            
        return vector

# Global instance for reuse across the pipeline
embeddings_service = RAGEmbeddings()
