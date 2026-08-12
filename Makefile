# All targets assume Python 3.11. See README quickstart.
PY ?= python3

.PHONY: install data index run eval test docker-build docker-run clean

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

test:
	$(PY) -m pytest -q

docker-build:
	docker build -t claimlens:latest .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env.example claimlens:latest

clean:
	rm -rf .chroma .bm25 traces *.sqlite3 .pytest_cache
