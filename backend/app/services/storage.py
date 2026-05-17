import os
import json
from datetime import datetime
from app.utils.logger import logger, log_execution_time

class StorageService:
    def __init__(self, base_path="./backend/data/raw"):
        # Initialize the storage service and ensure the target directory exists
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    @log_execution_time
    def save_raw_data(self, url: str, data: dict):
        # Save raw JSON data to the local filesystem with a unique timestamped filename
        logger.info(f"Saving raw data for URL: {url}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}_{timestamp}.json"
        filepath = os.path.join(self.base_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        return filepath

storage_service = StorageService()
