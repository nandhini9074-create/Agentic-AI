import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.embeddings import embeddings_service
from app.utils.logger import logger

class RAGVectorDB:
    def __init__(self, persist_path: str = "./backend/storage/qdrant_rag"):
        logger.info(f"RAGVectorDB: Initializing persistent Qdrant at {persist_path}...")
        os.makedirs(persist_path, exist_ok=True)
        
        # Initialize standard local persistent client (no Docker required!)
        self.client = QdrantClient(path=persist_path)
        self.collection_name = "rag_profile_chunks"
        
        try:
            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                # MiniLM-L6-v2 outputs 384 dimensional vectors
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"RAGVectorDB: Created Qdrant collection '{self.collection_name}' with Cosine metric.")
            else:
                logger.info(f"RAGVectorDB: Qdrant collection '{self.collection_name}' ready.")
        except Exception as e:
            logger.error(f"RAGVectorDB: Failed to initialize Qdrant collection: {str(e)}")

    def add_chunks(self, chunks: list[dict]):
        """
        Takes list of chunks:
        {
          "chunk_id": "...",
          "source_url": "...",
          "content": "...",
          "metadata": {...}
        }
        Converts content to vectors, checks for duplicates, and persists them to Qdrant.
        """
        if not chunks:
            return

        logger.info(f"RAGVectorDB: Vectorizing and adding {len(chunks)} chunks to Qdrant...")
        
        # Generate embeddings in batch
        contents = [chunk["content"] for chunk in chunks]
        embeddings = embeddings_service.get_embeddings(contents)

        points = []
        for i, chunk in enumerate(chunks):
            cid = chunk["chunk_id"]
            
            # Map clean metadata
            meta = chunk.get("metadata", {})
            meta["source_url"] = chunk["source_url"]
            meta["chunk_id"] = cid
            meta["content"] = chunk["content"]  # Save raw content in payload
            
            # Prepare clean flattened metadata
            cleaned_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    cleaned_meta[k] = v
                elif isinstance(v, list):
                    cleaned_meta[k] = ", ".join([str(item) for item in v])
                else:
                    cleaned_meta[k] = str(v)

            # Generate unique deterministic UUID for each chunk ID to prevent duplicates in Qdrant
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, cid))

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embeddings[i],
                    payload=cleaned_meta
                )
            )

        try:
            # Upload points to Qdrant collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"RAGVectorDB: Successfully added {len(points)} new vectors to Qdrant.")
        except Exception as e:
            logger.error(f"RAGVectorDB: Failed to add chunks to Qdrant: {str(e)}")

    def similarity_search(self, query: str, k: int = 10, where: dict = None) -> list[dict]:
        """
        Performs semantic similarity search with query using Qdrant.
        Returns top k matching chunks.
        """
        logger.info(f"RAGVectorDB: Querying Qdrant for '{query}' (k={k}, filter={where})")
        if not query:
            return []

        # Embed query
        query_vector = embeddings_service.get_embedding(query)

        # Build Qdrant metadata filters dynamically if 'where' filters are passed
        q_filter = None
        if where:
            try:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                conditions = []
                for key, val in where.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=val))
                    )
                q_filter = Filter(must=conditions)
            except Exception as fe:
                logger.error(f"RAGVectorDB: Failed to parse search filter: {str(fe)}")

        try:
            # query_points replaces deprecated search method in newer qdrant-client versions
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=q_filter,
                limit=k
            )
            
            parsed_chunks = []
            for hit in response.points:
                payload = hit.payload or {}
                parsed_chunks.append({
                    "chunk_id": payload.get("chunk_id", hit.id),
                    "content": payload.get("content", ""),
                    "source_url": payload.get("source_url", ""),
                    "distance": hit.score,
                    "metadata": payload
                })
            
            logger.info(f"RAGVectorDB: Retrieved {len(parsed_chunks)} matched chunks from Qdrant.")
            return parsed_chunks
        except Exception as e:
            logger.error(f"RAGVectorDB: Qdrant Query failed: {str(e)}")
            return []

    def delete_target_chunks(self, target_name: str):
        """
        Deletes all persistent vector points matching target_name filter.
        """
        logger.info(f"RAGVectorDB: Deleting legacy points for target '{target_name}'...")
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="target_name",
                            match=MatchValue(value=target_name)
                        )
                    ]
                )
            )
            logger.info(f"RAGVectorDB: Successfully deleted legacy points for '{target_name}'.")
        except Exception as e:
            logger.error(f"RAGVectorDB: Failed to delete legacy points for '{target_name}': {str(e)}")

    def list_all_points(self, limit: int = 100) -> list[dict]:
        """
        Helper method to list stored points in Qdrant for easy visual inspection.
        """
        try:
            res, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            points = []
            for record in res:
                payload = record.payload
                points.append({
                    "id": record.id,
                    "chunk_id": payload.get("chunk_id", ""),
                    "target_name": payload.get("target_name", ""),
                    "content": payload.get("content", ""),
                    "source_url": payload.get("source_url", ""),
                    "word_count": payload.get("word_count", 0),
                    "metadata": payload
                })
            return points
        except Exception as e:
            logger.error(f"RAGVectorDB: Failed to list Qdrant points: {str(e)}")
            return []

    def clear_database(self):
        """
        Helper method to reset/clear chunk collection.
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logger.info("RAGVectorDB: Successfully cleared Qdrant collection.")
        except Exception as e:
            logger.error(f"RAGVectorDB: Failed to clear Qdrant collection: {str(e)}")

# Global instance for workspace persistence
vectordb_service = RAGVectorDB()

