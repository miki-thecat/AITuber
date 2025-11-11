import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

async def dummy_mouth_stream():
    import json
    import math
    while True:
        await asyncio.sleep(3)
        await manager.broadcast(json.dumps({"type": "utter_start", "text": "こんにちは！", "subtitle": "こんにちは！"}))
        for i in range(100):
            value = (math.sin(i * 0.2) + 1) / 2
            await manager.broadcast(json.dumps({"type": "mouth", "value": round(value, 2)}))
            await asyncio.sleep(0.03)
        await manager.broadcast(json.dumps({"type": "utter_end"}))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dummy_mouth_stream())
    print("Overlay server is ready.")

# 静的ファイルの配信
static_dir = Path(__file__).parent / "static"

@app.get("/")
async def read_index():
    return FileResponse(static_dir / "index.html")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CSSとJSファイルの直接配信
@app.get("/styles.css")
async def read_styles():
    return FileResponse(static_dir / "styles.css")

@app.get("/client.js")
async def read_client():
    return FileResponse(static_dir / "client.js")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5173)
