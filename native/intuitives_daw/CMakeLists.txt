cmake_minimum_required(VERSION 3.16)
project(IntuitivesDAW VERSION 0.6.0 LANGUAGES C CXX)

# INTUITIVES DAW v0.6 BETA
# "Does this sound cool?" - The only rule.

set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# macOS Intel architecture (x86_64)
if(APPLE)
    set(CMAKE_OSX_ARCHITECTURES "x86_64" CACHE STRING "Build for Intel architecture")
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum macOS version")
endif()

# Options
option(INTUITIVES_DAW_BUILD_GUI "Build with Dear ImGui GUI" OFF)
option(INTUITIVES_DAW_USE_ENGINE "Use Intuitives Core Engine" ON)

# ============================================================================
# PLATFORM DETECTION
# ============================================================================

if(APPLE)
    set(PLATFORM_MACOS TRUE)
    add_definitions(-DSG_OS=0)  # macOS
elseif(UNIX)
    set(PLATFORM_LINUX TRUE)
    add_definitions(-DSG_OS=1)  # Linux
elseif(WIN32)
    set(PLATFORM_WINDOWS TRUE)
    add_definitions(-DSG_OS=2)  # Windows
endif()

# Cache line size for lock-free structures
add_definitions(-DCACHE_LINE_SIZE=64)
add_definitions(-D_GNU_SOURCE)

# ============================================================================
# INTUITIVES DSP LIBRARY (our 40 features)
# ============================================================================

set(INTUITIVES_ENGINE_DIR ${CMAKE_SOURCE_DIR}/../)
include_directories(${INTUITIVES_ENGINE_DIR}/include)

set(INTUITIVES_DSP_SOURCES
    ${INTUITIVES_ENGINE_DIR}/src/core/engine.c
    ${INTUITIVES_ENGINE_DIR}/src/dsp/oscillators.c
    ${INTUITIVES_ENGINE_DIR}/src/dsp/effects.c
    ${INTUITIVES_ENGINE_DIR}/src/generators/generators.c
    ${INTUITIVES_ENGINE_DIR}/src/input/input.c
    ${INTUITIVES_ENGINE_DIR}/src/visual/visual.c
)

# ============================================================================
# INTUITIVES CORE ENGINE (full DAW core)
# ============================================================================

if(INTUITIVES_DAW_USE_ENGINE)
    set(ENGINE_DIR ${CMAKE_SOURCE_DIR}/intuitives_engine)
    include_directories(${ENGINE_DIR}/include)
    include_directories(${ENGINE_DIR}/libcds/include)
    
    # Find all engine source files
    file(GLOB_RECURSE ENGINE_SRC_FILES 
        "${ENGINE_DIR}/src/*.c"
    )
    file(GLOB_RECURSE ENGINE_LIBCDS_FILES
        "${ENGINE_DIR}/libcds/src/*.c"
    )
    
    # Exclude CLI main file (we have our own)
    list(FILTER ENGINE_SRC_FILES EXCLUDE REGEX "_main\\.c$")
    
    set(ENGINE_SOURCES
        ${ENGINE_SRC_FILES}
        ${ENGINE_LIBCDS_FILES}
    )
    
    # Build Intuitives Core engine as a static library
    add_library(intuitives_engine STATIC ${ENGINE_SOURCES})
    target_include_directories(intuitives_engine PUBLIC 
        ${ENGINE_DIR}/include
        ${ENGINE_DIR}/libcds/include
    )
    target_compile_options(intuitives_engine PRIVATE -O2 -ffast-math)
    
    # Link engine dependencies
    if(PLATFORM_MACOS)
        find_library(COREAUDIO CoreAudio)
        find_library(AUDIOTOOLBOX AudioToolbox)
        find_library(COREFOUNDATION CoreFoundation)
        target_link_libraries(intuitives_engine PUBLIC
            ${COREAUDIO}
            ${AUDIOTOOLBOX}
            ${COREFOUNDATION}
        )
    elseif(PLATFORM_LINUX)
        find_package(ALSA QUIET)
        if(ALSA_FOUND)
            target_link_libraries(intuitives_engine PUBLIC ${ALSA_LIBRARIES})
            target_include_directories(intuitives_engine PUBLIC ${ALSA_INCLUDE_DIRS})
        endif()
    endif()
    
    # Find PortAudio (audio backend)
    find_library(PORTAUDIO_LIB portaudio HINTS /usr/local/lib /opt/homebrew/lib)
    find_path(PORTAUDIO_INCLUDE portaudio.h HINTS /usr/local/include /opt/homebrew/include)
    if(PORTAUDIO_LIB AND PORTAUDIO_INCLUDE)
        target_include_directories(intuitives_engine PUBLIC ${PORTAUDIO_INCLUDE})
        target_link_libraries(intuitives_engine PUBLIC ${PORTAUDIO_LIB})
        message(STATUS "Found PortAudio: ${PORTAUDIO_LIB}")
    endif()
    
    # Find PortMIDI
    find_library(PORTMIDI_LIB portmidi HINTS /usr/local/lib /opt/homebrew/lib)
    if(PORTMIDI_LIB)
        target_link_libraries(intuitives_engine PUBLIC ${PORTMIDI_LIB})
        message(STATUS "Found PortMIDI: ${PORTMIDI_LIB}")
    endif()
    
    # Find libsndfile
    find_library(SNDFILE_LIB sndfile HINTS /usr/local/lib /opt/homebrew/lib)
    find_path(SNDFILE_INCLUDE sndfile.h HINTS /usr/local/include /opt/homebrew/include)
    if(SNDFILE_LIB AND SNDFILE_INCLUDE)
        target_include_directories(intuitives_engine PUBLIC ${SNDFILE_INCLUDE})
        target_link_libraries(intuitives_engine PUBLIC ${SNDFILE_LIB})
        message(STATUS "Found libsndfile: ${SNDFILE_LIB}")
    endif()
    
    # Find FFTW3
    find_library(FFTW3_LIB fftw3 HINTS /usr/local/lib /opt/homebrew/lib)
    find_library(FFTW3F_LIB fftw3f HINTS /usr/local/lib /opt/homebrew/lib)
    if(FFTW3_LIB)
        target_link_libraries(intuitives_engine PUBLIC ${FFTW3_LIB})
    endif()
    if(FFTW3F_LIB)
        target_link_libraries(intuitives_engine PUBLIC ${FFTW3F_LIB})
    endif()
    
    target_link_libraries(intuitives_engine PUBLIC m pthread)
