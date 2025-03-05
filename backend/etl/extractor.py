import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarvelRivalsExtractor:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def extract_recent_matches(self, hours: int = 24) -> List[Dict]:
        """Extract match data from the last N hours"""
        endpoint = f"{self.base_url}/matches"
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "limit": 1000  # Adjust based on API limitations
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()["matches"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting match data: {e}")
            return []
    
    def extract_hero_data(self) -> List[Dict]:
        """Extract hero metadata"""
        endpoint = f"{self.base_url}/heroes"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()["heroes"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting hero data: {e}")
            return []
    
    def extract_player_stats(self, player_id: str) -> Optional[Dict]:
        """Extract stats for a specific player"""
        endpoint = f"{self.base_url}/players/{player_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting player stats: {e}")
            return None 