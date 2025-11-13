"""E2E test for text input mode."""

import pytest

from apps.brain.main import BrainOrchestrator


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_text_mode_e2e():
    """Test complete text mode flow."""
    orch = BrainOrchestrator()

    # Test with dummy providers (no overlay connection needed)
    try:
        await orch.process_text("こんにちは")
        # If we get here without exception, test passes
        assert True
    except Exception as e:
        # Overlay connection failure is acceptable in E2E test
        if "overlay" in str(e).lower() or "websocket" in str(e).lower():
            pytest.skip(f"Overlay not available: {e}")
        else:
            raise
