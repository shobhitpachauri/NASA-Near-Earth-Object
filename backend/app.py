from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from utils.data_processor import NEODataProcessor

app = Flask(__name__)
CORS(app)

# Initialize data processor with NASA data
data_processor = NEODataProcessor('../nasa.csv')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(data_processor.get_stats())

@app.route('/api/objects', methods=['GET'])
def get_objects():
    limit = request.args.get('limit', default=10, type=int)
    return jsonify(data_processor.get_latest_objects(limit))

@app.route('/api/hazardous', methods=['GET'])
def get_hazardous():
    limit = request.args.get('limit', default=10, type=int)
    return jsonify(data_processor.get_hazardous_objects(limit))

if __name__ == '__main__':
    app.run(debug=True, port=5000) 