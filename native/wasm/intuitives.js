/**
 * INTUITIVES - JavaScript API
 * High-level wrapper for WebAssembly audio engine.
 * 
 * Usage with AudioWorklet:
 *   const intuitives = await Intuitives.create();
 *   intuitives.noteOn(60, 0.8);
 *   intuitives.setFilter(2000, 0.7);
 */

class Intuitives {
  constructor(module, sampleRate = 48000, bufferSize = 128) {
    this.module = module;
    this.sampleRate = sampleRate;
    this.bufferSize = bufferSize;
    this.initialized = false;
  }

  /**
   * Create and initialize the Intuitives engine
   * @param {Object} options - Configuration options
   * @returns {Promise<Intuitives>}
   */
  static async create(options = {}) {
    const sampleRate = options.sampleRate || 48000;
    const bufferSize = options.bufferSize || 128;

    // Load WASM module
    const wasmUrl = options.wasmUrl || './intuitives.js';
    const IntuitivesModule = await import(wasmUrl);
    const module = await IntuitivesModule.default();

    const instance = new Intuitives(module, sampleRate, bufferSize);
    await instance.init();
    return instance;
  }

  /**
   * Initialize the audio engine
   */
  async init() {
    if (this.initialized) return;

    const result = this.module._wasm_init(this.sampleRate, this.bufferSize);
    if (result !== 0) {
      throw new Error('Failed to initialize Intuitives engine');
    }

    // Get output buffer pointers
    this.outputL = this.module._wasm_get_output_l();
    this.outputR = this.module._wasm_get_output_r();

    this.initialized = true;
    console.log(`🎹 Intuitives v${this.version} initialized`);
  }

  /**
   * Process audio and return stereo output
   * @param {number} frames - Number of frames to process
   * @returns {{left: Float32Array, right: Float32Array}}
   */
  process(frames = this.bufferSize) {
    if (!this.initialized) return null;

    this.module._wasm_process(frames);

    // Read output from WASM memory
    const left = new Float32Array(
      this.module.HEAPF32.buffer, 
      this.outputL, 
      frames
    );
    const right = new Float32Array(
      this.module.HEAPF32.buffer, 
      this.outputR, 
      frames
    );

    return { left: new Float32Array(left), right: new Float32Array(right) };
  }

  // =========================================================================
  // SYNTH CONTROL
  // =========================================================================

  /**
   * Trigger a note
   * @param {number} note - MIDI note number (0-127)
   * @param {number} velocity - Velocity (0.0-1.0)
   */
  noteOn(note, velocity = 0.8) {
    this.module._wasm_note_on(note, velocity);
  }

  /**
   * Release the current note
   */
  noteOff() {
    this.module._wasm_note_off();
  }

  /**
   * Set oscillator waveform
   * @param {string|number} type - 'sine', 'saw', 'square', 'triangle' or type index
   */
  setWaveform(type) {
    const types = { sine: 0, saw: 1, square: 2, triangle: 3, noise: 4 };
    const typeIndex = typeof type === 'string' ? types[type.toLowerCase()] || 0 : type;
    this.module._wasm_set_waveform(typeIndex);
  }

  /**
   * Set waveform morph amount
   * @param {number} morph - Morph amount (0.0-1.0)
   */
  setMorph(morph) {
    this.module._wasm_set_morph(morph);
  }

  /**
   * Set filter parameters
   * @param {number} cutoff - Cutoff frequency in Hz (20-20000)
   * @param {number} resonance - Resonance amount (0.0-1.0)
   */
  setFilter(cutoff, resonance = 0.5) {
    this.module._wasm_set_filter(cutoff, resonance);
  }

  /**
   * Set envelope parameters
   * @param {number} attack - Attack time in seconds
   * @param {number} decay - Decay time in seconds
   * @param {number} sustain - Sustain level (0.0-1.0)
   * @param {number} release - Release time in seconds
   */
  setEnvelope(attack, decay, sustain, release) {
    this.module._wasm_set_envelope(attack, decay, sustain, release);
  }

  // =========================================================================
  // GENERATIVE
  // =========================================================================

  /**
   * Initialize Markov melody generator
   * @param {number} seed - Random seed
   */
  initMarkov(seed = Date.now()) {
    this.module._wasm_markov_init(seed);
  }

  /**
   * Set Markov generator temperature
   * @param {number} temperature - Temperature (0.1-2.0, lower = more predictable)
   */
  setMarkovTemperature(temperature) {
    this.module._wasm_markov_set_temperature(temperature);
  }

  /**
   * Get next Markov-generated note
   * @returns {number} MIDI note number
   */
  nextMarkovNote() {
    return this.module._wasm_markov_next();
  }

  /**
   * Initialize text-to-melody converter
   * @param {string} text - Input text
   */
  initTextMelody(text) {
    const textPtr = this.module.allocateUTF8(text);
    this.module._wasm_text_melody_init(textPtr);
    this.module._free(textPtr);
  }

  /**
   * Get next note from text melody
   * @returns {number} MIDI note number
   */
  nextTextNote() {
    return this.module._wasm_text_melody_next();
  }

  // =========================================================================
  // COLOR TO HARMONY
  // =========================================================================

