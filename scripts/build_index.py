"""Builds the Chroma and BM25 indexes from data/policies/.

Kept as a script rather than lazy index-on-first-request so the Docker image
build absorbs the cost, including the model download, and the container starts
instantly with no network. Usage: `make index`.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from claimlens.config import settings  # noqa: E402
from claimlens.retrieval.index import build_indexes, load_corpus  # noqa: E402


def main() -> None:
    started = time.time()
    chunks = load_corpus()
    stats = build_indexes(chunks)
    elapsed = time.time() - started

    per_doc: dict[str, int] = {}
    for chunk in chunks:
        per_doc[chunk.policy_slug] = per_doc.get(chunk.policy_slug, 0) + 1

    print(f"documents : {len(per_doc)}")
    print(f"chunks    : {stats['chunks']}  ({stats['dimensions']}-dim embeddings)")
    print(f"chroma    : {settings.chroma_dir}")
    print(f"bm25      : {settings.bm25_dir}")
    print(f"elapsed   : {elapsed:.1f}s")
    if elapsed > 60:
        print("WARNING: index build exceeded the 60s Phase 2 budget")


if __name__ == "__main__":
    main()
