"""Unit tests for config loader."""
import os
from apps.brain import config


def test_getenv_with_default():
    """Test getenv returns default when not set."""
    result = config.getenv("NONEXISTENT_KEY", "default_value")
    assert result == "default_value"


def test_as_int_with_valid_value():
    """Test as_int with valid integer."""
    os.environ["TEST_INT"] = "42"
    result = config.as_int("TEST_INT", 0)
    assert result == 42


def test_as_int_with_invalid_value():
    """Test as_int falls back to default with invalid value."""
    os.environ["TEST_INT_INVALID"] = "not_a_number"
    result = config.as_int("TEST_INT_INVALID", 99)
    assert result == 99


def test_as_float_with_valid_value():
    """Test as_float with valid float."""
    os.environ["TEST_FLOAT"] = "3.14"
    result = config.as_float("TEST_FLOAT", 0.0)
    assert result == 3.14


def test_as_bool_true():
    """Test as_bool recognizes true values."""
    for value in ["true", "True", "1", "yes", "YES", "on"]:
        os.environ["TEST_BOOL"] = value
        result = config.as_bool("TEST_BOOL", False)
        assert result is True


def test_as_bool_false():
    """Test as_bool recognizes false values."""
    os.environ["TEST_BOOL"] = "false"
    result = config.as_bool("TEST_BOOL", True)
    assert result is False
