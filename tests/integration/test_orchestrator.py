"""Integration test for Brain orchestrator."""
import pytest
from apps.brain.main import BrainOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator can be initialized."""
    orch = BrainOrchestrator()
    assert orch.stt is not None
    assert orch.llm is not None
    assert orch.tts is not None


@pytest.mark.asyncio
async def test_process_text_dummy():
    """Test text processing with dummy providers."""
    orch = BrainOrchestrator()
    # This should not raise exception
    try:
        await orch.process_text("テスト")
    except Exception as e:
        # WebSocket connection failure is OK
        if "overlay" not in str(e).lower():
            raise
