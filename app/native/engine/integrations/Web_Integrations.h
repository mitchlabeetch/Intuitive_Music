#ifndef WEB_INTEGRATIONS_H
#define WEB_INTEGRATIONS_H

// --- Web / Frontend Audio Bridge ---

// 1. Tone.js Bridge (Shared Memory / WebSocket)
class ToneBridge {
public:
    void triggerAttackRelease(const std::string& note, const std::string& duration) {
        // Implementation Strategy:
        // Send command to Frontend via WebSocket to trigger Tone.PolySynth
        // Server::send("TONE_TRIGGER", {note, duration});
    }
};

// 2. WebAudio API (WASM Export)
// "Compile C++ DSP to .wasm"
// This class is a placeholder for the Emscripten binding logic.
class WebAudioWASM {
public:
    // This function would be exported to JS via Emscripten
    // EMSCRIPTEN_KEEPALIVE
    void process_audio_block(float* buffer, int size) {
        // Run C++ DSP here
    }
};

// 3. AudioWorklet Helper
class AudioWorkletProcessor {
    // Strategy:
    // This C++ code is compiled to WASM.
    // The JS `AudioWorkletProcessor` calls this `process` method.
};

#endif // WEB_INTEGRATIONS_H
