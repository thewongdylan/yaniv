import { useState, useRef } from 'react'

export default function useGameSocket() {
  const [gameState, setGameState] = useState(null)
  const [socketError, setSocketError] = useState('')
  const [serverMessage, setServerMessage] = useState('')
  const [username, setUsername] = useState(null)
  const socketRef = useRef(null)
  const socketBase = (import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000').replace(/\/$/, '')

  const connect = (roomCode, nextUsername) => {
    setUsername(nextUsername)

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.close()
    }

    const ws = new WebSocket(
      `${socketBase}/ws/${encodeURIComponent(roomCode)}?username=${encodeURIComponent(nextUsername)}`
    )
    
    ws.onopen = () => {
      console.log('Connected to server')
      setSocketError('')
      setServerMessage('')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.error) {
        setServerMessage(data.error)
        return
      }

      setGameState(data)
      setServerMessage('')
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setSocketError('Connection failed. Is the Python backend running?')
    }

    ws.onclose = () => {
      console.log('Disconnected from server')
    }

    socketRef.current = ws
  }

  const sendAction = (payload) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload))
    } else {
      setServerMessage('Socket is not connected')
    }
  }

  const selectCard = (cardId) => {
    sendAction({ action: 'SELECT', cardId })
  }

  const deselectCard = (cardId) => {
    sendAction({ action: 'DESELECT', cardId })
  }
  
  const exchangeCards = (fromPile, discardCardId) => {
    sendAction({ action: 'EXCHANGE' , fromPile, discardCardId })
  }

  const callYaniv = () => {
    sendAction({ action: 'YANIV' })
  }

  return {
    gameState,
    socketError,
    serverMessage,
    username,
    connect,
    selectCard,
    deselectCard,
    exchangeCards,
    callYaniv,
  }
}