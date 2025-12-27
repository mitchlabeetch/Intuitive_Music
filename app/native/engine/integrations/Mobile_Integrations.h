#ifndef MOBILE_INTEGRATIONS_H
#define MOBILE_INTEGRATIONS_H

// --- Mobile / C++ Audio Engine Integrations ---

// 1. AudioKit Wrapper (C++ DSP Extraction)
// "Integration Goal: Extract the DSP kernels (Oscillators, Filters) for use in our Engine."
class AudioKitWrapper {
public:
    // Implementation Strategy:
    // AudioKit's core is often C++. We can link the `AudioKit/Core` folder.
    // Example wrapper for a Moog Filter from AudioKit
    void process_moog_filter(float* in, float* out, int frames, float cutoff) {
        // Pseudo-code for AudioKit's AKMoogLadder
        // static AKMoogLadder filter;
        // filter.setCutoff(cutoff);
        // filter.process(in, out, frames);
    }
};

// 2. React Native Sound (Cross-Platform I/O)
class OboeWrapper {
public:
    // For Android Low-Latency
    void initOboe() {
        // oboe::AudioStreamBuilder builder;
        // builder.setDirection(oboe::Direction::Output);
        // builder.setPerformanceMode(oboe::PerformanceMode::LowLatency);
        // builder.start();
    }
};

// 3. SuperCollider (scsynth) Integration
// "Control it via OSC (Open Sound Control) over UDP port 57110."
class SuperColliderClient {
public:
    void send_synth_def(const std::string& name, float freq) {
        // Implementation Strategy:
        // Use `liblo` or `tinyosc` to send UDP packet to 127.0.0.1:57110
        // Msg: ["/s_new", "sine", 1000, 1, 0, "freq", freq]
    }
};

#endif // MOBILE_INTEGRATIONS_H
