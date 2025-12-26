#!/bin/bash

# ============================================================
# INTUITIVES DAW v0.6 BETA - Build Script
# "Does this sound cool?" - The only rule.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo -e "${PURPLE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║       INTUITIVES DAW v0.6 BETA Builder         ║${NC}"
echo -e "${PURPLE}║   'Does this sound cool?' - The only rule.     ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
BUILD_TYPE="Release"
USE_STARGATE="OFF"
BUILD_GUI="OFF"

while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            BUILD_TYPE="Debug"
            shift
            ;;
        --stargate)
            USE_STARGATE="ON"
            shift
            ;;
        --gui)
            BUILD_GUI="ON"
            shift
            ;;
        --clean)
            echo -e "${CYAN}Cleaning build directory...${NC}"
            rm -rf build
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --debug      Build with debug symbols"
            echo "  --stargate   Include Stargate engine"
            echo "  --gui        Build with Dear ImGui GUI"
            echo "  --clean      Clean before building"
            echo "  --help       Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create build directory
mkdir -p build
cd build

# Configure
echo -e "${CYAN}Configuring CMake...${NC}"
cmake .. \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DINTUITIVES_DAW_USE_STARGATE=${USE_STARGATE} \
    -DINTUITIVES_DAW_BUILD_GUI=${BUILD_GUI}

# Build
echo ""
echo -e "${CYAN}Building...${NC}"
make -j$(sysctl -n hw.ncpu)

# Success
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           BUILD SUCCESSFUL! 🎉                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "App bundle: ${PURPLE}build/IntuitivesDAW.app${NC}"
echo ""

# App info
echo -e "${CYAN}App Info:${NC}"
echo "  Version: 0.6.0-beta"
echo "  Architecture: x86_64 (Intel)"
echo "  Platform: macOS 10.15+"
echo ""

# Run option
echo -e "To run the app:"
echo -e "  ${CYAN}open build/IntuitivesDAW.app${NC}"
echo "  or"
echo -e "  ${CYAN}./build/IntuitivesDAW.app/Contents/MacOS/IntuitivesDAW${NC}"
echo ""

# Python GUI option
echo -e "To run Python GUI with AI tools:"
echo -e "  ${CYAN}pip install -r requirements.txt${NC}"
echo -e "  ${CYAN}python intuitives.py${NC}"
echo ""
