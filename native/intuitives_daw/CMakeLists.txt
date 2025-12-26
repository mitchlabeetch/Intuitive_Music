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
option(INTUITIVES_DAW_USE_STARGATE "Use Stargate engine" ON)

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
# STARGATE ENGINE (full DAW core)
# ============================================================================

if(INTUITIVES_DAW_USE_STARGATE)
    set(STARGATE_DIR ${CMAKE_SOURCE_DIR}/stargate_engine)
    include_directories(${STARGATE_DIR}/include)
    include_directories(${STARGATE_DIR}/libcds/include)
    
    # Find all Stargate source files
    file(GLOB_RECURSE STARGATE_SRC_FILES 
        "${STARGATE_DIR}/src/*.c"
    )
    file(GLOB_RECURSE STARGATE_LIBCDS_FILES
        "${STARGATE_DIR}/libcds/src/*.c"
    )
    
    # Exclude CLI main file (we have our own)
    list(FILTER STARGATE_SRC_FILES EXCLUDE REGEX "_main\\.c$")
    
    set(STARGATE_SOURCES
        ${STARGATE_SRC_FILES}
        ${STARGATE_LIBCDS_FILES}
    )
    
    # Build Stargate engine as a static library
    add_library(stargate_engine STATIC ${STARGATE_SOURCES})
    target_include_directories(stargate_engine PUBLIC 
        ${STARGATE_DIR}/include
        ${STARGATE_DIR}/libcds/include
    )
    target_compile_options(stargate_engine PRIVATE -O2 -ffast-math)
    
    # Link dependencies for Stargate
    if(PLATFORM_MACOS)
        find_library(COREAUDIO CoreAudio)
        find_library(AUDIOTOOLBOX AudioToolbox)
        find_library(COREFOUNDATION CoreFoundation)
        target_link_libraries(stargate_engine PUBLIC
            ${COREAUDIO}
            ${AUDIOTOOLBOX}
            ${COREFOUNDATION}
        )
    elseif(PLATFORM_LINUX)
        find_package(ALSA QUIET)
        if(ALSA_FOUND)
            target_link_libraries(stargate_engine PUBLIC ${ALSA_LIBRARIES})
            target_include_directories(stargate_engine PUBLIC ${ALSA_INCLUDE_DIRS})
        endif()
    endif()
    
    # Find PortAudio (Stargate's audio backend)
    find_library(PORTAUDIO_LIB portaudio HINTS /usr/local/lib /opt/homebrew/lib)
    find_path(PORTAUDIO_INCLUDE portaudio.h HINTS /usr/local/include /opt/homebrew/include)
    if(PORTAUDIO_LIB AND PORTAUDIO_INCLUDE)
        target_include_directories(stargate_engine PUBLIC ${PORTAUDIO_INCLUDE})
        target_link_libraries(stargate_engine PUBLIC ${PORTAUDIO_LIB})
        message(STATUS "Found PortAudio: ${PORTAUDIO_LIB}")
    endif()
    
    # Find PortMIDI
    find_library(PORTMIDI_LIB portmidi HINTS /usr/local/lib /opt/homebrew/lib)
    if(PORTMIDI_LIB)
        target_link_libraries(stargate_engine PUBLIC ${PORTMIDI_LIB})
        message(STATUS "Found PortMIDI: ${PORTMIDI_LIB}")
    endif()
    
    # Find libsndfile
    find_library(SNDFILE_LIB sndfile HINTS /usr/local/lib /opt/homebrew/lib)
    find_path(SNDFILE_INCLUDE sndfile.h HINTS /usr/local/include /opt/homebrew/include)
    if(SNDFILE_LIB AND SNDFILE_INCLUDE)
        target_include_directories(stargate_engine PUBLIC ${SNDFILE_INCLUDE})
        target_link_libraries(stargate_engine PUBLIC ${SNDFILE_LIB})
        message(STATUS "Found libsndfile: ${SNDFILE_LIB}")
    endif()
    
    # Find FFTW3
    find_library(FFTW3_LIB fftw3 HINTS /usr/local/lib /opt/homebrew/lib)
    find_library(FFTW3F_LIB fftw3f HINTS /usr/local/lib /opt/homebrew/lib)
    if(FFTW3_LIB)
        target_link_libraries(stargate_engine PUBLIC ${FFTW3_LIB})
    endif()
    if(FFTW3F_LIB)
        target_link_libraries(stargate_engine PUBLIC ${FFTW3F_LIB})
    endif()
    
    target_link_libraries(stargate_engine PUBLIC m pthread)
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

# Link Stargate engine if enabled
if(INTUITIVES_DAW_USE_STARGATE)
    target_link_libraries(IntuitivesDAW PRIVATE stargate_engine)
    target_compile_definitions(IntuitivesDAW PRIVATE USE_STARGATE_ENGINE=1)
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
        target_sources(IntuitivesDAW PRIVATE
            ${IMGUI_DIR}/imgui.cpp
            ${IMGUI_DIR}/imgui_draw.cpp
            ${IMGUI_DIR}/imgui_tables.cpp
            ${IMGUI_DIR}/imgui_widgets.cpp
            ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
            ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
        )
        target_include_directories(IntuitivesDAW PRIVATE ${IMGUI_DIR} ${IMGUI_DIR}/backends)
        target_compile_definitions(IntuitivesDAW PRIVATE INTUITIVES_DAW_GUI=1)
    endif()
    
    target_link_libraries(IntuitivesDAW PRIVATE OpenGL::GL)
    if(glfw3_FOUND)
        target_link_libraries(IntuitivesDAW PRIVATE glfw)
    endif()
endif()

# Output settings
set_target_properties(IntuitivesDAW PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# ============================================================================
# STARGATE CLI (optional - standalone engine)
# ============================================================================

if(INTUITIVES_DAW_USE_STARGATE)
    add_executable(stargate-engine 
        ${STARGATE_DIR}/cli/main.c
    )
    target_link_libraries(stargate-engine PRIVATE stargate_engine)
    target_include_directories(stargate-engine PRIVATE 
        ${STARGATE_DIR}/include
        ${STARGATE_DIR}/libcds/include
    )
    set_target_properties(stargate-engine PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    )
endif()

# ============================================================================
# Installation
# ============================================================================

install(TARGETS IntuitivesDAW
    RUNTIME DESTINATION bin
)

if(INTUITIVES_DAW_USE_STARGATE)
    install(TARGETS stargate-engine
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
message(STATUS "║ Stargate Engine: ${INTUITIVES_DAW_USE_STARGATE}")
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
