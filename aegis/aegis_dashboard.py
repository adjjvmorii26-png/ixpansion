import asyncio
import json
import logging
import time
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

logger = logging.getLogger("service.dashboard")
app = FastAPI(title="MYAGENTSPACE Control Plane")

# Global WebSockets connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/")
async def get_dashboard():
    """Serves retro MYAGENTSPACE control page UI."""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>MYAGENTSPACE // AEGIS Control Hub</title>
    <style>
        body { background-color: #0d1117; color: #58a6ff; font-family: monospace; padding: 20px; }
        h1 { color: #2f81f7; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 15px; }
        .alert { color: #f85149; font-weight: bold; }
        .success { color: #3fb950; }
        #logs { height: 300px; overflow-y: scroll; background: #010409; padding: 10px; border: 1px solid #30363d; }
    </style>
</head>
<body>
    <h1>MYAGENTSPACE // AEGIS Control Hub</h1>
    <div class="card">
        <h2>System Status</h2>
        <p>Agent mesh operational</p>
    </div>
    <div id="logs"></div>
</body>
</html>
""")
