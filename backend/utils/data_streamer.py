import pandas as pd
import requests
from datetime import datetime, timedelta
import time
from typing import Generator

class NEODataStreamer:
    def __init__(self, api_key: str = 'DEMO_KEY'):
        self.api_key = api_key
        self.base_url = 'https://api.nasa.gov/neo/rest/v1/feed'
        self.last_update = None
        self.update_interval = 3600  # 1 hour (NASA updates daily)

    def fetch_nasa_data(self) -> pd.DataFrame:
        """Fetch real NASA NEO data"""
        try:
            # Get data for today and tomorrow
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'api_key': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                print(f"Error from NASA API: {response.status_code}")
                return pd.DataFrame()
                
            data = response.json()
            neo_data = []
            
            for date in data['near_earth_objects']:
                for neo in data['near_earth_objects'][date]:
                    neo_data.append({
                        'name': neo['name'],
                        'id': neo['id'],
                        'hazardous': neo['is_potentially_hazardous_asteroid'],
                        'est_diameter_min': neo['estimated_diameter']['kilometers']['estimated_diameter_min'],
                        'est_diameter_max': neo['estimated_diameter']['kilometers']['estimated_diameter_max'],
                        'miss_distance': float(neo['close_approach_data'][0]['miss_distance']['kilometers']),
                        'relative_velocity': float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']),
                        'approach_date': neo['close_approach_data'][0]['close_approach_date'],
                        'orbit_body': neo['close_approach_data'][0]['orbiting_body'],
                        'nasa_url': neo['nasa_jpl_url'],
                        'last_updated': datetime.now().isoformat()
                    })
            
            return pd.DataFrame(neo_data)
            
        except Exception as e:
            print(f"Error fetching NASA data: {e}")
            return pd.DataFrame()

    def stream_data(self) -> Generator[pd.DataFrame, None, None]:
        """Stream NEO data"""
        while True:
            current_time = datetime.now()
            
            if (self.last_update is None or 
                (current_time - self.last_update).seconds >= self.update_interval):
                
                print("Fetching new data from NASA...")
                data = self.fetch_nasa_data()
                
                if not data.empty:
                    self.last_update = current_time
                    yield data
                else:
                    print("No data received from NASA")
            
            time.sleep(60)  # Check every minute 