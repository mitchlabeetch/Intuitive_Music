# Instructions - Intuitives

## Development Setup
1. Initialize project: `npm create vite@latest` (React + TS).
2. Install audio core: `npm install tone`.
3. Set up the 3D environment: `npm install three @react-three/fiber`.

## Coding Standards
- **Performance:** Audio processing must never block the main thread. Use `AudioWorklet` for custom DSP.
- **Modularity:** Every "Module" (Synth, Effect, Generator) should be an independent component that can be connected to others.
- **Accessibility:** Ensure the UI (despite being experimental) is navigable via keyboard.

## Session Workflow
- **Before:** Check `to_do.md`.
- **After:** Update `features.md`.
