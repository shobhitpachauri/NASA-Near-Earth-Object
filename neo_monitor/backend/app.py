from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the data
try:
    df = pd.read_csv('nasa.csv')
except FileNotFoundError:
    # Create sample data if file doesn't exist
    df = pd.DataFrame({
        'name': [f'Asteroid_{i}' for i in range(100)],
        'hazardous': np.random.choice([True, False], 100),
        'est_diameter_min': np.random.uniform(0.1, 2.0, 100),
        'miss_distance': np.random.uniform(1000, 100000, 100),
        'relative_velocity': np.random.uniform(10000, 50000, 100),
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = {
        'total_objects': len(df),
        'hazardous_count': int(df['hazardous'].sum()),
        'avg_diameter': float(df['est_diameter_min'].mean()),
        'closest_object': {
            'name': str(df.loc[df['miss_distance'].idxmin(), 'name']),
            'distance': float(df['miss_distance'].min())
        }
    }
    return jsonify(stats)

@app.route('/api/objects', methods=['GET'])
def get_objects():
    limit = request.args.get('limit', default=10, type=int)
    latest_objects = df.head(limit).to_dict(orient='records')
    return jsonify(latest_objects)

@app.route('/api/hazardous', methods=['GET'])
def get_hazardous():
    limit = request.args.get('limit', default=10, type=int)
    hazardous = df[df['hazardous'] == True].head(limit).to_dict(orient='records')
    return jsonify(hazardous)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)