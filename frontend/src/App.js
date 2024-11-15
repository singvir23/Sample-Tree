import React, { useState } from 'react';
import TreeDiagram from './TreeDiagram';
import './App.css';

function App() {
  const [songData, setSongData] = useState(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchSongData = async (title) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/song/${encodeURIComponent(title)}`);
      const contentType = response.headers.get("content-type");
      
      if (!contentType?.includes("application/json")) {
        throw new Error("Received non-JSON response from server");
      }

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `Error: ${response.status}`);
      }
      
      setSongData(data);
    } catch (error) {
      console.error("Error fetching song data:", error);
      setError(error.message);
      setSongData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (title.trim()) {
      fetchSongData(title);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sample Tree Visualization</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter song title"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !title.trim()}>
            {loading ? 'Loading...' : 'Fetch Song'}
          </button>
        </form>
        
        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}
        
        {loading && <div>Loading...</div>}
        {songData && <TreeDiagram data={songData} />}
      </header>
    </div>
  );
}

export default App;