  /**
   * Convert RGB color to musical harmony
   * @param {number} r - Red (0-255)
   * @param {number} g - Green (0-255)
   * @param {number} b - Blue (0-255)
   * @param {number} octave - Base octave (default: 4)
   * @returns {{root: number, chord: number[]}}
   */
  colorToHarmony(r, g, b, octave = 4) {
    this.module._wasm_color_to_harmony(r, g, b, octave);
    
    const root = this.module._wasm_color_get_root();
    const size = this.module._wasm_color_get_chord_size();
    const chord = [];
    
    for (let i = 0; i < size; i++) {
      chord.push(this.module._wasm_color_get_chord_note(i));
    }
    
    return { root, chord };
  }

  /**
   * Convert hex color to harmony
   * @param {string} hex - Hex color (e.g., '#FF5733')
   * @returns {{root: number, chord: number[]}}
   */
  hexToHarmony(hex, octave = 4) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return this.colorToHarmony(r, g, b, octave);
  }

  // =========================================================================
  // EFFECTS
  // =========================================================================

  /**
   * Initialize reverb effect
   */
  initReverb() {
    this.module._wasm_reverb_init(this.sampleRate);
  }

  /**
   * Set reverb parameters
   * @param {number} roomSize - Room size (0.0-1.0)
   * @param {number} damping - Damping amount (0.0-1.0)
   * @param {number} mix - Wet/dry mix (0.0-1.0)
   */
  setReverb(roomSize, damping = 0.5, mix = 0.3) {
    this.module._wasm_reverb_set(roomSize, damping, mix);
  }

  // =========================================================================
  // VISUALIZATION
  // =========================================================================

  /**
   * Get spectrum analyzer data
   * @param {number} numBands - Number of frequency bands (max 128)
   * @returns {Float32Array} Spectrum magnitudes
   */
  getSpectrum(numBands = 64) {
    const ptr = this.module._wasm_get_spectrum(numBands);
    return new Float32Array(this.module.HEAPF32.buffer, ptr, numBands);
  }

  /**
   * Get current audio levels
   * @returns {{left: number, right: number}}
   */
  getLevels() {
    return {
      left: this.module._wasm_get_level_l(),
      right: this.module._wasm_get_level_r()
    };
  }

  /**
   * Convert MIDI note to color (chromasynesthesia)
   * @param {number} note - MIDI note number
   * @returns {{r: number, g: number, b: number, hex: string}}
   */
  noteToColor(note) {
    const rgb = this.module._wasm_note_to_color(note);
    const r = (rgb >> 16) & 0xFF;
    const g = (rgb >> 8) & 0xFF;
    const b = rgb & 0xFF;
    const hex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    return { r, g, b, hex };
  }

  // =========================================================================
  // UTILITIES
  // =========================================================================

  /**
   * Get engine version
   */
  get version() {
    const ptr = this.module._wasm_version();
    return this.module.UTF8ToString(ptr);
  }

  /**
   * Get total feature count
   */
  get featureCount() {
    return this.module._wasm_feature_count();
  }

  /**
   * Convert MIDI note to frequency
   */
  static midiToFreq(note) {
    return 440 * Math.pow(2, (note - 69) / 12);
  }

  /**
   * Convert frequency to MIDI note
   */
  static freqToMidi(freq) {
    return 69 + 12 * Math.log2(freq / 440);
  }

  /**
   * Cleanup and free resources
   */
  destroy() {
    if (this.initialized) {
      this.module._wasm_free();
      this.initialized = false;
    }
  }
}

// =========================================================================
// AUDIO WORKLET PROCESSOR
// =========================================================================

/**
 * AudioWorklet processor for real-time audio
 * Register with: audioContext.audioWorklet.addModule('intuitives-processor.js')
 */
class IntuitivesProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.intuitives = null;
    this.port.onmessage = this.handleMessage.bind(this);
  }

  async handleMessage(event) {
    const { type, data } = event.data;

    switch (type) {
      case 'init':
        // Note: WASM loading in worklet requires special handling
        this.port.postMessage({ type: 'ready' });
        break;
      case 'noteOn':
        if (this.intuitives) this.intuitives.noteOn(data.note, data.velocity);
        break;
      case 'noteOff':
        if (this.intuitives) this.intuitives.noteOff();
        break;
      case 'setFilter':
        if (this.intuitives) this.intuitives.setFilter(data.cutoff, data.resonance);
        break;
    }
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];

    if (this.intuitives) {
      const { left, right } = this.intuitives.process(128);
      output[0].set(left);
      if (output[1]) output[1].set(right);
    }

    return true;
  }

  static get parameterDescriptors() {
    return [
      { name: 'cutoff', defaultValue: 2000, minValue: 20, maxValue: 20000 },
      { name: 'resonance', defaultValue: 0.5, minValue: 0, maxValue: 1 },
      { name: 'morph', defaultValue: 0, minValue: 0, maxValue: 1 }
    ];
  }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Intuitives, IntuitivesProcessor };
}

if (typeof window !== 'undefined') {
  window.Intuitives = Intuitives;
}

export { Intuitives, IntuitivesProcessor };
export default Intuitives;
