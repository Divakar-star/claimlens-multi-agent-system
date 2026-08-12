# Two stages. The builder needs a C toolchain to compile any sdists; the runtime
# does not, and shipping build-essential is ~300MB of dead weight.
#
# The size story that matters is torch: sentence-transformers depends on it, and
# the default PyPI torch wheel for Linux bundles the CUDA runtime -- several GB of
# GPU libraries this project can never use, since embeddings run on CPU by design.
# Installing the CPU-only build first means the later `pip install -r
# requirements.txt` sees the requirement already satisfied and leaves it alone.
# See docs/FAILURES.md entry 1.

FROM python:3.11-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# CPU-only torch, same version pinned in requirements.txt.
RUN pip install --no-cache-dir torch==2.13.0 \
    --index-url https://download.pytorch.org/whl/cpu

WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN pip install --no-cache-dir -e . --no-deps

# Drop test suites, C headers and bytecode that ship inside wheels.
RUN find /opt/venv -name "__pycache__" -type d -prune -exec rm -rf {} + \
 && find /opt/venv -name "*.pyc" -delete \
 && find /opt/venv -name "tests" -type d -prune -exec rm -rf {} + \
 && find /opt/venv -name "*.h" -delete \
 && find /opt/venv -name "*.a" -delete


FROM python:3.11-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY src/ ./src/
COPY data/ ./data/
COPY eval/ ./eval/
COPY scripts/ ./scripts/
COPY Makefile pyproject.toml ./

# Embedding weights and indexes are baked in at build time so the container
# starts instantly and the demo runs with no network and no API key.
RUN HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 python scripts/build_index.py \
 || echo "index build skipped (phase 2 not implemented yet)"

EXPOSE 8000
CMD ["uvicorn", "claimlens.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
