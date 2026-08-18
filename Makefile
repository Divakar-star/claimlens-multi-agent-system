# All targets assume Python 3.11. See README quickstart.
PY ?= python3

.PHONY: install data index run eval test test-model verify docker-build docker-run clean

install:
	pip install -r requirements.txt
	pip install -e .

data:
	$(PY) scripts/generate_data.py

index:
	$(PY) scripts/build_index.py

run:
	uvicorn claimlens.api.main:app --host 0.0.0.0 --port 8000

eval:
	$(PY) eval/run_eval.py $(ARGS)

# Fast tier: no model, no network, no downloads. This is what CI runs.
test:
	$(PY) -m pytest -q

# Full tier: adds the tests that need real embeddings.
test-model:
	CLAIMLENS_RUN_MODEL_TESTS=1 $(PY) -m pytest -q

# One command per phase gate. Builds the image and runs the full suite inside
# it, so the result does not depend on anything installed on the host.
verify: docker-build
	docker run --rm -e CLAIMLENS_RUN_MODEL_TESTS=1 claimlens:latest \
		python -m pytest -q -rA

docker-build:
	docker build -t claimlens:latest .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env.example claimlens:latest

clean:
	rm -rf .chroma .bm25 traces *.sqlite3 .pytest_cache