endif()

# ============================================================================
# DAW APPLICATION
# ============================================================================

include_directories(${CMAKE_SOURCE_DIR}/include)

set(DAW_SOURCES
    src/main.cpp
    ${INTUITIVES_DSP_SOURCES}
)

add_executable(IntuitivesDAW ${DAW_SOURCES})

# Compiler flags
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(IntuitivesDAW PRIVATE -Wall -Wextra -O2 -ffast-math)
endif()

# Link Intuitives Core engine if enabled
if(INTUITIVES_DAW_USE_ENGINE)
    target_link_libraries(IntuitivesDAW PRIVATE intuitives_engine)
    target_compile_definitions(IntuitivesDAW PRIVATE USE_INTUITIVES_ENGINE=1)
endif()

# Platform-specific linking
if(PLATFORM_MACOS)
    target_link_libraries(IntuitivesDAW PRIVATE
        "-framework CoreAudio"
        "-framework AudioToolbox" 
        "-framework CoreFoundation"
        "-framework Accelerate"
    )
elseif(PLATFORM_LINUX)
    find_package(ALSA QUIET)
    if(ALSA_FOUND)
        target_link_libraries(IntuitivesDAW PRIVATE ${ALSA_LIBRARIES})
        target_include_directories(IntuitivesDAW PRIVATE ${ALSA_INCLUDE_DIRS})
    endif()
    target_link_libraries(IntuitivesDAW PRIVATE m pthread dl)
elseif(PLATFORM_WINDOWS)
    target_link_libraries(IntuitivesDAW PRIVATE ole32 winmm ws2_32)
endif()

# ============================================================================
# DEAR IMGUI GUI (optional - for visual version)
# ============================================================================

if(INTUITIVES_DAW_BUILD_GUI)
    find_package(OpenGL REQUIRED)
    find_package(glfw3 QUIET)
    
    set(IMGUI_DIR ${CMAKE_SOURCE_DIR}/third_party/imgui)
    if(EXISTS ${IMGUI_DIR})
        # Add ImGui sources
        target_sources(IntuitivesDAW PRIVATE
            ${IMGUI_DIR}/imgui.cpp
            ${IMGUI_DIR}/imgui_draw.cpp
            ${IMGUI_DIR}/imgui_tables.cpp
            ${IMGUI_DIR}/imgui_widgets.cpp
            ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
            ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
            # Our GUI implementation
            ${CMAKE_SOURCE_DIR}/src/gui/intuitives_gui.cpp
            ${CMAKE_SOURCE_DIR}/src/gui/sequencer.cpp
            ${CMAKE_SOURCE_DIR}/src/gui/synth_rack.cpp
            ${CMAKE_SOURCE_DIR}/src/gui/settings.cpp
            ${CMAKE_SOURCE_DIR}/src/gui/visualizer_3d.cpp
        )
        target_include_directories(IntuitivesDAW PRIVATE 
            ${IMGUI_DIR} 
            ${IMGUI_DIR}/backends
            ${CMAKE_SOURCE_DIR}/include/gui
        )
        target_compile_definitions(IntuitivesDAW PRIVATE INTUITIVES_DAW_GUI=1)
        message(STATUS "Dear ImGui GUI enabled")
    else()
        message(WARNING "Dear ImGui not found at ${IMGUI_DIR}")
        message(STATUS "To enable GUI, clone imgui to third_party/imgui:")
        message(STATUS "  git clone https://github.com/ocornut/imgui.git third_party/imgui")
    endif()
    
    target_link_libraries(IntuitivesDAW PRIVATE OpenGL::GL)
    if(glfw3_FOUND)
        target_link_libraries(IntuitivesDAW PRIVATE glfw)
    else()
        message(WARNING "GLFW not found - GUI may not link correctly")
        message(STATUS "Install GLFW: brew install glfw")
    endif()
