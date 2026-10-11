import React from 'react'
import Card from './Card'
import PlayerHand from './PlayerHand'
import PlayerSelection from './PlayerSelection'
import { calculateHandValue } from '../utils/cardUtils'

function GameTable({
  gameState,
  username,
  serverMessage,
  onSelect,
  onDeselect,
  onExchange,
  onCallYaniv,
}) {
  if (!gameState) return <div>Loading table...</div>

  const isMyTurn = gameState.currentPlayer === username &&
    !gameState.gameOver && !gameState.roundOver
  const handCards = gameState.handCards || []
  const selectedCards = gameState.selectedCards || []
  const totalHandValue = calculateHandValue([...handCards, ...selectedCards])
  const myScore = gameState.scores[username] ?? 0

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', textAlign: 'center' }}>
      <h2>Room Code: {gameState.roomCode} | Round: {gameState.roundNumber ?? 1} </h2>

      <div
        style={{
          marginBottom: '20px',
          padding: '12px',
          backgroundColor: '#f3f3f3',
          borderRadius: '8px',
        }}
      >
        <strong>Current turn:</strong> {gameState.currentPlayer || 'Waiting...'}
        <br />
        <strong>Your turn:</strong> {isMyTurn ? 'Yes' : 'No'}
      </div>

      {serverMessage && (
        <div
          style={{
            marginBottom: '20px',
            padding: '10px',
            backgroundColor: '#fff3cd',
            color: '#856404',
            borderRadius: '6px',
            fontWeight: 'bold',
          }}
        >
          {serverMessage}
        </div>
      )}

      {gameState.roundOver && !gameState.gameOver && (
        <div
          role="status"
          style={{
            marginBottom: '20px',
            padding: '10px',
            backgroundColor: '#d4edda',
            color: '#155724',
            borderRadius: '6px',
            fontWeight: 'bold',
          }}
        >
          Round {gameState.roundNumber} complete. The next round starts shortly.
        </div>
      )}

      {gameState.gameOver && (
        <div
          style={{
            marginBottom: '20px',
            padding: '10px',
            backgroundColor: '#d4edda',
            color: '#155724',
            borderRadius: '6px',
            fontWeight: 'bold',
          }}
        >
          Game over. Winner: {gameState.winner}
        </div>
      )}

      <div
        style={{
          marginBottom: '30px',
          padding: '15px',
          backgroundColor: '#f0f0f0',
          borderRadius: '8px',
        }}
      >
        <h3>Opponents</h3>

        {gameState.opponents && gameState.opponents.map((opp) => (
          <span key={opp.username} style = {{ margin: '0 15px' }}>
            <strong>{opp.username}:</strong> {opp.cardCount} cards
            {' | Score: '}
            {gameState.scores?.[opp.username] ?? 0 }
          </span>
        ))}
      </div>

      <div style={{ marginBottom: '40px' }}>
        <h3>The Table</h3>

        <button
          onClick={() => onExchange('deck')}
          disabled={!isMyTurn}
          style={{
            padding: '15px',
            marginRight: '10px',
            cursor: isMyTurn ? 'pointer' : 'not-allowed',
            opacity: isMyTurn ? 1 : 0.5,
          }}
        >
          <img src='/cards/Card_Back.png' alt='Deck' style={{ width: '60px', marginLeft: '10px' }} />
        </button>

        <div
          style={{
            display: 'inline-flex',
            flexDirection: 'row',
            gap: '10px',
            verticalAlign: 'top',
            padding: '15px',
            backgroundColor: '#f0f0f0',
            borderRadius: '8px',
          }}
        >
          {(gameState.previousDiscard || []).map((card) => {
            const isLegalDiscard = (
              gameState.legalDiscardIds || []
            ).includes(card.id)

            return (
              <Card
                key={card.id}
                id={card.id}
                suit={card.suit}
                value={card.value}
                disabled={!isMyTurn || !isLegalDiscard}
                onClick={() => onExchange('discard', card.id)}
              />
            )
          })}
        </div>
      </div>

      <div>
        <h3>Your Hand (Value: {totalHandValue} | Score: {myScore})</h3>
        
        <button
          onClick={onCallYaniv}
          disabled={!isMyTurn || gameState.gameOver}
          style={{
            padding: '15px',
            cursor: isMyTurn ? 'pointer' : 'not-allowed',
            opacity: isMyTurn ? 1 : 0.5,
            backgroundColor: '#e74c3c',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
          }}
        >
          Call Yaniv
        </button>

        <div style={{ backgroundColor: '#f0f0f0', padding: '10px', borderRadius: '6px' }}>
          <p>Selected Cards</p>
          <PlayerSelection
            cards={gameState.selectedCards || []}
            onCardClick={isMyTurn ? onDeselect : () => {}}
            />
        </div>

        <div style={{padding: '10px', borderRadius: '6px' }}>
          <p>Your Hand</p>
          <PlayerHand
            cards={gameState.handCards || []}
            onCardClick={isMyTurn ? onSelect : () => {}}
            />
        </div>
      </div>
    </div>
  )
}

export default GameTable