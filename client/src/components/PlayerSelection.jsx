import React from 'react'
import Card from './Card'
import { sortCards } from '../utils/cardUtils'

function PlayerSelection({ cards, onCardClick }) {
  const sortedCards = sortCards(cards)
  return (
    <div style={{ display: "flex", flexDirection: "row", justifyContent: "center", gap: "10px" }}>
      {sortedCards.map((cardData) => (
         <Card 
           key={cardData.id}
           id={cardData.id}
           suit={cardData.suit} 
           value={cardData.value} 
           onClick={() => onCardClick(cardData.id)}
         />
      ))}
    </div>
  )
}

export default PlayerSelection