# Variables & State - Intuitives

## Global State
- `isPlaying`: Boolean.
- `globalTempo`: Number (BPM).
- `chaosLevel`: Number (0-100).
- `inputSource`: Enum (`MOUSE`, `WEBCAM`, `MIDI`).

## Data Models
- **Track:** `{ id, type (SYNTH/AUDIO), sourceData (Image/File), modifiers: [] }`
- **Modifier:** `{ type (LFO/ENV), targetParam, intensity }`
- **Session:** `{ tracks: [], globalEffects: [], aiSettings: {} }`

## AI Context
- `currentHarmony`: The detected chord progression.
- `userVibe`: A vector representing the user's current "mood" (aggressive, chill) derived from their input speed and gesture data.
