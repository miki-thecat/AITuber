
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

app = FastAPI()

# 静的ファイルの配信
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを待機（必要であれば）
            data = await websocket.receive_text()
            # ここではブロードキャストはせず、接続を維持する
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

# テスト用に、定期的にメッセージをブロードキャストするサンプル
async def dummy_mouth_stream():
    import json
    import math
    import time
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
    # テスト用のダミーストリームを開始
    asyncio.create_task(dummy_mouth_stream())
    print("Overlay server is ready.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5173)
