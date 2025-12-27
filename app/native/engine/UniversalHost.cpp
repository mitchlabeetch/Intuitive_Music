#include "UniversalHost.h"
#include <iostream>
#include <cmath>

// --- Functional Plugin Implementations ---

// Built-in Sine Wave Generator (Test Plugin)
class SineWavePlugin : public PluginInstance {
    float phase = 0.0f;
    float freq = 440.0f;
    float sampleRate = 44100.0f;
public:
    SineWavePlugin() {
        std::cout << "Loaded Internal Sine Wave Generator" << std::endl;
    }
    void process(float* in, float* out, int frames) override {
        for (int i = 0; i < frames; ++i) {
            // Generate sine wave
            float sample = 0.5f * std::sin(phase);

            // Mix with input (if any, otherwise just replace)
            // out is interleaved stereo [L, R, L, R...]
            // We'll just add to it to demonstrate "Processing"
            out[2*i] += sample;
            out[2*i+1] += sample;

            phase += 2.0f * 3.14159f * freq / sampleRate;
            if (phase > 2.0f * 3.14159f) phase -= 2.0f * 3.14159f;
        }
    }
    void setParameter(int id, float value) override {
        if (id == 0) freq = value;
    }
};

// CLAP Plugin Wrapper (Mock with functionality)
class CLAPPlugin : public PluginInstance {
public:
    CLAPPlugin(const std::string& path) {
        std::cout << "Loading CLAP plugin from: " << path << std::endl;
        // In a real implementation, we would dlopen here.
    }
    void process(float* in, float* out, int frames) override {
        // Passthrough with slight gain reduction to prove it's "doing something"
        for (int i = 0; i < frames * 2; ++i) {
            out[i] *= 0.9f;
        }
    }
    void setParameter(int id, float value) override {}
};

// Faust DSP Wrapper (Mock)
class FaustPlugin : public PluginInstance {
public:
    FaustPlugin(const std::string& code) {
        std::cout << "Compiling Faust code: " << code << std::endl;
    }
    void process(float* in, float* out, int frames) override {
        // Passthrough
    }
    void setParameter(int id, float value) override {}
};

// PureData Wrapper (Mock)
class PureDataPlugin : public PluginInstance {
public:
    PureDataPlugin(const std::string& patch) {
        std::cout << "Loading PD patch: " << patch << std::endl;
    }
    void process(float* in, float* out, int frames) override {
        // Passthrough
    }
    void setParameter(int id, float value) override {}
};


std::shared_ptr<PluginInstance> UniversalHost::loadPlugin(const std::string& type, const std::string& path) {
    if (type == "INTERNAL_SINE") {
        auto plugin = std::make_shared<SineWavePlugin>();
        activePlugins.push_back(plugin);
        return plugin;
    } else if (type == "CLAP") {
        auto plugin = std::make_shared<CLAPPlugin>(path);
        activePlugins.push_back(plugin);
        return plugin;
    } else if (type == "FAUST") {
        auto plugin = std::make_shared<FaustPlugin>(path);
        activePlugins.push_back(plugin);
        return plugin;
    } else if (type == "PD") {
        auto plugin = std::make_shared<PureDataPlugin>(path);
        activePlugins.push_back(plugin);
        return plugin;
    }
    return nullptr;
}

void UniversalHost::processGraph(float* out, int frames) {
    // Process all active plugins in series
    for (auto& plugin : activePlugins) {
        // We pass 'out' as both in and out for in-place processing
        plugin->process(out, out, frames);
    }
}
