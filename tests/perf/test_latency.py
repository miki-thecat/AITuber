"""Performance test for latency measurement."""
import pytest
import asyncio
import time
from apps.brain.main import BrainOrchestrator


@pytest.mark.perf
@pytest.mark.asyncio
async def test_response_latency():
    """Measure response latency."""
    orch = BrainOrchestrator()
    
    start_time = time.time()
    
    try:
        await orch.process_text("テスト")
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time (dummy providers are fast)
        assert elapsed < 10.0, f"Response took too long: {elapsed}s"
    except Exception as e:
        if "overlay" in str(e).lower():
            pytest.skip("Overlay not available")
        else:
            raise
