#ifndef DATASET_INTEGRATIONS_H
#define DATASET_INTEGRATIONS_H

#include <string>
#include <vector>
#include <iostream>

// --- Dataset Loading Frameworks ---

// 1. Free Music Archive (FMA) Loader
// "Integration Goal: Training data for our internal classifiers."
class FMALoader {
public:
    void loadMetadata(const std::string& csvPath) {
        // Implementation Strategy:
        // Parse tracks.csv using efficient CSV parser
        // Store genre/tempo tags in internal DB (SQLite or std::map)
        std::cout << "Loading FMA metadata from " << csvPath << std::endl;
    }

    std::vector<float> loadSample(int trackId) {
        // Implementation Strategy:
        // Construct path from trackId (e.g. 000/000123.mp3)
        // Decode using libsndfile/ffmpeg
        return {};
    }
};

// 2. NSynth Loader
// "Integration Goal: Infinite sample library."
class NSynthLoader {
public:
    struct InstrumentAttributes {
        std::string family;
        int pitch;
        int velocity;
    };

    void indexDataset(const std::string& rootPath) {
        // Implementation Strategy:
        // Walk directory, parse filename "guitar_acoustic_001-060-100.wav"
        // Populate fast lookup index
        std::cout << "Indexing NSynth dataset at " << rootPath << std::endl;
    }
};

// 3. AudioSet Ontology
// "Integration Goal: Ontology for sample library tags."
class AudioSetOntology {
public:
    void loadOntology(const std::string& jsonPath) {
        // Implementation Strategy:
        // Parse ontology.json
        // Build graph of ID -> Label (e.g., "/m/0dgw9r" -> "Human sounds")
        std::cout << "Loading AudioSet ontology..." << std::endl;
    }
};

// 4. Common Voice Loader
class CommonVoiceLoader {
public:
    void loadTranscript(const std::string& tsvPath) {
        std::cout << "Loading Common Voice transcripts..." << std::endl;
    }
};

#endif // DATASET_INTEGRATIONS_H
