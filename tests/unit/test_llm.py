"""Unit tests for LLM providers."""
from apps.brain.llm import DummyLLM, get_llm_provider


def test_dummy_llm_returns_string():
    """Test DummyLLM returns string."""
    llm = DummyLLM()
    result = llm.generate("hello")
    assert isinstance(result, str)
    assert "hello" in result


def test_get_llm_provider_dummy():
    """Test LLM provider factory returns dummy."""
    llm = get_llm_provider("unknown")
    assert isinstance(llm, DummyLLM)