endif()

# Output settings
set_target_properties(IntuitivesDAW PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# ============================================================================
# INTUITIVES CLI (optional - standalone engine)
# ============================================================================

if(INTUITIVES_DAW_USE_ENGINE)
    add_executable(intuitives-engine 
        ${ENGINE_DIR}/cli/main.c
    )
    target_link_libraries(intuitives-engine PRIVATE intuitives_engine)
    target_include_directories(intuitives-engine PRIVATE 
        ${ENGINE_DIR}/include
        ${ENGINE_DIR}/libcds/include
    )
    set_target_properties(intuitives-engine PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    )
endif()

# ============================================================================
# Installation
# ============================================================================

install(TARGETS IntuitivesDAW
    RUNTIME DESTINATION bin
)

if(INTUITIVES_DAW_USE_ENGINE)
    install(TARGETS intuitives-engine
        RUNTIME DESTINATION bin
    )
endif()

# ============================================================================
# Print configuration
# ============================================================================

message(STATUS "")
message(STATUS "╔════════════════════════════════════════════════╗")
message(STATUS "║       INTUITIVES DAW v${PROJECT_VERSION}-BETA          ║")
message(STATUS "║   'Does this sound cool?' - The only rule.     ║")
message(STATUS "╠════════════════════════════════════════════════╣")
message(STATUS "║ Platform: ${CMAKE_SYSTEM_NAME} (${CMAKE_OSX_ARCHITECTURES})")
message(STATUS "║ Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "║ GUI: ${INTUITIVES_DAW_BUILD_GUI}")
message(STATUS "║ Core Engine: ${INTUITIVES_DAW_USE_ENGINE}")
message(STATUS "║ DSP Features: 40 Original")
message(STATUS "║ Generators: Markov, Genetic, Cellular, L-System")
message(STATUS "║ Input: Text, Color, Image, MIDI")
message(STATUS "╚════════════════════════════════════════════════╝")
message(STATUS "")

# ============================================================================
# macOS App Bundle (optional)
# ============================================================================

if(APPLE)
    option(INTUITIVES_BUILD_BUNDLE "Build macOS .app bundle" ON)
    
    if(INTUITIVES_BUILD_BUNDLE)
        # Check for icns icon
        set(MACOSX_BUNDLE_ICON_FILE "")
        if(EXISTS ${CMAKE_SOURCE_DIR}/assets/AppIcon.icns)
            set(MACOSX_BUNDLE_ICON_FILE "AppIcon.icns")
            set(APP_ICON_FILE ${CMAKE_SOURCE_DIR}/assets/AppIcon.icns)
            set_source_files_properties(${APP_ICON_FILE} PROPERTIES
                MACOSX_PACKAGE_LOCATION "Resources"
            )
        endif()
        
        set_target_properties(IntuitivesDAW PROPERTIES
            MACOSX_BUNDLE TRUE
            MACOSX_BUNDLE_BUNDLE_NAME "Intuitives"
            MACOSX_BUNDLE_BUNDLE_VERSION "${PROJECT_VERSION}"
            MACOSX_BUNDLE_SHORT_VERSION_STRING "${PROJECT_VERSION}"
            MACOSX_BUNDLE_GUI_IDENTIFIER "dev.intuitives.daw"
            MACOSX_BUNDLE_COPYRIGHT "© 2024 Intuitives Team"
            MACOSX_BUNDLE_INFO_STRING "Rule-free Experimental DAW"
            MACOSX_BUNDLE_ICON_FILE "${MACOSX_BUNDLE_ICON_FILE}"
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
        )
        
        # Add icon as a source
        if(APP_ICON_FILE)
            target_sources(IntuitivesDAW PRIVATE ${APP_ICON_FILE})
        endif()
        
        # Copy other assets
        set(RESOURCE_FILES
            ${CMAKE_SOURCE_DIR}/assets/icon.svg
            ${CMAKE_SOURCE_DIR}/assets/logo.svg
        )
        
        foreach(RESOURCE ${RESOURCE_FILES})
            if(EXISTS ${RESOURCE})
                set_source_files_properties(${RESOURCE} PROPERTIES
                    MACOSX_PACKAGE_LOCATION "Resources"
                )
                target_sources(IntuitivesDAW PRIVATE ${RESOURCE})
            endif()
        endforeach()
        
        message(STATUS "Building macOS app bundle: Intuitives.app")
        message(STATUS "App Icon: ${MACOSX_BUNDLE_ICON_FILE}")
    endif()
endif()
