.PHONY: dev overlay brain test clean install

install:
pip install -r requirements.txt

overlay:
uvicorn apps.overlay.server:app --host 0.0.0.0 --port 5173

brain:
python -m apps.brain.main

dev:
./scripts/run_dev.sh

test:
pytest -q

test-verbose:
pytest -v

test-unit:
pytest tests/unit/ -v

test-integration:
pytest tests/integration/ -v

test-e2e:
pytest tests/e2e/ -v -m e2e

test-perf:
pytest tests/perf/ -v -m perf

clean:
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.wav" -delete
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
