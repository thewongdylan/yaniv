import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.game.engine import process_player_action
from app.game.room_manager import manager

app = FastAPI()

# Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    username = websocket.query_params.get("username")

    if not await manager.connect(websocket, room_code, username):
        return

    try:
        while True:
            data = await websocket.receive_text()
            action_data = json.loads(data)

            game = manager.games.get(room_code)
            if game is None:
                continue

            result = process_player_action(game, username, action_data)

            if result["ok"]:
                await manager.broadcast_game_state(room_code)

                if action_data.get("action") == "YANIV":
                    game = manager.games.get(room_code)
                    if game and game.roundOver and not game.gameOver:
                        asyncio.create_task(manager.finish_round(room_code))
            else:
                await websocket.send_json({"error": result["message"]})

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)