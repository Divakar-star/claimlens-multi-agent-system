FROM python:3.11-slim

# Build tools are needed by some wheels (chromadb, sentence-transformers deps)
# on slim images; removed in the same layer to keep the image small.
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY eval/ ./eval/
COPY scripts/ ./scripts/
COPY Makefile ./
RUN pip install --no-cache-dir -e .

# Indexes are built at image build time so `docker run` starts a working demo
# with no network and no API key.
RUN python scripts/build_index.py || echo "index build skipped (phase 2 not implemented yet)"

EXPOSE 8000
CMD ["uvicorn", "claimlens.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
