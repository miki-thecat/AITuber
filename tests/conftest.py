"""Pytest configuration."""


def pytest_configure(config):
    config.addinivalue_line("markers", "perf: performance tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
