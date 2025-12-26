/**
 * INTUITIVES - Universal Audio Processor Interface
 *
 * Generic abstraction for all audio processing nodes:
 * - Internal oscillators/synths
 * - External plugins (CLAP, VST3)
 * - Faust DSP
 * - Pure Data patches
 * - AI-generated processors
 *
 * "Does this sound cool?" - The only rule.
 *
 * (C) 2024 - MIT License
 */

#ifndef INTUITIVES_PROCESSOR_H
#define INTUITIVES_PROCESSOR_H

#include "core.h"
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// AUDIO NODE TYPES
// ============================================================================

typedef enum {
  NODE_TYPE_INTERNAL = 0, // Built-in oscillators/effects
  NODE_TYPE_CLAP,         // CLAP plugin
  NODE_TYPE_VST3,         // VST3 plugin
  NODE_TYPE_FAUST,        // Faust DSP
  NODE_TYPE_PUREDATA,     // Pure Data patch
  NODE_TYPE_AI_GENERATED, // AI-generated processor
  NODE_TYPE_EXTERNAL      // Generic external processor
} AudioNodeType;

typedef enum {
  NODE_CATEGORY_INSTRUMENT = 0, // Sound generator
  NODE_CATEGORY_EFFECT,         // Audio effect
  NODE_CATEGORY_ANALYZER,       // Visualization/analysis only
  NODE_CATEGORY_MIDI_EFFECT,    // MIDI processor
  NODE_CATEGORY_UTILITY         // Utility (gain, pan, routing)
} AudioNodeCategory;

// Forward declarations
typedef struct AudioNode AudioNode;
typedef struct MidiEvent MidiEvent;
typedef struct ParameterInfo ParameterInfo;
typedef struct NodeConnection NodeConnection;

// ============================================================================
// MIDI EVENT
// ============================================================================

typedef struct MidiEvent {
  uint8_t status;    // MIDI status byte
  uint8_t data1;     // First data byte (note/CC number)
  uint8_t data2;     // Second data byte (velocity/value)
  uint8_t channel;   // MIDI channel (0-15)
  SampleTime offset; // Sample offset within buffer
} MidiEvent;

#define MIDI_NOTE_ON 0x90
#define MIDI_NOTE_OFF 0x80
#define MIDI_CC 0xB0
#define MIDI_PITCH_BEND 0xE0
#define MIDI_AFTERTOUCH 0xD0
#define MIDI_POLY_AFTERTOUCH 0xA0
#define MIDI_PROGRAM_CHANGE 0xC0

// ============================================================================
// PARAMETER INFO
// ============================================================================

typedef struct ParameterInfo {
  uint32_t id;
  char name[64];
  char short_name[16];
  float min_value;
  float max_value;
  float default_value;
  float step; // 0 for continuous
  bool is_automatable;
  bool is_modulatable;
  char unit[16]; // dB, Hz, %, ms, etc.
} ParameterInfo;

// ============================================================================
// NODE CONNECTIONS (Signal Flow Graph)
// ============================================================================

typedef struct NodeConnection {
  AudioNode *source;
  AudioNode *destination;
  uint32_t source_output;      // Output port index
  uint32_t destination_input;  // Input port index
  float gain;                  // Connection gain (default 1.0)
  struct NodeConnection *next; // Linked list
} NodeConnection;

// ============================================================================
// AUDIO NODE (Universal Interface)
// ============================================================================

/**
 * AudioNode - The Universal Audio Processor Interface
 *
 * Every sound source and effect in Intuitives implements this interface.
 * This enables:
 * - Unified processing pipeline
 * - Hot-swapping of processors
 * - Plugin hosting (CLAP, VST3)
 * - AI-generated processors
 * - Dynamic routing graphs
 */
