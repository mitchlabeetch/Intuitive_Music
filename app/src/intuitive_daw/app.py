import sys
import os

# Ensure the app module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from flask import Flask, jsonify, request
from flask_cors import CORS
# Change import to relative if needed or use sys.path trick
try:
    from app.src.intuitive_daw.engine_wrapper import engine
except ImportError:
    # If running directly, adjust path
    from engine_wrapper import engine

app = Flask(__name__)
CORS(app)

@app.route('/api/project', methods=['POST'])
def create_project():
    data = request.json
    return jsonify({"success": True, "project": {"name": data.get('name', 'New Project')}})

@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    # In a real app, we'd query the engine for track info
    return jsonify([])

@app.route('/api/tracks', methods=['POST'])
def add_track():
    data = request.json
    track_type = data.get('type')
    # Engine integration:
    # engine.add_track("dummy_path.wav")
    return jsonify({"success": True})

@app.route('/api/transport/play', methods=['POST'])
def play():
    engine.play()
    return jsonify({"success": True})

@app.route('/api/transport/stop', methods=['POST'])
def stop():
    engine.stop()
    return jsonify({"success": True})

@app.route('/api/plugins/load', methods=['POST'])
def load_plugin():
    data = request.json
    plugin_type = data.get('type')
    plugin_path = data.get('path')

    if not plugin_type or not plugin_path:
        return jsonify({"success": False, "error": "Missing type or path"}), 400

    print(f"Loading plugin: {plugin_type} -> {plugin_path}")
    engine.load_plugin(plugin_type, plugin_path)

    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
