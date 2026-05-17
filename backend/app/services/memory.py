import chromadb
from chromadb.config import Settings
import os
from app.utils.logger import logger, log_execution_time

class MemoryService:
    def __init__(self):
        # Initialize a persistent ChromaDB client to manage long-term profile data storage
        logger.info("Initializing ChromaDB Memory Service")
        self.client = chromadb.PersistentClient(path="./storage/chroma")
        self.collection = self.client.get_or_create_collection(name="profile_data")

    @log_execution_time
    def write(self, key: str, value: str):
        # Store a piece of information in the vector database for future retrieval
        logger.info(f"Writing to memory: {key}")
        self.collection.add(
            documents=[value],
            metadatas=[{"key": key}],
            ids=[f"{key}_{os.urandom(4).hex()}"]
        )

    @log_execution_time
    def read(self, query: str):
        # Search the vector database for relevant information based on a text query
        logger.info(f"Querying memory: {query}")
        results = self.collection.query(
            query_texts=[query],
            n_results=5
        )
        return results["documents"]

memory_service = MemoryService()