typedef struct AudioNode {
  // === Identification ===
  uint32_t id;
  char name[64];
  AudioNodeType type;
  AudioNodeCategory category;

  // === Instance Data ===
  void *instance_data;     // Type-specific state (opaque pointer)
  void *plugin_handle;     // For external plugins (loaded library)
  uint32_t sample_rate;    // Current sample rate
  uint32_t max_block_size; // Maximum processing block size

  // === Port Configuration ===
  uint32_t num_audio_inputs;
  uint32_t num_audio_outputs;
  uint32_t num_midi_inputs;
  uint32_t num_midi_outputs;

  // === Parameters ===
  uint32_t num_parameters;
  ParameterInfo *parameters; // Array of parameter info

  // === Connections ===
  NodeConnection *input_connections;  // Linked list of inputs
  NodeConnection *output_connections; // Linked list of outputs

  // === State ===
  bool is_active;
  bool is_bypassed;
  _Atomic bool needs_reset; // Atomic flag for thread-safe reset

  // === Function Pointers (Virtual Methods) ===

  /**
   * Initialize the node with the given sample rate and block size.
   * Called before processing begins.
   */
  IntuitivesResult (*init)(AudioNode *self, uint32_t sample_rate,
                           uint32_t max_block_size);

  /**
   * Free all resources associated with this node.
   */
  void (*free)(AudioNode *self);

  /**
   * Activate the node (prepare for processing).
   * Called when entering playback mode.
   */
  void (*activate)(AudioNode *self);

  /**
   * Deactivate the node (stop processing).
   * Called when leaving playback mode.
   */
  void (*deactivate)(AudioNode *self);

  /**
   * Reset the node's internal state (e.g., clear delays, reset filters).
   * Called on transport stop or loop point.
   */
  void (*reset)(AudioNode *self);

  /**
   * Process a block of audio.
   *
   * @param inputs  Array of input channel pointers (or NULL for generators)
   * @param outputs Array of output channel pointers
   * @param frames  Number of sample frames to process
   */
  void (*process_audio)(AudioNode *self, float **inputs, float **outputs,
                        uint32_t frames);

  /**
   * Process MIDI events.
   *
   * @param events Array of MIDI events
   * @param count  Number of events
   */
  void (*process_midi)(AudioNode *self, MidiEvent *events, uint32_t count);

  /**
   * Get the current value of a parameter.
   *
   * @param param_id Parameter ID
   * @param value    Output value
   */
  void (*get_parameter)(AudioNode *self, uint32_t param_id, float *value);

  /**
   * Set the value of a parameter.
   *
   * @param param_id Parameter ID
   * @param value    New value
   */
  void (*set_parameter)(AudioNode *self, uint32_t param_id, float value);

  /**
   * Mutate parameters randomly (Happy Accidents feature).
   *
   * @param amount Mutation amount (0.0-1.0, percentage of range)
   * @param seed   Random seed (0 for random)
   */
  void (*mutate)(AudioNode *self, float amount, uint32_t seed);

  /**
   * Get the node's current state as a serializable blob.
   * Used for presets and undo/redo.
   *
   * @param data      Output buffer (if NULL, returns required size)
   * @param max_size  Maximum size of output buffer
   * @return          Actual size of state data
   */
  size_t (*save_state)(AudioNode *self, void *data, size_t max_size);

  /**
   * Restore the node's state from a serialized blob.
   *
   * @param data Data buffer
   * @param size Size of data
   */
  IntuitivesResult (*load_state)(AudioNode *self, const void *data,
                                 size_t size);

} AudioNode;

// ============================================================================
// NODE FACTORY FUNCTIONS
// ============================================================================

/**
 * Create a new AudioNode with default values.
 * Caller must set function pointers and initialize.
 */
static inline AudioNode *audio_node_create(void) {
  AudioNode *node = (AudioNode *)calloc(1, sizeof(AudioNode));
  if (node) {
    node->is_active = false;
    node->is_bypassed = false;
    atomic_init(&node->needs_reset, false);
  }
  return node;
}

/**
 * Destroy an AudioNode (calls free if set, then deallocates).
 */
static inline void audio_node_destroy(AudioNode *node) {
  if (node) {
    if (node->free) {
      node->free(node);
    }
    if (node->parameters) {
      free(node->parameters);
    }
    free(node);
  }
}

/**
 * Check if a node is ready for processing.
 */
static inline bool audio_node_is_ready(const AudioNode *node) {
  return node && node->is_active && !node->is_bypassed && node->process_audio;
}

/**
 * Request a reset on the next processing cycle (thread-safe).
 */
static inline void audio_node_request_reset(AudioNode *node) {
  if (node) {
    atomic_store(&node->needs_reset, true);
  }
}

/**
 * Check and clear the reset flag (called from audio thread).
 */
static inline bool audio_node_check_reset(AudioNode *node) {
  if (node && atomic_load(&node->needs_reset)) {
    atomic_store(&node->needs_reset, false);
    return true;
  }
  return false;
}

// ============================================================================
// NODE CONNECTION HELPERS
// ============================================================================

/**
 * Connect two nodes.
 */
static inline NodeConnection *node_connect(AudioNode *source,
                                           uint32_t source_output,
                                           AudioNode *destination,
                                           uint32_t destination_input) {
  NodeConnection *conn = (NodeConnection *)calloc(1, sizeof(NodeConnection));
  if (conn) {
    conn->source = source;
    conn->destination = destination;
    conn->source_output = source_output;
    conn->destination_input = destination_input;
    conn->gain = 1.0f;

    // Add to source's output list
    conn->next = source->output_connections;
    source->output_connections = conn;
  }
  return conn;
}

/**
 * Disconnect two nodes.
 */
static inline void node_disconnect(AudioNode *source, AudioNode *destination) {
  NodeConnection **prev = &source->output_connections;
  NodeConnection *conn = source->output_connections;

  while (conn) {
    if (conn->destination == destination) {
      *prev = conn->next;
      free(conn);
      return;
    }
    prev = &conn->next;
    conn = conn->next;
  }
}

// ============================================================================
// BUILT-IN NODE TYPES (Factory Functions)
// ============================================================================

// Forward declarations for built-in node factories
// These will be implemented in separate .c files

/**
 * Create a built-in oscillator node.
 * @param wave_type Waveform type (from core.h WaveformType enum)
 */
AudioNode *create_oscillator_node(WaveformType wave_type);

/**
 * Create a built-in effect node.
 * @param effect_type Effect type (from core.h EffectType enum)
 */
AudioNode *create_effect_node(EffectType effect_type);

/**
 * Create a gain/utility node.
 */
AudioNode *create_gain_node(void);

/**
 * Load a CLAP plugin as an AudioNode.
 * @param path Path to the .clap bundle
 */
AudioNode *load_clap_plugin(const char *path);

/**
 * Load a VST3 plugin as an AudioNode.
 * @param path Path to the .vst3 bundle
 */
AudioNode *load_vst3_plugin(const char *path);

/**
 * Compile and load a Faust DSP as an AudioNode.
 * @param dsp_code Faust DSP source code
 */
AudioNode *load_faust_dsp(const char *dsp_code);

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_PROCESSOR_H
