import React from 'react'
import './Card.css'

function Card({ id, suit, value, onClick, disabled = false, selected = false }) {
  const image = suit === 'Joker' ? `/cards/${id}.png` : `/cards/${suit}_${value}.png`

  return (
    <button
      type="button"
      className="playing-card"
      onClick={onClick}
      disabled={disabled}
      aria-label={`${value} of ${suit}`}
      aria-pressed={selected}
    >
      <img src={image} alt="" draggable="false" />
    </button>
  )
}

export default Card