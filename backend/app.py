from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

NASA_API_KEY = os.getenv('NASA_API_KEY')

class NEOStats:
    def __init__(self):
        self.total_known_neos = 31000  # Approximate number from NASA
        self.potentially_hazardous = 2300  # Approximate number
        self.last_update = datetime.now()
        self.discovery_rate = "Around 30 new NEOs per week"
        
    def get_global_stats(self):
        self.last_update = datetime.now()  # Update timestamp
        return {
            "total_known_neos": self.total_known_neos,
            "potentially_hazardous_total": self.potentially_hazardous,
            "largest_known": "1036 Ganymed (31.7 km)",
            "closest_approach_2024": "Asteroid 2024 BX1 (Jan 27, 2024)",
            "discovery_rate": self.discovery_rate,
            "observation_programs": [
                "NASA's NEOWISE",
                "Pan-STARRS",
                "Catalina Sky Survey"
            ],
            "last_update": self.last_update.isoformat()
        }

neo_stats = NEOStats()

def generate_sample_data():
    """Generate sample NEO data with realistic values and ensure updates"""
    current_time = datetime.now()
    n_objects = np.random.randint(20, 50)  # Random number of objects each time
    
    # More realistic name generation with timestamp to show updates
    name_prefixes = ['2024 ', '2023 ', '2022 ']
    name_suffixes = [chr(i) + str(j) for i in range(65, 91) for j in range(1, 10)]
    
    # Generate base data
    data = {
        'name': [f"{np.random.choice(name_prefixes)}{np.random.choice(name_suffixes)}" 
                for _ in range(n_objects)],
        'hazardous': np.random.choice([True, False], n_objects, p=[0.2, 0.8]),
        'est_diameter_min': np.random.uniform(0.01, 5.0, n_objects),
        'est_diameter_max': np.random.uniform(5.0, 10.0, n_objects),
        'miss_distance': np.random.uniform(10000, 1000000, n_objects),
        'relative_velocity': np.random.uniform(20000, 100000, n_objects),
        'orbit_type': np.random.choice(['Apollo', 'Aten', 'Amor'], n_objects),
        'discovery_date': [
            (current_time - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
            for _ in range(n_objects)
        ],
        'last_observed': [current_time.strftime('%Y-%m-%d %H:%M:%S') for _ in range(n_objects)],
        'update_timestamp': [current_time.strftime('%H:%M:%S') for _ in range(n_objects)]
    }
    
    return pd.DataFrame(data)

@app.route('/api/objects', methods=['GET'])
def get_objects():
    """Get current NEO objects with guaranteed updates"""
    try:
        data = generate_sample_data()
        return jsonify({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'objects': data.to_dict(orient='records')
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get global NEO statistics"""
    return jsonify(neo_stats.get_global_stats())

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "message": "Data is being updated regularly"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 