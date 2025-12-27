#ifndef DAW_H
#define DAW_H

#include <vector>
#include <string>
#include <mutex>
#include <memory>
#include <atomic>
#include "UniversalHost.h"

// Include all Integration Frameworks to ensure they are part of the engine
#include "integrations/AI_Integrations.h"
#include "integrations/Mobile_Integrations.h"
#include "integrations/Web_Integrations.h"
#include "integrations/Plugin_Integrations.h"
#include "integrations/Dataset_Integrations.h"

#ifdef _WIN32
  #define EXPORT extern "C" __declspec(dllexport)
#else
  #define EXPORT extern "C"
#endif

struct Track {
    std::string fileName;
    int sampleRate;
    int channels;
    double duration;
    std::vector<float> audioData;
    std::atomic<size_t> playbackPosition{0};
};

class DAW {
public:
    static DAW& getInstance() {
        static DAW instance;
        return instance;
    }

    // Initialize all integration subsystems
    void initIntegrations();

    void addTrack(const std::string& filePath);
    void removeTrack(int index);
    std::vector<std::shared_ptr<Track>>& getTracks();

    void play();
    void playAll();
    void stop();
    bool isPlaying() const;

    void loadPlugin(const std::string& type, const std::string& path);
    int fillMixedBuffer(float* out, unsigned long frames);

private:
    DAW() {
        initIntegrations();
    }

    std::vector<std::shared_ptr<Track>> tracks;
    std::vector<float> mixedAudioBuffer;
    std::atomic<size_t> mixPlaybackPosition{0};
    std::atomic<bool> playing{false};
    std::mutex trackMutex;

    // Subsystem Managers
    std::unique_ptr<AudioCraftWrapper> aiAudioCraft;
    std::unique_ptr<MagentaWrapper> aiMagenta;
    std::unique_ptr<FMALoader> datasetFMA;
    std::unique_ptr<AudioSetOntology> datasetOntology;
    // ... add others as needed

    void loadAudio(const std::string& filePath, Track& track);
};

// C Interface
EXPORT void DAW_AddTrack(const char* filePath);
EXPORT void DAW_RemoveTrack(int index);
EXPORT void DAW_Play();
EXPORT void DAW_PlayAll();
EXPORT void DAW_Stop();
EXPORT bool DAW_IsPlaying();
EXPORT void DAW_LoadPlugin(const char* type, const char* path);

#endif
