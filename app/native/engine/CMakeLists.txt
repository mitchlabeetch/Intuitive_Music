cmake_minimum_required(VERSION 3.10)
project(IntuitivesEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Packages
find_package(PkgConfig REQUIRED)
pkg_check_modules(SNDFILE REQUIRED sndfile)
pkg_check_modules(PORTAUDIO REQUIRED portaudio-2.0)

# Include Directories
include_directories(
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/integrations
    ${SNDFILE_INCLUDE_DIRS}
    ${PORTAUDIO_INCLUDE_DIRS}
)

# Source Files
set(SOURCES
    daw.cpp
    UniversalHost.cpp
)

# Shared Library (for Python ctypes)
add_library(intuitives_engine SHARED ${SOURCES})

# Link Libraries
target_link_libraries(intuitives_engine
    ${SNDFILE_LIBRARIES}
    ${PORTAUDIO_LIBRARIES}
    pthread
)

# Install (optional, but good for structure)
install(TARGETS intuitives_engine DESTINATION lib)
