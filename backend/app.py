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

def generate_dynamic_data():
    """Generate dynamic NEO data with time-based changes"""
    current_time = datetime.now()
    n_objects = np.random.randint(15, 35)  # Random number of objects
    
    # Base data generation
    data = {
        'name': [f'NEO-{i}-{current_time.strftime("%H%M%S")}' for i in range(n_objects)],
        'hazardous': np.random.choice([True, False], n_objects, p=[0.2, 0.8]),
        'est_diameter_min': np.random.uniform(0.1, 2.0, n_objects),
        'last_updated': current_time.isoformat()
    }
    
    # Dynamic distance calculation (objects moving closer/farther)
    base_distances = np.random.uniform(10000, 500000, n_objects)
    time_factor = np.sin(current_time.timestamp() / 10000) * 50000  # Oscillating factor
    data['miss_distance'] = base_distances + time_factor
    
    # Dynamic velocity (changes over time)
    base_velocities = np.random.uniform(20000, 100000, n_objects)
    velocity_factor = np.cos(current_time.timestamp() / 8000) * 10000
    data['relative_velocity'] = base_velocities + velocity_factor
    
    # Add orbital parameters
    data['orbit_inclination'] = np.random.uniform(0, 45, n_objects)
    data['orbit_eccentricity'] = np.random.uniform(0, 0.5, n_objects)
    
    return pd.DataFrame(data)

@app.route('/api/objects', methods=['GET'])
def get_objects():
    """Get current NEO objects with dynamic updates"""
    try:
        data = generate_dynamic_data()
        return jsonify(data.to_dict(orient='records'))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 