from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.bus import metric_bus
from app.models.metrics import InverterMetrics

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws/live")
async def websocket_live_metrics(websocket: WebSocket):
    await manager.connect(websocket)
    queue = metric_bus.subscribe()
    try:
        while True:
            metrics: InverterMetrics = await queue.get()
            data = metrics.model_dump_json()
            await websocket.send_text(data)
    except (WebSocketDisconnect, ConnectionResetError):
        pass
    finally:
        metric_bus.unsubscribe(queue)
        manager.disconnect(websocket)
