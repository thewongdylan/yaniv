import asyncio
import re

from typing import Dict, Any
from fastapi import WebSocket
from app.models import GameState
from app.game.engine import create_new_game, add_player_to_game, get_legal_discard_indices, start_next_round, get_player_order

MAX_PLAYERS = 4
ROOM_CODE_PATTERN = re.compile(r"^[0-9]{4}$")  # 4 numbers
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,20}$")  # 1-20 alphanumeric

class RoomManager:
    def __init__(self):
        # Maps room codes to their active GameState
        self.games: Dict[str, GameState] = {}
        # Maps room codes to a list of active WebSocket connections
        self.connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_code: str, username: str | None) -> bool:
        room_code = room_code.strip()

        if not username:
            await websocket.accept()
            await websocket.close(code=1008, reason="Username is required.")
            return False

        username = username.strip()

        if not ROOM_CODE_PATTERN.fullmatch(room_code):
            await websocket.accept()
            await websocket.close(code=1008, reason="Invalid room code format.")
            return False

        if not USERNAME_PATTERN.fullmatch(username):
            await websocket.accept()
            await websocket.close(code=1008, reason="Invalid username format.")
            return False

        game = self.games.get(room_code)
        if game and username not in game.players:
            if len(game.players) >= MAX_PLAYERS:
                await websocket.accept()
                await websocket.close(code=1008, reason="Room is full.")
                return False

        active_connections = self.connections.get(room_code, [])
        if any(
            ws.query_params.get("username") == username
            for ws in active_connections
        ):
            await websocket.accept()
            await websocket.close(
                code=1008,
                reason="Username already connected in this room.",
            )
            return False

        await websocket.accept()

        if game is None:
            game = create_new_game(room_code)
            self.games[room_code] = game
            self.connections[room_code] = []

        add_player_to_game(game, username)
        self.connections[room_code].append(websocket)
        await self.broadcast_game_state(room_code)
        return True

    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.connections:
            if websocket in self.connections[room_code]:
                self.connections[room_code].remove(websocket)

        if room_code in self.connections and len(self.connections[room_code]) == 0:
            self.connections.pop(room_code, None)
            self.games.pop(room_code, None)

    async def finish_round(self, room_code: str) -> None:
        await asyncio.sleep(2)
        game = self.games.get(room_code)
        if game is None or not game.roundOver or game.gameOver:
            return
        start_next_round(game)
        await self.broadcast_game_state(room_code)

    def client_state_for(self, game: GameState, username: str) -> Dict[str, Any]:
        player = game.players.get(username)
        player_order = get_player_order(game)
        current_player = player_order[game.currentTurn % len(player_order)] if player_order else None
        legal_indices = get_legal_discard_indices(game.previousDiscard)

        return {
            "roomCode": game.roomCode,
            "handCards": [card.model_dump() for card in player.hand_cards],
            "selectedCards": [card.model_dump() for card in player.selected_cards],
            "opponents": [
                {
                    "username": opponent.username, 
                    "cardCount": len(opponent.hand_cards + opponent.selected_cards)
                }
                for opponent in game.players.values() if opponent.username != username
            ],
            "previousDiscard": [card.model_dump() for card in game.previousDiscard],
            "legalDiscardIds": [game.previousDiscard[index].id for index in legal_indices],
            "currentTurn": game.currentTurn,
            "currentPlayer": current_player,
            "winner": game.winner,
            "gameOver": game.gameOver,
            "roundOver": game.roundOver,
            "roundNumber": game.roundNumber,
            "scores": {p.username: p.score for p in game.players.values()},
        }

    async def broadcast_game_state(self, room_code: str):
        if room_code not in self.connections:
            return
            
        game = self.games[room_code]
        
        for ws in self.connections[room_code]:
            # Extract the username from the websocket query params
            username = ws.query_params.get("username")
            client_state = self.client_state_for(game, username)
            await ws.send_json(client_state)

# A global instance to hold data in memory while the server runs
manager = RoomManager()