/**
 * INTUITIVES - React Hooks
 * Easy integration with React applications.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Hook for the Intuitives audio engine
 * 
 * @example
 * const { isReady, noteOn, noteOff, setFilter, getSpectrum } = useIntuitives();
 * 
 * // Play a note
 * noteOn(60, 0.8);
 * 
 * // Change filter
 * setFilter(2000, 0.7);
 */
export function useIntuitives(options = {}) {
  const [isReady, setIsReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [levels, setLevels] = useState({ left: 0, right: 0 });
  const [spectrum, setSpectrum] = useState(new Float32Array(64));
  
  const intuitivesRef = useRef(null);
  const audioContextRef = useRef(null);
  const animationRef = useRef(null);

  // Initialize engine
  useEffect(() => {
    let mounted = true;

    async function init() {
      try {
        // Dynamic import to avoid SSR issues
        const { Intuitives } = await import('./intuitives.js');
        
        const intuitives = await Intuitives.create({
          sampleRate: options.sampleRate || 48000,
          bufferSize: options.bufferSize || 128,
          wasmUrl: options.wasmUrl
        });

        if (mounted) {
          intuitivesRef.current = intuitives;
          setIsReady(true);
        }
      } catch (error) {
        console.error('Failed to initialize Intuitives:', error);
      }
    }

    init();

    return () => {
      mounted = false;
      if (intuitivesRef.current) {
        intuitivesRef.current.destroy();
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [options.sampleRate, options.bufferSize, options.wasmUrl]);

  // Animation loop for visualization
  const startVisualization = useCallback(() => {
    function update() {
      if (intuitivesRef.current && isPlaying) {
        setLevels(intuitivesRef.current.getLevels());
        setSpectrum(new Float32Array(intuitivesRef.current.getSpectrum(64)));
      }
      animationRef.current = requestAnimationFrame(update);
    }
    update();
  }, [isPlaying]);

  useEffect(() => {
    if (isPlaying) {
      startVisualization();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, startVisualization]);

  // Synth controls
  const noteOn = useCallback((note, velocity = 0.8) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.noteOn(note, velocity);
      setIsPlaying(true);
    }
  }, []);

  const noteOff = useCallback(() => {
    if (intuitivesRef.current) {
      intuitivesRef.current.noteOff();
    }
  }, []);

  const setWaveform = useCallback((type) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.setWaveform(type);
    }
  }, []);

  const setMorph = useCallback((morph) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.setMorph(morph);
    }
  }, []);

  const setFilter = useCallback((cutoff, resonance = 0.5) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.setFilter(cutoff, resonance);
    }
  }, []);

  const setEnvelope = useCallback((attack, decay, sustain, release) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.setEnvelope(attack, decay, sustain, release);
    }
  }, []);

  // Generative
  const initMarkov = useCallback((seed) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.initMarkov(seed);
    }
  }, []);

  const nextMarkovNote = useCallback(() => {
    return intuitivesRef.current?.nextMarkovNote() ?? 60;
  }, []);

  const initTextMelody = useCallback((text) => {
    if (intuitivesRef.current) {
      intuitivesRef.current.initTextMelody(text);
    }
  }, []);

  const nextTextNote = useCallback(() => {
    return intuitivesRef.current?.nextTextNote() ?? 60;
  }, []);

  // Color to harmony
  const colorToHarmony = useCallback((r, g, b, octave = 4) => {
    return intuitivesRef.current?.colorToHarmony(r, g, b, octave) ?? { root: 60, chord: [60, 64, 67] };
  }, []);

  const hexToHarmony = useCallback((hex, octave = 4) => {
    return intuitivesRef.current?.hexToHarmony(hex, octave) ?? { root: 60, chord: [60, 64, 67] };
  }, []);

  // Chromasynesthesia
  const noteToColor = useCallback((note) => {
    return intuitivesRef.current?.noteToColor(note) ?? { r: 255, g: 0, b: 0, hex: '#ff0000' };
  }, []);

  // Visualization
  const getSpectrum = useCallback((numBands = 64) => {
    return intuitivesRef.current?.getSpectrum(numBands) ?? new Float32Array(numBands);
  }, []);

  const getLevels = useCallback(() => {
    return intuitivesRef.current?.getLevels() ?? { left: 0, right: 0 };
  }, []);

  return {
    isReady,
    isPlaying,
    levels,
    spectrum,
    
    // Synth
    noteOn,
    noteOff,
    setWaveform,
    setMorph,
    setFilter,
    setEnvelope,
    
    // Generative
    initMarkov,
    nextMarkovNote,
    initTextMelody,
    nextTextNote,
    
    // Color/Harmony
    colorToHarmony,
    hexToHarmony,
    noteToColor,
    
    // Visualization
    getSpectrum,
    getLevels,
    
    // Raw access
    engine: intuitivesRef.current
  };
}

/**
 * Hook for keyboard-to-MIDI input
 */
export function useKeyboardMidi(onNoteOn, onNoteOff) {
  const activeNotes = useRef(new Set());
  
  // Computer keyboard to MIDI mapping (Z-M = C3-B3, Q-U = C4-B4)
  const keyMap = {
    'z': 48, 's': 49, 'x': 50, 'd': 51, 'c': 52, 'v': 53,
    'g': 54, 'b': 55, 'h': 56, 'n': 57, 'j': 58, 'm': 59,
    'q': 60, '2': 61, 'w': 62, '3': 63, 'e': 64, 'r': 65,
    '5': 66, 't': 67, '6': 68, 'y': 69, '7': 70, 'u': 71,
    'i': 72, '9': 73, 'o': 74, '0': 75, 'p': 76
  };

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.repeat) return;
      const note = keyMap[e.key.toLowerCase()];
      if (note && !activeNotes.current.has(note)) {
        activeNotes.current.add(note);
        onNoteOn?.(note, 0.8);
      }
    }

    function handleKeyUp(e) {
      const note = keyMap[e.key.toLowerCase()];
      if (note && activeNotes.current.has(note)) {
        activeNotes.current.delete(note);
        onNoteOff?.(note);
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [onNoteOn, onNoteOff]);

  return activeNotes.current;
}

/**
 * Hook for generative melody playback
 */
export function useGenerativeMelody(engine, options = {}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentNote, setCurrentNote] = useState(null);
  const intervalRef = useRef(null);

  const tempo = options.tempo || 120;
  const noteLength = (60 / tempo) * 1000; // ms per beat

  const start = useCallback(() => {
    if (!engine || isPlaying) return;
    
    setIsPlaying(true);
    
    intervalRef.current = setInterval(() => {
      const note = engine.nextMarkovNote();
      setCurrentNote(note);
      
      if (note >= 0) {
        engine.noteOn(note, 0.7);
        setTimeout(() => engine.noteOff(), noteLength * 0.8);
      }
    }, noteLength);
  }, [engine, isPlaying, noteLength]);

  const stop = useCallback(() => {
    setIsPlaying(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    engine?.noteOff();
  }, [engine]);

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { isPlaying, currentNote, start, stop };
}

export default useIntuitives;
