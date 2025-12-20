# API Documentation

## REST API Endpoints

### Health Check
```
GET /health
```
Returns server status and version.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### Project Management

#### Create Project
```
POST /api/project
```

**Request Body:**
```json
{
  "name": "My New Project"
}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "name": "My New Project",
    "path": "./projects/My New Project"
  }
}
```

#### Load Project
```
GET /api/project/<project_path>
```

**Response:**
```json
{
  "success": true,
  "project": {
    "name": "My Project",
    "tempo": 120.0,
    "tracks": 5
  }
}
```

#### Save Project
```
POST /api/project/save
```

**Response:**
```json
{
  "success": true,
  "path": "./projects/My Project"
}
```

### Track Management

#### Get All Tracks
```
GET /api/tracks
```

**Response:**
```json
[
  {
    "index": 0,
    "name": "Track 1",
    "type": "audio",
    "muted": false,
    "volume": 0.0,
    "pan": 0.0
  }
]
```

#### Add Track
```
POST /api/tracks
```

**Request Body:**
```json
{
  "type": "audio",
  "name": "New Track"
}
```

**Response:**
```json
{
  "success": true,
  "track": {
    "index": 1,
    "name": "New Track",
    "type": "audio"
  }
}
```

### Transport Controls

#### Play
```
POST /api/transport/play
```

**Response:**
```json
{
  "success": true,
  "playing": true
}
```

#### Stop
```
POST /api/transport/stop
```

**Response:**
```json
{
  "success": true,
  "playing": false
}
```

#### Record
```
POST /api/transport/record
```

**Response:**
```json
{
  "success": true,
  "recording": true
}
```

### AI Assistant

#### Suggest Chords
```
POST /api/ai/suggest-chords
```

**Request Body:**
```json
{
  "key": "C major",
  "style": "pop"
}
```

**Response:**
```json
{
  "success": true,
  "content": "For a pop song in C major, I'd suggest: C - Am - F - G...",
  "error": null
}
```

#### AI Chat
```
POST /api/ai/chat
```

**Request Body:**
```json
{
  "message": "How do I mix vocals?"
}
```

**Response:**
```json
{
  "success": true,
  "content": "Here are some tips for mixing vocals...",
  "error": null
}
```

## WebSocket Events

### Client -> Server

#### Transport Update
```javascript
socket.emit('transport_update', {
  action: 'play' | 'stop' | 'record'
});
```

### Server -> Client

#### Status
```javascript
socket.on('status', (data) => {
  // data: { message: "Connected to DAW server" }
});
```

#### Transport State
```javascript
socket.on('transport_state', (data) => {
  // data: {
  //   playing: true,
  //   recording: false,
  //   position: 12000
  // }
});
```
