import asyncio
import json
import math
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import uvicorn

app = FastAPI()
static_dir = Path(__file__).parent / "static"

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
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def index():
    html_file = static_dir / "index.html"
    return FileResponse(html_file, media_type="text/html")

@app.get("/styles.css")
async def styles():
    css_file = static_dir / "styles.css"
    return FileResponse(css_file, media_type="text/css")

@app.get("/client.js")
async def client():
    js_file = static_dir / "client.js"
    return FileResponse(js_file, media_type="application/javascript")

@app.get("/test.html", response_class=HTMLResponse)
async def test():
    test_file = static_dir / "test.html"
    return FileResponse(test_file, media_type="text/html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def dummy_mouth_stream():
    while True:
        await asyncio.sleep(3)
        await manager.broadcast(json.dumps({
            "type": "utter_start",
            "text": "こんにちは！",
            "subtitle": "こんにちは！"
        }))
        for i in range(100):
            value = (math.sin(i * 0.2) + 1) / 2
            await manager.broadcast(json.dumps({
                "type": "mouth",
                "value": round(value, 2)
            }))
            await asyncio.sleep(0.03)
        await manager.broadcast(json.dumps({"type": "utter_end"}))

@app.on_event("startup")
async def startup():
    asyncio.create_task(dummy_mouth_stream())
    print(f"Overlay server ready. Static dir: {static_dir}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5173)
