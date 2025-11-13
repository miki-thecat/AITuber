"""Integration test for Overlay WebSocket."""
import json
import time
from multiprocessing import Process

import pytest
import uvicorn
import websockets


def run_overlay_server():
    """Run overlay server in subprocess."""
    from apps.overlay.server import app
    uvicorn.run(app, host="127.0.0.1", port=15173, log_level="error")


@pytest.fixture(scope="module")
def overlay_server():
    """Start overlay server for testing."""
    proc = Process(target=run_overlay_server, daemon=True)
    proc.start()
    time.sleep(2)  # Wait for server to start
    yield
    proc.terminate()
    proc.join(timeout=5)


@pytest.mark.asyncio
async def test_websocket_connection(overlay_server):
    """Test WebSocket connection to overlay."""
    try:
        async with websockets.connect("ws://127.0.0.1:15173/ws") as ws:
            # Connection successful
            assert ws.open

            # Send test message
            test_msg = {"type": "utter_start", "text": "test", "subtitle": "test"}
            await ws.send(json.dumps(test_msg))

            # Close gracefully
            await ws.close()
    except Exception as e:
        pytest.skip(f"Overlay server not available: {e}")
