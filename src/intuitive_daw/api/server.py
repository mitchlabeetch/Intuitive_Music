"""Flask API server for the DAW"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from typing import Dict, Any

from ..core.engine import AudioEngine, AudioConfig
from ..core.project import Project
from ..core.track import Track, AudioTrack, MIDITrack
from ..ai.assistant import AIAssistant


class DAWServer:
    """Main DAW server class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.config = config or {}
        self.audio_engine = AudioEngine()
        self.ai_assistant = AIAssistant()
        self.current_project: Project = None
        
        self._setup_routes()
        self._setup_socket_handlers()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "ok",
                "version": "0.1.0"
            })
        
        @self.app.route('/api/project', methods=['POST'])
        def create_project():
            """Create a new project"""
            data = request.json
            name = data.get('name', 'Untitled Project')
            
            self.current_project = Project(name=name)
            
            return jsonify({
                "success": True,
                "project": {
                    "name": self.current_project.metadata.name,
                    "path": self.current_project.path
                }
            })
        
        @self.app.route('/api/project/<path:project_path>', methods=['GET'])
        def load_project(project_path):
            """Load an existing project"""
            project = Project.load(project_path)
            
            if project:
                self.current_project = project
                return jsonify({
                    "success": True,
                    "project": {
                        "name": project.metadata.name,
                        "tempo": project.metadata.tempo,
                        "tracks": len(project.tracks)
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to load project"
                }), 404
        
        @self.app.route('/api/project/save', methods=['POST'])
        def save_project():
            """Save current project"""
            if not self.current_project:
                return jsonify({
                    "success": False,
                    "error": "No project loaded"
                }), 400
            
            success = self.current_project.save()
            
            return jsonify({
                "success": success,
                "path": self.current_project.path if success else None
            })
        
        @self.app.route('/api/tracks', methods=['GET'])
        def get_tracks():
            """Get all tracks in current project"""
            if not self.current_project:
                return jsonify([])
            
            tracks = [{
                "index": i,
                "name": t.name,
                "type": t.track_type.value,
                "muted": t.settings.mute,
                "volume": t.settings.volume,
                "pan": t.settings.pan
            } for i, t in enumerate(self.current_project.tracks)]
            
            return jsonify(tracks)
        
        @self.app.route('/api/tracks', methods=['POST'])
        def add_track():
            """Add a new track"""
            if not self.current_project:
                return jsonify({
                    "success": False,
                    "error": "No project loaded"
                }), 400
            
            data = request.json
            track_type = data.get('type', 'audio')
            name = data.get('name', f'Track {len(self.current_project.tracks) + 1}')
            
            if track_type == 'audio':
                track = AudioTrack(name, len(self.current_project.tracks))
            elif track_type == 'midi':
                track = MIDITrack(name, len(self.current_project.tracks))
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid track type"
                }), 400
            
            self.current_project.add_track(track)
            self.audio_engine.add_track(track)
            
            return jsonify({
                "success": True,
                "track": {
                    "index": track.index,
                    "name": track.name,
                    "type": track.track_type.value
                }
            })
        
        @self.app.route('/api/transport/play', methods=['POST'])
        def play():
            """Start playback"""
            self.audio_engine.start_playback()
            return jsonify({"success": True, "playing": True})
        
        @self.app.route('/api/transport/stop', methods=['POST'])
        def stop():
            """Stop playback"""
            self.audio_engine.stop_playback()
            return jsonify({"success": True, "playing": False})
        
        @self.app.route('/api/transport/record', methods=['POST'])
        def record():
            """Start recording"""
            self.audio_engine.start_recording()
            return jsonify({"success": True, "recording": True})
        
        @self.app.route('/api/ai/suggest-chords', methods=['POST'])
        def suggest_chords():
            """Get chord suggestions from AI"""
            data = request.json
            key = data.get('key', 'C major')
            style = data.get('style', 'pop')
            
            response = self.ai_assistant.suggest_chords(key, style)
            
            return jsonify({
                "success": response.success,
                "content": response.content,
                "error": response.error
            })
        
        @self.app.route('/api/ai/chat', methods=['POST'])
        def ai_chat():
            """Chat with AI assistant"""
            data = request.json
            message = data.get('message', '')
            
            response = self.ai_assistant.chat(message)
            
            return jsonify({
                "success": response.success,
                "content": response.content,
                "error": response.error
            })
    
    def _setup_socket_handlers(self):
        """Setup WebSocket handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            emit('status', {'message': 'Connected to DAW server'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print('Client disconnected')
        
        @self.socketio.on('transport_update')
        def handle_transport_update(data):
            """Handle transport state updates"""
            action = data.get('action')
            
            if action == 'play':
                self.audio_engine.start_playback()
            elif action == 'stop':
                self.audio_engine.stop_playback()
            elif action == 'record':
                self.audio_engine.start_recording()
            
            emit('transport_state', {
                'playing': self.audio_engine.is_playing,
                'recording': self.audio_engine.is_recording,
                'position': self.audio_engine.get_position()
            }, broadcast=True)
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = True):
        """Run the server"""
        print(f"Starting Intuitive Music DAW Server on {host}:{port}")
        self.audio_engine.initialize()
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def create_app(config: Dict[str, Any] = None) -> Flask:
    """Factory function to create Flask app"""
    server = DAWServer(config)
    return server.app


if __name__ == '__main__':
    server = DAWServer()
    server.run()
