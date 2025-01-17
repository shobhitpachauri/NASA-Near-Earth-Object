import pandas as pd
import numpy as np
from typing import Dict, List

class NEODataProcessor:
    def __init__(self, data_path: str):
        self.df = self._load_data(data_path)

    def _load_data(self, data_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(data_path)
            # Ensure required columns exist
            required_columns = ['name', 'hazardous', 'est_diameter_min', 
                              'miss_distance', 'relative_velocity']
            if not all(col in df.columns for col in required_columns):
                return self._create_sample_data()
            return df
        except FileNotFoundError:
            print(f"Warning: {data_path} not found. Using sample data.")
            return self._create_sample_data()

    def _create_sample_data(self, n_samples: int = 100) -> pd.DataFrame:
        return pd.DataFrame({
            'name': [f'Asteroid_{i}' for i in range(n_samples)],
            'hazardous': np.random.choice([True, False], n_samples),
            'est_diameter_min': np.random.uniform(0.1, 2.0, n_samples),
            'miss_distance': np.random.uniform(1000, 100000, n_samples),
            'relative_velocity': np.random.uniform(10000, 50000, n_samples),
        })

    def get_stats(self) -> Dict:
        return {
            'total_objects': len(self.df),
            'hazardous_count': int(self.df['hazardous'].sum()),
            'avg_diameter': float(self.df['est_diameter_min'].mean()),
            'closest_object': {
                'name': str(self.df.loc[self.df['miss_distance'].idxmin(), 'name']),
                'distance': float(self.df['miss_distance'].min())
            }
        }

    def get_latest_objects(self, limit: int = 10) -> List[Dict]:
        return self.df.head(limit).to_dict(orient='records')

    def get_hazardous_objects(self, limit: int = 10) -> List[Dict]:
        return self.df[self.df['hazardous'] == True].head(limit).to_dict(orient='records') 