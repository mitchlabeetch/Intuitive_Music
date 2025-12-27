/**
 * Main DAW Application Component
 */
import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

function App() {
  const [connected, setConnected] = useState(false);
  const [socket, setSocket] = useState(null);
  const [project, setProject] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [playing, setPlaying] = useState(false);
  const [recording, setRecording] = useState(false);
  // Integration State
  const [plugins, setPlugins] = useState([]);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io(API_URL);
    
    newSocket.on('connect', () => {
      console.log('Connected to DAW server');
      setConnected(true);
    });
    
    newSocket.on('disconnect', () => {
      console.log('Disconnected from DAW server');
      setConnected(false);
    });
    
    newSocket.on('transport_state', (data) => {
      setPlaying(data.playing);
      setRecording(data.recording);
    });
    
    setSocket(newSocket);
    
    return () => newSocket.close();
  }, []);

  const createProject = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/project`, {
        name: 'New Project'
      });
      
      if (response.data.success) {
        setProject(response.data.project);
        loadTracks();
      }
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const loadTracks = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/tracks`);
      setTracks(response.data);
    } catch (error) {
      console.error('Failed to load tracks:', error);
    }
  };

  const addTrack = async (type = 'audio') => {
    try {
      const response = await axios.post(`${API_URL}/api/tracks`, {
        type,
        name: `${type} Track ${tracks.length + 1}`
      });
      
      if (response.data.success) {
        loadTracks();
      }
    } catch (error) {
      console.error('Failed to add track:', error);
    }
  };

  const togglePlayback = async () => {
    try {
      const endpoint = playing ? 'stop' : 'play';
      await axios.post(`${API_URL}/api/transport/${endpoint}`);
      setPlaying(!playing);
    } catch (error) {
      console.error('Failed to toggle playback:', error);
    }
  };

  const toggleRecord = async () => {
    try {
      await axios.post(`${API_URL}/api/transport/record`);
      setRecording(!recording);
    } catch (error) {
      console.error('Failed to toggle recording:', error);
    }
  };

  const loadPlugin = async (type, path) => {
      try {
          await axios.post(`${API_URL}/api/plugins/load`, {
              type: type,
              path: path
          });
          setPlugins([...plugins, {type, path}]);
          alert(`Loaded ${type} plugin!`);
      } catch (error) {
          console.error("Failed to load plugin:", error);
      }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🎵 Intuitives DAW</h1>
        <div className="connection-status">
          <span className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}></span>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="toolbar">
        <button onClick={createProject} disabled={!!project}>
          New Project
        </button>
        <button onClick={() => addTrack('audio')} disabled={!project}>
          Add Audio Track
        </button>
        <button onClick={() => addTrack('midi')} disabled={!project}>
          Add MIDI Track
        </button>
        <div className="plugin-loader">
            <button onClick={() => loadPlugin('CLAP', '/path/to/plugin.clap')} disabled={!project}>Load CLAP</button>
            <button onClick={() => loadPlugin('FAUST', 'process = osc(440);')} disabled={!project}>Load Faust Code</button>
        </div>
      </div>

      <div className="transport">
        <button 
          className={`transport-btn ${playing ? 'active' : ''}`}
          onClick={togglePlayback}
          disabled={!project}
        >
          {playing ? '⏸ Pause' : '▶ Play'}
        </button>
        <button 
          className={`transport-btn ${recording ? 'active' : ''}`}
          onClick={toggleRecord}
          disabled={!project}
        >
          ⏺ Record
        </button>
      </div>

      <div className="main-content">
        <div className="track-list">
          {tracks.length === 0 ? (
            <div className="empty-state">
              <p>No tracks yet. Create a project and add some tracks!</p>
            </div>
          ) : (
            tracks.map((track, index) => (
              <div key={index} className="track">
                <div className="track-header">
                  <span className="track-name">{track.name}</span>
                  <span className="track-type">{track.type}</span>
                </div>
                <div className="track-controls">
                  <button className={track.muted ? 'muted' : ''}>M</button>
                  <button className={track.solo ? 'solo' : ''}>S</button>
                </div>
              </div>
            ))
          )}
        </div>
        <div className="plugin-rack">
            <h3>Loaded Plugins (Engine Side)</h3>
            <ul>
                {plugins.map((p, i) => <li key={i}>{p.type}: {p.path}</li>)}
            </ul>
        </div>
      </div>

      <footer className="footer">
        <div className="status-bar">
          {project ? `Project: ${project.name}` : 'No project loaded'}
        </div>
      </footer>
    </div>
  );
}

export default App;
