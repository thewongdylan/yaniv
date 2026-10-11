import React, { useState } from 'react'

function Lobby({ onJoin, socketError }) {
  const [username, setUsername] = useState("")
  const [roomCode, setRoomCode] = useState("")

  const handleJoinClick = () => {
    // Only attempt connection if both fields are filled
    if (username && roomCode) {
      onJoin(roomCode, username)
    }
  }

  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h1>Welcome to Yaniv</h1>
      
      {socketError && (
        <p style={{ color: 'red', fontWeight: 'bold' }}>
          Connection failed. Is your Python backend running?
        </p>
      )}

      <div style={{ marginBottom: '10px' }}>
        <input 
          type="text"
          placeholder="Enter Username" 
          value={username}
          onChange={(e) => setUsername(e.target.value)} 
          style={{ padding: '8px', marginRight: '5px' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <input 
          type="text"
          placeholder="4-Letter Room Code" 
          value={roomCode}
          onChange={(e) => setRoomCode(e.target.value)} 
          style={{ padding: '8px', marginRight: '5px' }}
        />
      </div>

      <button onClick={handleJoinClick} style={{ padding: '10px 20px', cursor: 'pointer' }}>
        Join Game
      </button>
    </div>
  )
}

export default Lobby