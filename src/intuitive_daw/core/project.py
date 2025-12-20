"""Project management for the DAW"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path


@dataclass
class ProjectMetadata:
    """Project metadata"""
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    description: str = ""
    tempo: float = 120.0
    time_signature: tuple = (4, 4)
    key: str = "C"
    tags: List[str] = field(default_factory=list)


class Project:
    """
    Represents a DAW project containing tracks, settings, and metadata
    """
    
    def __init__(self, name: str, path: Optional[str] = None):
        self.metadata = ProjectMetadata(name=name)
        self.path = path or f"./projects/{name}"
        self.tracks: List[Any] = []
        self.markers: List[Dict[str, Any]] = []
        self.automation: Dict[str, Any] = {}
        self.effects_chains: Dict[str, List[Any]] = {}
        self.is_modified = False
        
    def add_track(self, track: Any) -> None:
        """Add a track to the project"""
        self.tracks.append(track)
        self.is_modified = True
        self.metadata.modified_at = datetime.now()
    
    def remove_track(self, track: Any) -> None:
        """Remove a track from the project"""
        if track in self.tracks:
            self.tracks.remove(track)
            self.is_modified = True
            self.metadata.modified_at = datetime.now()
    
    def get_track(self, index: int) -> Optional[Any]:
        """Get track by index"""
        if 0 <= index < len(self.tracks):
            return self.tracks[index]
        return None
    
    def add_marker(self, position: float, name: str, color: str = "#FF0000") -> None:
        """Add a marker at the given position"""
        self.markers.append({
            "position": position,
            "name": name,
            "color": color
        })
        self.is_modified = True
    
    def set_tempo(self, tempo: float) -> None:
        """Set project tempo"""
        self.metadata.tempo = tempo
        self.is_modified = True
        self.metadata.modified_at = datetime.now()
    
    def set_time_signature(self, numerator: int, denominator: int) -> None:
        """Set project time signature"""
        self.metadata.time_signature = (numerator, denominator)
        self.is_modified = True
        self.metadata.modified_at = datetime.now()
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save project to disk
        
        Args:
            path: Optional custom save path
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self.path
        
        try:
            # Create project directory
            os.makedirs(save_path, exist_ok=True)
            
            # Prepare project data
            project_data = {
                "metadata": {
                    "name": self.metadata.name,
                    "created_at": self.metadata.created_at.isoformat(),
                    "modified_at": self.metadata.modified_at.isoformat(),
                    "author": self.metadata.author,
                    "description": self.metadata.description,
                    "tempo": self.metadata.tempo,
                    "time_signature": self.metadata.time_signature,
                    "key": self.metadata.key,
                    "tags": self.metadata.tags
                },
                "tracks": [self._serialize_track(t) for t in self.tracks],
                "markers": self.markers,
                "automation": self.automation
            }
            
            # Write project file
            project_file = os.path.join(save_path, "project.json")
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            self.is_modified = False
            return True
            
        except Exception as e:
            print(f"Failed to save project: {e}")
            return False
    
    @classmethod
    def load(cls, path: str) -> Optional['Project']:
        """
        Load project from disk
        
        Args:
            path: Path to project directory
            
        Returns:
            Project instance or None if failed
        """
        try:
            project_file = os.path.join(path, "project.json")
            
            with open(project_file, 'r') as f:
                data = json.load(f)
            
            # Create project
            metadata = data['metadata']
            project = cls(name=metadata['name'], path=path)
            
            # Restore metadata
            project.metadata.created_at = datetime.fromisoformat(metadata['created_at'])
            project.metadata.modified_at = datetime.fromisoformat(metadata['modified_at'])
            project.metadata.author = metadata.get('author', '')
            project.metadata.description = metadata.get('description', '')
            project.metadata.tempo = metadata['tempo']
            project.metadata.time_signature = tuple(metadata['time_signature'])
            project.metadata.key = metadata['key']
            project.metadata.tags = metadata.get('tags', [])
            
            # Restore markers and automation
            project.markers = data.get('markers', [])
            project.automation = data.get('automation', {})
            
            # Note: Track deserialization would be implemented here
            # For now, just store the data
            project._track_data = data.get('tracks', [])
            
            project.is_modified = False
            return project
            
        except Exception as e:
            print(f"Failed to load project: {e}")
            return None
    
    def _serialize_track(self, track: Any) -> Dict[str, Any]:
        """Serialize a track to dictionary"""
        # This would be implemented based on Track class
        return {
            "type": track.__class__.__name__,
            "name": getattr(track, 'name', 'Untitled'),
            # Add more track properties
        }
    
    def export(self, output_path: str, format: str = 'wav') -> bool:
        """
        Export project to audio file
        
        Args:
            output_path: Path to output file
            format: Audio format (wav, mp3, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        # This would use the audio engine to render
        # Placeholder for now
        print(f"Exporting project to {output_path} as {format}")
        return True
    
    def get_duration(self) -> float:
        """Get total project duration in seconds"""
        if not self.tracks:
            return 0.0
        # Calculate based on longest track
        max_duration = 0.0
        for track in self.tracks:
            if hasattr(track, 'get_duration'):
                max_duration = max(max_duration, track.get_duration())
        return max_duration
