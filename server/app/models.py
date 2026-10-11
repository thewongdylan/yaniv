from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Card(BaseModel):
    id: str
    suit: str
    value: str

class Player(BaseModel):
    username: str
    hand_cards: list[Card] = Field(default_factory=list)
    selected_cards: list[Card] = Field(default_factory=list)
    score: int = 0
    has_called_yaniv: bool = False
    eliminated: bool = False

class OpponentState(BaseModel):
    username: str
    cardCount: int

class GameState(BaseModel):
    roomCode: str
    players: Dict[str, Player] = Field(default_factory=dict)
    deck: List[Card] = Field(default_factory=list)
    discardPile: List[Card] = Field(default_factory=list)
    previousDiscard: List[Card] = Field(default_factory=list)
    currentTurn: int = 0
    winner: Optional[str] = None
    gameOver: bool = False
    roundOver: bool = False
    roundNumber: int = 1
    yanivThreshold: int = 7
    losingScore: int = 200