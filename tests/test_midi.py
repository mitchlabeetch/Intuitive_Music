"""Test suite for MIDI processing"""
import pytest
from src.intuitive_daw.midi.processor import (
    MIDIClip, MIDINote, MIDIProcessor, MIDIUtilities
)


class TestMIDIClip:
    """Test MIDI clip functionality"""
    
    def test_clip_creation(self):
        """Test creating MIDI clip"""
        clip = MIDIClip("Test Clip")
        assert clip.name == "Test Clip"
        assert len(clip.notes) == 0
    
    def test_add_note(self):
        """Test adding notes"""
        clip = MIDIClip()
        clip.add_note(60, 80, 0.0, 1.0)
        assert len(clip.notes) == 1
        assert clip.notes[0].pitch == 60
    
    def test_transpose(self):
        """Test transposing notes"""
        clip = MIDIClip()
        clip.add_note(60, 80, 0.0, 1.0)
        clip.transpose(5)
        assert clip.notes[0].pitch == 65
    
    def test_quantize(self):
        """Test quantization"""
        clip = MIDIClip()
        clip.add_note(60, 80, 0.12, 1.0)
        clip.quantize(0.25)
        # Should quantize to nearest 0.25 beat
        assert abs(clip.notes[0].start_time - 0.0) < 0.01


class TestMIDIProcessor:
    """Test MIDI processor"""
    
    def test_create_major_chord(self):
        """Test creating major chord"""
        notes = MIDIProcessor.create_chord(60, "major")
        assert len(notes) == 3
        pitches = [n.pitch for n in notes]
        assert pitches == [60, 64, 67]  # C, E, G
    
    def test_create_minor_chord(self):
        """Test creating minor chord"""
        notes = MIDIProcessor.create_chord(60, "minor")
        assert len(notes) == 3
        pitches = [n.pitch for n in notes]
        assert pitches == [60, 63, 67]  # C, Eb, G
    
    def test_create_arpeggio(self):
        """Test creating arpeggio"""
        notes = MIDIProcessor.create_arpeggio(
            [60, 64, 67],
            pattern="up",
            note_duration=0.25
        )
        assert len(notes) == 3
        # Check timing
        assert notes[0].start_time == 0.0
        assert notes[1].start_time == 0.25
        assert notes[2].start_time == 0.5


class TestMIDIUtilities:
    """Test MIDI utilities"""
    
    def test_note_name_to_number(self):
        """Test converting note names to MIDI numbers"""
        assert MIDIUtilities.note_name_to_number("C4") == 60
        assert MIDIUtilities.note_name_to_number("A4") == 69
        assert MIDIUtilities.note_name_to_number("C#4") == 61
    
    def test_note_number_to_name(self):
        """Test converting MIDI numbers to note names"""
        assert MIDIUtilities.note_number_to_name(60) == "C4"
        assert MIDIUtilities.note_number_to_name(69) == "A4"
    
    def test_beats_to_seconds(self):
        """Test beats to seconds conversion"""
        seconds = MIDIUtilities.beats_to_seconds(4.0, 120.0)
        assert abs(seconds - 2.0) < 0.01
    
    def test_seconds_to_beats(self):
        """Test seconds to beats conversion"""
        beats = MIDIUtilities.seconds_to_beats(2.0, 120.0)
        assert abs(beats - 4.0) < 0.01


if __name__ == '__main__':
    pytest.main([__file__])
