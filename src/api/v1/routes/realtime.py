from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.schemas.websockets import BanHammered
import json

router = APIRouter(prefix="/realtime", tags=["realtime"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: dict):
        message = json.dumps(event)
        dead_connections: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                dead_connections.append(connection)
            except RuntimeError:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Keep the socket open and consume client messages when present.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/ban-sent")
async def trigger_sound(banHammered: BanHammered):
    await manager.broadcast(
        {
            "type": "ban",
            "reason": banHammered.reason,
            "banned_username": banHammered.banned_username,
            "actor_username": banHammered.actor_username,
        }
        )
    return {"ok": True, "receivers": len(manager.active_connections)}
