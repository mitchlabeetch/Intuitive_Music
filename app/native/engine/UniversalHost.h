#ifndef UNIVERSAL_HOST_H
#define UNIVERSAL_HOST_H

#include <vector>
#include <string>
#include <memory>
#include <iostream>

// Abstract base class for all plugins (The "Wrapper")
class PluginInstance {
public:
    virtual ~PluginInstance() {}
    virtual void process(float* in, float* out, int frames) = 0;
    virtual void setParameter(int id, float value) = 0;
};

// Universal Host managing different types of plugins
class UniversalHost {
public:
    static UniversalHost& getInstance() {
        static UniversalHost instance;
        return instance;
    }

    // Factory method to load plugins based on type
    std::shared_ptr<PluginInstance> loadPlugin(const std::string& type, const std::string& path);

    void processGraph(float* out, int frames);

private:
    UniversalHost() {
        // Initialize with default internal plugins if needed
    }
    std::vector<std::shared_ptr<PluginInstance>> activePlugins;
};

#endif // UNIVERSAL_HOST_H
