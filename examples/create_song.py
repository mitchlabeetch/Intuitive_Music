"""
Example: Creating a simple song with the DAW
"""
from intuitive_daw.core.engine import AudioEngine
from intuitive_daw.core.project import Project
from intuitive_daw.core.track import MIDITrack, AudioTrack
from intuitive_daw.midi.processor import MIDIProcessor, MIDIClip
from intuitive_daw.ai.assistant import AIAssistant


def create_simple_song():
    """Create a simple song with MIDI and AI assistance"""
    
    # Initialize project
    print("Creating new project...")
    project = Project("My First Song")
    project.set_tempo(120.0)
    project.set_time_signature(4, 4)
    
    # Add AI assistant
    print("\nInitializing AI assistant...")
    ai = AIAssistant()
    
    # Get chord suggestions from AI
    print("\nGetting chord suggestions from AI...")
    response = ai.suggest_chords(key="C major", style="pop", num_chords=4)
    if response.success:
        print(f"AI suggests: {response.content}")
    
    # Create MIDI track for chords
    print("\nCreating chord track...")
    chord_track = MIDITrack("Chords")
    project.add_track(chord_track)
    
    # Create chord progression
    clip = MIDIClip("Verse Chords")
    
    # C major chord at beat 0
    c_major = MIDIProcessor.create_chord(
        root=60,  # C4
        chord_type="major",
        velocity=70,
        start_time=0.0,
        duration=1.0
    )
    for note in c_major:
        clip.notes.append(note)
    
    # A minor chord at beat 1
    a_minor = MIDIProcessor.create_chord(
        root=69,  # A4
        chord_type="minor",
        velocity=70,
        start_time=1.0,
        duration=1.0
    )
    for note in a_minor:
        clip.notes.append(note)
    
    # F major chord at beat 2
    f_major = MIDIProcessor.create_chord(
        root=65,  # F4
        chord_type="major",
        velocity=70,
        start_time=2.0,
        duration=1.0
    )
    for note in f_major:
        clip.notes.append(note)
    
    # G major chord at beat 3
    g_major = MIDIProcessor.create_chord(
        root=67,  # G4
        chord_type="major",
        velocity=70,
        start_time=3.0,
        duration=1.0
    )
    for note in g_major:
        clip.notes.append(note)
    
    chord_track.add_clip(clip)
    
    # Create melody track
    print("Creating melody track...")
    melody_track = MIDITrack("Melody")
    project.add_track(melody_track)
    
    # Create simple melody
    melody_clip = MIDIClip("Verse Melody")
    melody_notes = [
        (72, 0.0),   # C5
        (71, 0.5),   # B4
        (69, 1.0),   # A4
        (67, 1.5),   # G4
        (65, 2.0),   # F4
        (67, 2.5),   # G4
        (69, 3.0),   # A4
        (72, 3.5),   # C5
    ]
    
    for pitch, start in melody_notes:
        melody_clip.add_note(
            pitch=pitch,
            velocity=80,
            start=start,
            duration=0.4
        )
    
    melody_track.add_clip(melody_clip)
    
    # Add markers
    print("Adding markers...")
    project.add_marker(0.0, "Intro")
    project.add_marker(4.0, "Verse")
    project.add_marker(8.0, "Chorus")
    
    # Get mixing advice from AI
    print("\nGetting mixing advice from AI...")
    response = ai.mixing_advice(
        track_name="Melody",
        track_type="melody",
        issues=["needs clarity", "sits too forward"]
    )
    if response.success:
        print(f"AI mixing advice: {response.content[:200]}...")
    
    # Save project
    print("\nSaving project...")
    if project.save():
        print(f"✓ Project saved to {project.path}")
    
    # Initialize audio engine (for playback)
    print("\nInitializing audio engine...")
    engine = AudioEngine()
    if engine.initialize():
        print("✓ Audio engine initialized")
        
        # Add tracks to engine
        for track in project.tracks:
            engine.add_track(track)
    
    print("\n✓ Song creation complete!")
    print(f"\nProject details:")
    print(f"  Name: {project.metadata.name}")
    print(f"  Tempo: {project.metadata.tempo} BPM")
    print(f"  Time Signature: {project.metadata.time_signature[0]}/{project.metadata.time_signature[1]}")
    print(f"  Tracks: {len(project.tracks)}")
    print(f"  Markers: {len(project.markers)}")
    
    return project, engine


if __name__ == '__main__':
    # Run the example
    try:
        project, engine = create_simple_song()
        print("\nExample completed successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
