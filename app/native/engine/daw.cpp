#include "daw.h"
#include <sndfile.h>
#include <portaudio.h>
#include <stdexcept>
#include <iostream>
#include <thread>
#include <string>
#include <cstring>
#include <algorithm>
#include <mutex>

// --- Singleton Wrapper Implementations ---

void DAW_AddTrack(const char* filePath) {
    try {
        DAW::getInstance().addTrack(std::string(filePath));
    } catch (const std::exception& e) {
        std::cerr << "Error adding track: " << e.what() << std::endl;
    }
}

void DAW_RemoveTrack(int index) {
    DAW::getInstance().removeTrack(index);
}

void DAW_Play() {
    DAW::getInstance().play();
}

void DAW_PlayAll() {
    DAW::getInstance().playAll();
}

void DAW_Stop() {
    DAW::getInstance().stop();
}

bool DAW_IsPlaying() {
    return DAW::getInstance().isPlaying();
}

void DAW_LoadPlugin(const char* type, const char* path) {
    DAW::getInstance().loadPlugin(type, path);
}

// --- Class Implementations ---

void DAW::initIntegrations() {
    std::cout << "--- Initializing Intuitives Engine Integrations ---" << std::endl;

    // Initialize AI
    aiAudioCraft = std::make_unique<AudioCraftWrapper>();
    aiMagenta = std::make_unique<MagentaWrapper>();
    std::cout << "[AI] AudioCraft and Magenta wrappers initialized." << std::endl;

    // Initialize Datasets
    datasetFMA = std::make_unique<FMALoader>();
    datasetOntology = std::make_unique<AudioSetOntology>();
    std::cout << "[DATA] FMA and AudioSet frameworks ready." << std::endl;

    // Initialize Plugin Host (handled by UniversalHost singleton)
    std::cout << "[PLUGINS] Universal Host ready for CLAP/VST3/Faust." << std::endl;

    std::cout << "--- Integrations Loaded Successfully ---" << std::endl;
}

void DAW::loadPlugin(const std::string& type, const std::string& path) {
    UniversalHost::getInstance().loadPlugin(type, path);
}

static int audioCallback(const void* inputBuffer, void* outputBuffer,
    unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo,
    PaStreamCallbackFlags statusFlags, void* userData) {

    auto* track = reinterpret_cast<Track*>(userData);
    auto* out = static_cast<float*>(outputBuffer);

    if (!track) {
         std::fill(out, out + framesPerBuffer * 2, 0.0f);
         return paContinue;
    }

    size_t currentPos = track->playbackPosition.load();
    size_t remaining = track->audioData.size() - currentPos;
    size_t toCopy = std::min<size_t>(framesPerBuffer * track->channels, remaining);

    std::copy(track->audioData.begin() + currentPos, track->audioData.begin() + currentPos + toCopy, out);
    track->playbackPosition.store(currentPos + toCopy);

    if (toCopy < framesPerBuffer * track->channels) {
        std::fill(out + toCopy, out + framesPerBuffer * track->channels, 0.0f);
        track->playbackPosition.store(0);
        return paComplete;
    }

    return paContinue;
}

void DAW::addTrack(const std::string& filePath) {
    std::lock_guard<std::mutex> lock(trackMutex);
    auto track = std::make_shared<Track>();
    loadAudio(filePath, *track);
    tracks.push_back(track);
}

void DAW::removeTrack(int index) {
    std::lock_guard<std::mutex> lock(trackMutex);
    if (playing) {
        stop();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    if (index >= 0 && index < tracks.size()) {
        tracks.erase(tracks.begin() + index);
    }
}

std::vector<std::shared_ptr<Track>>& DAW::getTracks() {
    return tracks;
}

void DAW::loadAudio(const std::string& filePath, Track& track) {
    SF_INFO sfInfo;
    SNDFILE* sndFile = sf_open(filePath.c_str(), SFM_READ, &sfInfo);
    if (!sndFile) {
        throw std::runtime_error("Failed to open audio file: " + filePath);
    }

    track.fileName = filePath;
    track.sampleRate = sfInfo.samplerate;
    track.channels = sfInfo.channels;
    track.duration = static_cast<double>(sfInfo.frames) / sfInfo.samplerate;
    track.playbackPosition = 0;

    size_t totalFrames = sfInfo.frames * sfInfo.channels;
    track.audioData.resize(totalFrames);

    sf_read_float(sndFile, track.audioData.data(), totalFrames);
    sf_close(sndFile);
}

void DAW::play() {
    std::lock_guard<std::mutex> lock(trackMutex);
    if (tracks.empty() || playing) return;

    playing = true;
    Pa_Initialize();

    auto track = tracks[0];
    track->playbackPosition = 0;

    PaStream* stream;
    Pa_OpenDefaultStream(&stream, 0, track->channels, paFloat32, track->sampleRate,
        256, audioCallback, track.get());
    Pa_StartStream(stream);

    std::thread playbackThread([stream, this]() {
        while (Pa_IsStreamActive(stream) == 1) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            if (!this->playing) {
                Pa_StopStream(stream);
            }
        }
        Pa_CloseStream(stream);
        Pa_Terminate();
        this->playing = false;
        });
    playbackThread.detach();
}

static int mixedAudioCallback(const void* inputBuffer, void* outputBuffer,
    unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo,
    PaStreamCallbackFlags statusFlags, void* userData) {

    auto* daw = static_cast<DAW*>(userData);
    auto* out = static_cast<float*>(outputBuffer);
    return daw->fillMixedBuffer(out, framesPerBuffer);
}

int DAW::fillMixedBuffer(float* out, unsigned long frames) {
    size_t currentPos = mixPlaybackPosition.load();
    size_t remaining = mixedAudioBuffer.size() - currentPos;
    size_t toCopy = std::min<size_t>(frames * 2, remaining);

    std::copy(mixedAudioBuffer.begin() + currentPos, mixedAudioBuffer.begin() + currentPos + toCopy, out);
    mixPlaybackPosition.store(currentPos + toCopy);

    UniversalHost::getInstance().processGraph(out, frames);

    if (toCopy < frames * 2) {
        std::fill(out + toCopy, out + frames * 2, 0.0f);
        mixPlaybackPosition.store(0);
        return paComplete;
    }
    return paContinue;
}


void DAW::playAll() {
    std::lock_guard<std::mutex> lock(trackMutex);
    if (tracks.empty() || playing) return;

    playing = true;
    Pa_Initialize();

    size_t maxSamples = 0;
    for (const auto& track : tracks) {
        maxSamples = std::max(maxSamples, track->audioData.size());
    }

    mixedAudioBuffer.assign(maxSamples, 0.0f);
    mixPlaybackPosition = 0;

    for (const auto& track : tracks) {
        for (size_t i = 0; i < track->audioData.size(); ++i) {
            mixedAudioBuffer[i] += track->audioData[i] / tracks.size();
        }
    }

    PaStream* stream;
    Pa_OpenDefaultStream(&stream, 0, 2, paFloat32, tracks[0]->sampleRate, 256,
        mixedAudioCallback, this);

    Pa_StartStream(stream);

    std::thread playbackThread([stream, this]() {
        while (Pa_IsStreamActive(stream) == 1) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            if (!this->playing) {
                Pa_StopStream(stream);
            }
        }
        Pa_CloseStream(stream);
        Pa_Terminate();
        this->playing = false;
        });
    playbackThread.detach();
}


void DAW::stop() {
    playing = false;
}

bool DAW::isPlaying() const {
    return playing;
}
