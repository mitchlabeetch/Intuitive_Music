cmake_minimum_required(VERSION 3.16)
project(Intuitives VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Options
option(INTUITIVES_BUILD_WASM "Build WebAssembly target" OFF)
option(INTUITIVES_BUILD_DEMO "Build demo applications" ON)
option(INTUITIVES_ENABLE_SIMD "Enable SIMD optimizations" ON)

# Compiler flags
if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    add_compile_options(-Wall -Wextra -O3 -ffast-math)
    
    if(INTUITIVES_ENABLE_SIMD AND NOT INTUITIVES_BUILD_WASM)
        # Detect platform for SIMD
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm|ARM|aarch64|AARCH64")
            add_compile_options(-march=armv8-a+simd)
        else()
            add_compile_options(-mavx2 -mfma)
        endif()
    endif()
endif()

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Source files
set(INTUITIVES_SOURCES
    src/core/engine.c
    src/dsp/oscillators.c
    src/dsp/effects.c
    src/generators/generators.c
    src/input/input.c
    src/visual/visual.c
)

# Static library
add_library(intuitives STATIC ${INTUITIVES_SOURCES})
target_include_directories(intuitives PUBLIC ${CMAKE_SOURCE_DIR}/include)

# Shared library
add_library(intuitives_shared SHARED ${INTUITIVES_SOURCES})
target_include_directories(intuitives_shared PUBLIC ${CMAKE_SOURCE_DIR}/include)
set_target_properties(intuitives_shared PROPERTIES OUTPUT_NAME intuitives)

# Platform-specific linking
if(APPLE)
    target_link_libraries(intuitives PRIVATE "-framework Accelerate")
    target_link_libraries(intuitives_shared PRIVATE "-framework Accelerate")
elseif(UNIX)
    target_link_libraries(intuitives PRIVATE m pthread)
    target_link_libraries(intuitives_shared PRIVATE m pthread)
endif()

# WebAssembly build (requires Emscripten)
if(INTUITIVES_BUILD_WASM)
    set(WASM_SOURCES
        ${INTUITIVES_SOURCES}
        src/wasm/bindings.c
    )
    
    add_executable(intuitives_wasm ${WASM_SOURCES})
    target_include_directories(intuitives_wasm PRIVATE ${CMAKE_SOURCE_DIR}/include)
    target_compile_options(intuitives_wasm PRIVATE -O3 -fno-exceptions)
    
    # Emscripten link flags
    set(WASM_EXPORTS
        "_wasm_init"
        "_wasm_free"
        "_wasm_process"
        "_wasm_get_output_l"
        "_wasm_get_output_r"
        "_wasm_note_on"
        "_wasm_note_off"
        "_wasm_set_waveform"
        "_wasm_set_morph"
        "_wasm_set_filter"
        "_wasm_set_envelope"
        "_wasm_osc_init"
        "_wasm_osc_set_freq"
        "_wasm_osc_set_type"
        "_wasm_osc_process"
        "_wasm_reverb_init"
        "_wasm_reverb_set"
        "_wasm_reverb_process"
        "_wasm_markov_init"
        "_wasm_markov_set_temperature"
        "_wasm_markov_next"
        "_wasm_text_melody_init"
        "_wasm_text_melody_next"
        "_wasm_color_to_harmony"
        "_wasm_color_get_root"
        "_wasm_color_get_chord_note"
        "_wasm_color_get_chord_size"
        "_wasm_get_spectrum"
        "_wasm_get_level_l"
        "_wasm_get_level_r"
        "_wasm_note_to_color"
        "_wasm_version"
        "_wasm_feature_count"
    )
    string(REPLACE ";" "," WASM_EXPORTS_STR "${WASM_EXPORTS}")
    
    set_target_properties(intuitives_wasm PROPERTIES
        SUFFIX ".js"
        LINK_FLAGS "-s WASM=1 \
                    -s MODULARIZE=1 \
                    -s EXPORT_NAME='IntuitivesModule' \
                    -s EXPORTED_FUNCTIONS='[${WASM_EXPORTS_STR}]' \
                    -s EXPORTED_RUNTIME_METHODS='[\"ccall\",\"cwrap\",\"UTF8ToString\",\"allocateUTF8\"]' \
                    -s ALLOW_MEMORY_GROWTH=1 \
                    -s INITIAL_MEMORY=16777216 \
                    -s STACK_SIZE=1048576 \
                    -O3"
    )
    
    # Copy JS wrapper files to build directory
    add_custom_command(TARGET intuitives_wasm POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${CMAKE_SOURCE_DIR}/wasm/intuitives.js
            ${CMAKE_BINARY_DIR}/intuitives-wrapper.js
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${CMAKE_SOURCE_DIR}/wasm/react-hooks.js
            ${CMAKE_BINARY_DIR}/react-hooks.js
    )
endif()

# Demo applications
if(INTUITIVES_BUILD_DEMO)
    add_executable(intuitives_demo demo/main.c)
    target_link_libraries(intuitives_demo PRIVATE intuitives)
    
    if(UNIX AND NOT APPLE)
        target_link_libraries(intuitives_demo PRIVATE m pthread)
    endif()
endif()

# ============================================================================
# STANDALONE NATIVE APPLICATION
# ============================================================================
option(INTUITIVES_BUILD_APP "Build standalone application" ON)

if(INTUITIVES_BUILD_APP)
    add_executable(intuitives_app app/standalone.c)
    target_include_directories(intuitives_app PRIVATE ${CMAKE_SOURCE_DIR}/include)
    target_link_libraries(intuitives_app PRIVATE intuitives)
    
    # Platform-specific audio libraries
    if(APPLE)
        target_link_libraries(intuitives_app PRIVATE 
            "-framework CoreAudio"
            "-framework AudioToolbox"
            "-framework CoreFoundation"
        )
    elseif(UNIX)
        # Try to find ALSA or PulseAudio
        find_package(ALSA QUIET)
        if(ALSA_FOUND)
            target_link_libraries(intuitives_app PRIVATE ${ALSA_LIBRARIES})
            target_include_directories(intuitives_app PRIVATE ${ALSA_INCLUDE_DIRS})
        endif()
        target_link_libraries(intuitives_app PRIVATE m pthread dl)
    elseif(WIN32)
        target_link_libraries(intuitives_app PRIVATE ole32 winmm)
    endif()
    
    set_target_properties(intuitives_app PROPERTIES
        OUTPUT_NAME "Intuitives"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    )
endif()

# Install
install(TARGETS intuitives intuitives_shared
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/ DESTINATION include)

# Package config
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/IntuitivesConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Print configuration
message(STATUS "")
message(STATUS "=== INTUITIVES Audio Engine Configuration ===")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "Platform: ${CMAKE_SYSTEM_NAME}")
message(STATUS "Compiler: ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "SIMD: ${INTUITIVES_ENABLE_SIMD}")
message(STATUS "WASM: ${INTUITIVES_BUILD_WASM}")
message(STATUS "Demo: ${INTUITIVES_BUILD_DEMO}")
message(STATUS "============================================")
message(STATUS "")
