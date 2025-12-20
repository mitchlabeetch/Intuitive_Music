# Architecture Overview

## System Design

The Intuitive Music DAW follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │   UI       │  │ Transport  │  │  Track Management      │ │
│  │ Components │  │  Controls  │  │  & Visualization       │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ WebSocket / REST API
┌──────────────────────────▼──────────────────────────────────┐
│                   API Server (Flask)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │  REST      │  │ WebSocket  │  │  Route Handlers        │ │
│  │ Endpoints  │  │   Events   │  │  & Middleware          │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Core Engine Layer                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │   Audio    │  │  Project   │  │      Track             │ │
│  │   Engine   │  │  Manager   │  │    Management          │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────┬───────────┴──────────┬─────────────────────┐
│              │                      │                     │
▼              ▼                      ▼                     ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│  Audio   │  │   MIDI   │  │    AI    │  │   Database   │
│Processing│  │Processing│  │Assistant │  │   Storage    │
└──────────┘  └──────────┘  └──────────┘  └──────────────┘
```

## Components

### 1. Frontend Layer
- **Technology**: React with modern hooks
- **Communication**: REST API + WebSocket
- **Responsibilities**:
  - User interface rendering
  - User input handling
  - Real-time state updates
  - Visualization (waveforms, meters)

### 2. API Server
- **Technology**: Flask + Flask-SocketIO
- **Responsibilities**:
  - HTTP request handling
  - WebSocket event management
  - API endpoint routing
  - Session management
  - CORS handling

### 3. Core Engine
- **Audio Engine**: Real-time audio processing
  - Buffer management
  - Track mixing
  - Effect processing
  - Playback control
  
- **Project Manager**: Project lifecycle
  - Create/save/load projects
  - Metadata management
  - File organization
  
- **Track Manager**: Multi-track handling
  - Track creation/deletion
  - Volume/pan control
  - Solo/mute functionality
  - Automation

### 4. Processing Modules

#### Audio Processing
- Audio effects (EQ, Compression, Reverb, Delay)
- Audio analysis (RMS, Peak, LUFS)
- Tempo detection
- Audio clip management

#### MIDI Processing
- MIDI event handling
- Note manipulation
- Chord generation
- Arpeggiator
- Quantization
- Humanization

#### AI Assistant
- OpenAI/Anthropic integration
- Music theory assistance
- Chord progression suggestions
- Melody generation
- Mixing/mastering advice
- Interactive chat

### 5. Data Layer
- **Database**: SQLAlchemy ORM with SQLite
- **Models**: Projects, Tracks, Sessions, Presets
- **File Storage**: Audio files, project data, renders

## Data Flow

### Playback Flow
```
User clicks Play
    → Frontend sends POST /api/transport/play
        → API Server updates engine state
            → Audio Engine starts processing
                → Mix tracks → Apply effects → Output buffer
                    → WebSocket broadcasts state update
                        → Frontend updates UI
```

### Project Save Flow
```
User clicks Save
    → Frontend sends POST /api/project/save
        → API Server calls Project.save()
            → Serialize project data
                → Write JSON to disk
                    → Update database record
                        → Return success/failure
```

### AI Assistance Flow
```
User requests chord suggestions
    → Frontend sends POST /api/ai/suggest-chords
        → API Server calls AIAssistant.suggest_chords()
            → Build prompt with context
                → Call AI provider (OpenAI/Anthropic)
                    → Parse response
                        → Return suggestions to frontend
```

## Threading Model

- **Main Thread**: Flask server and API handling
- **Audio Thread**: Real-time audio processing (when implemented)
- **Background Tasks**: Rendering, file I/O (Celery optional)

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **Input Validation**: All user inputs sanitized
3. **File Access**: Restricted to project directories
4. **CORS**: Configured for trusted origins
5. **Rate Limiting**: Consider implementing for AI endpoints

## Scalability

### Current Design
- Single-process architecture
- Local file storage
- SQLite database

### Future Enhancements
- Multi-process audio rendering
- Distributed processing with Celery
- Cloud storage integration
- PostgreSQL for production
- Redis for caching and session management

## Extension Points

1. **Plugin System**: Load custom audio/MIDI processors
2. **AI Providers**: Support multiple AI backends
3. **Export Formats**: Add new audio formats
4. **Database Backends**: Switch to different databases
5. **Audio Devices**: Support various audio I/O configurations
