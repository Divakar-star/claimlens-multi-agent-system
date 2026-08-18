"""Shared fixtures and the fast/model test split.

Tests that need real semantics are marked `requires_model` and skipped unless
CLAIMLENS_RUN_MODEL_TESTS=1 is set, which `make test-model` and `make verify`
do inside Docker. Everything else runs anywhere with no download and no
network -- see ADR 0002 for why the suite is split this way.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

RUN_MODEL_TESTS = os.getenv("CLAIMLENS_RUN_MODEL_TESTS") == "1"


def pytest_collection_modifyitems(config, items):
    skip = pytest.mark.skip(
        reason="needs the embedding model; set CLAIMLENS_RUN_MODEL_TESTS=1 "
               "(make test-model / make verify)"
    )
    for item in items:
        if "requires_model" in item.keywords and not RUN_MODEL_TESTS:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def corpus():
    from claimlens.retrieval.index import load_corpus

    chunks = load_corpus()
    if not chunks:
        pytest.skip("no policy corpus on disk -- run `make data`")
    return chunks


@pytest.fixture(scope="session")
def chunk_ids(corpus):
    return {c.chunk_id for c in corpus}


@pytest.fixture(scope="session")
def golden_cases():
    import json

    from claimlens.config import settings

    if not settings.golden_path.exists():
        pytest.skip("golden set missing -- run `make data`")
    return [json.loads(line) for line in settings.golden_path.read_text().splitlines()]
