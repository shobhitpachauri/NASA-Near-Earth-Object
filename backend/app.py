from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from utils.data_processor import NEODataProcessor
from utils.data_streamer import NEODataStreamer
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Initialize data processor with NASA data
data_processor = NEODataProcessor('../nasa.csv')

# Add at the top of the file
NASA_API_KEY = os.getenv('NASA_API_KEY')

# Update streamer initialization
streamer = NEODataStreamer(api_key=NASA_API_KEY)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(data_processor.get_stats())

@app.route('/api/objects', methods=['GET'])
def get_objects():
    """Get current NEO objects"""
    try:
        data = streamer.fetch_nasa_data()
        if data.empty:
            # If no NASA data, generate sample data
            data = pd.DataFrame({
                'name': [f'NEO-{i}' for i in range(10)],
                'hazardous': np.random.choice([True, False], 10),
                'est_diameter_min': np.random.uniform(0.1, 2.0, 10),
                'miss_distance': np.random.uniform(10000, 500000, 10),
                'relative_velocity': np.random.uniform(20000, 100000, 10),
                'last_updated': datetime.now().isoformat()
            })
        return jsonify(data.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hazardous', methods=['GET'])
def get_hazardous():
    limit = request.args.get('limit', default=10, type=int)
    return jsonify(data_processor.get_hazardous_objects(limit))

if __name__ == '__main__':
    app.run(debug=True, port=5000) 