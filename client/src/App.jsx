import React from 'react'
import Lobby from './components/Lobby'
import GameTable from './components/GameTable'
import useGameSocket from './hooks/useGameSocket'

function App() {
  const { 
    gameState, 
    socketError, 
    serverMessage, 
    username, 
    connect, 
    selectCard, 
    deselectCard,
    exchangeCards, 
    callYaniv } = useGameSocket()

  // If there is no active game state from the server, show the Lobby
  if (gameState === null) {
    return <Lobby onJoin={connect} socketError={socketError} />
  }

  // Otherwise, show the game board
  return (
    <GameTable 
      gameState={gameState} 
      username={username}
      serverMessage={serverMessage}
      onSelect={selectCard}
      onDeselect={deselectCard}
      onExchange={exchangeCards}
      onCallYaniv={callYaniv}
    />
  )
}

export default App