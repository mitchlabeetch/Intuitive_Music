"""Test suite for core DAW functionality"""
import pytest
import numpy as np
from src.intuitive_daw.core.engine import AudioEngine, AudioConfig
from src.intuitive_daw.core.project import Project
from src.intuitive_daw.core.track import Track, AudioTrack, MIDITrack


class TestAudioEngine:
    """Test audio engine functionality"""
    
    def test_engine_initialization(self):
        """Test engine can be initialized"""
        engine = AudioEngine()
        assert engine is not None
        assert engine.is_playing == False
        assert engine.is_recording == False
    
    def test_engine_config(self):
        """Test custom audio configuration"""
        config = AudioConfig(
            sample_rate=44100,
            buffer_size=256,
            channels=2
        )
        engine = AudioEngine(config)
        assert engine.config.sample_rate == 44100
        assert engine.config.buffer_size == 256
    
    def test_playback_control(self):
        """Test playback start/stop"""
        engine = AudioEngine()
        engine.start_playback()
        assert engine.is_playing == True
        
        engine.stop_playback()
        assert engine.is_playing == False
    
    def test_recording_control(self):
        """Test recording start/stop"""
        engine = AudioEngine()
        engine.start_recording()
        assert engine.is_recording == True
        
        engine.stop_recording()
        assert engine.is_recording == False
    
    def test_track_management(self):
        """Test adding and removing tracks"""
        engine = AudioEngine()
        track = Track("Test Track")
        
        engine.add_track(track)
        assert len(engine.tracks) == 1
        
        engine.remove_track(track)
        assert len(engine.tracks) == 0


class TestProject:
    """Test project management"""
    
    def test_project_creation(self):
        """Test creating a new project"""
        project = Project("Test Project")
        assert project.metadata.name == "Test Project"
        assert len(project.tracks) == 0
    
    def test_project_tempo(self):
        """Test setting project tempo"""
        project = Project("Test")
        project.set_tempo(140.0)
        assert project.metadata.tempo == 140.0
    
    def test_project_time_signature(self):
        """Test setting time signature"""
        project = Project("Test")
        project.set_time_signature(3, 4)
        assert project.metadata.time_signature == (3, 4)
    
    def test_add_remove_track(self):
        """Test adding and removing tracks"""
        project = Project("Test")
        track = Track("Track 1")
        
        project.add_track(track)
        assert len(project.tracks) == 1
        
        project.remove_track(track)
        assert len(project.tracks) == 0
    
    def test_add_marker(self):
        """Test adding markers"""
        project = Project("Test")
        project.add_marker(4.0, "Chorus")
        assert len(project.markers) == 1
        assert project.markers[0]['name'] == "Chorus"


class TestTrack:
    """Test track functionality"""
    
    def test_track_creation(self):
        """Test creating tracks"""
        track = Track("My Track")
        assert track.name == "My Track"
        assert track.is_enabled == True
    
    def test_audio_track(self):
        """Test audio track"""
        track = AudioTrack("Audio 1")
        assert track.track_type.value == "audio"
    
    def test_midi_track(self):
        """Test MIDI track"""
        track = MIDITrack("MIDI 1")
        assert track.track_type.value == "midi"
    
    def test_volume_control(self):
        """Test volume setting"""
        track = Track("Test")
        track.set_volume(-6.0)
        assert track.settings.volume == -6.0
    
    def test_pan_control(self):
        """Test pan setting"""
        track = Track("Test")
        track.set_pan(0.5)
        assert track.settings.pan == 0.5
    
    def test_mute_toggle(self):
        """Test mute toggle"""
        track = Track("Test")
        assert track.settings.mute == False
        track.toggle_mute()
        assert track.settings.mute == True
    
    def test_add_effect(self):
        """Test adding effects"""
        track = Track("Test")
        effect = {"name": "EQ"}
        track.add_effect(effect)
        assert len(track.effects) == 1
    
    def test_automation(self):
        """Test automation"""
        track = Track("Test")
        points = [(0.0, 0.0), (1.0, -6.0), (2.0, 0.0)]
        track.add_automation("volume", points)
        
        value = track.get_automation_value("volume", 0.5)
        assert value is not None


if __name__ == '__main__':
    pytest.main([__file__])
