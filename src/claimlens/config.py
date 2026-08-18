"""Central settings.

Why this exists as a module rather than scattered os.getenv calls: the
escalation thresholds and the rate-limit budget are policy, not implementation
detail. A reviewer should be able to read one file and know exactly what the
system will and will not decide on its own, and what it will spend doing it.

Every value is environment-overridable and every value has a default that
works with no .env file present.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    # python-dotenv is pinned in requirements.txt, but config must still import
    # in a minimal environment (data generation, CI lint) where it is absent.
    # Environment variables set directly by the shell still work.
    pass

REPO_ROOT = Path(__file__).resolve().parents[2]

# Notional pricing, USD per 1M tokens, used only to compute cost_per_claim_usd
# in the eval harness. Free-tier runs cost $0, so a real-dollar figure would be
# meaningless; these are Gemini's published PAID-tier rates so the agentic-vs-
# baseline comparison can be quantitative.
# Source: https://ai.google.dev/gemini-api/docs/pricing -- retrieved 2026-08-18.
# Verify before quoting these numbers anywhere; prices change.
PRICING_USD_PER_MTOK: dict[str, dict[str, float]] = {
    "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
}


def _f(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _i(name: str, default: int) -> int:
    return int(os.getenv(name, default))


@dataclass(frozen=True)
class Settings:
    """Runtime configuration, resolved once at import time."""

    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())

    # Both tiers default to the same model. That is not a mistake -- see ADR
    # 0006. The 2.5 tiers task.md specifies are capped at 20 requests per day on
    # the free tier, which is less than one eval run; 3.1 Flash Lite allows 500.
    # The two names are kept separate so the two-tier design of ADR 0004 is one
    # .env edit away.
    model_reasoning: str = field(
        default_factory=lambda: os.getenv("MODEL_REASONING", "gemini-3.1-flash-lite")
    )
    model_cheap: str = field(
        default_factory=lambda: os.getenv("MODEL_CHEAP", "gemini-3.1-flash-lite")
    )

    # Rate limiting. Measured from the AI Studio rate-limit page for this
    # project on 2026-08-18: 3.1 Flash Lite 15 RPM / 500 RPD, 2.5 Flash 5 RPM /
    # 20 RPD, 2.5 Flash Lite 10 RPM / 20 RPD, all at 250K TPM. The defaults sit
    # below those measurements so a burst does not walk into a 429. See README,
    # "Running on a free-tier quota".
    rpm_flash: int = field(default_factory=lambda: _i("RPM_FLASH", 4))
    rpm_flash_lite: int = field(default_factory=lambda: _i("RPM_FLASH_LITE", 12))
    rpd_budget: int = field(default_factory=lambda: _i("RPD_BUDGET", 450))

    # Escalation policy.
    auto_decide_max_usd: float = field(default_factory=lambda: _f("AUTO_DECIDE_MAX_USD", 25000.0))
    confidence_threshold: float = field(default_factory=lambda: _f("CONFIDENCE_THRESHOLD", 0.75))

    # Paths.
    repo_root: Path = REPO_ROOT
    data_dir: Path = REPO_ROOT / "data"
    policies_dir: Path = REPO_ROOT / "data" / "policies"
    claims_path: Path = REPO_ROOT / "data" / "claims" / "claims.jsonl"
    golden_path: Path = REPO_ROOT / "data" / "golden" / "golden_set.jsonl"
    chroma_dir: Path = REPO_ROOT / ".chroma"
    bm25_dir: Path = REPO_ROOT / ".bm25"
    traces_dir: Path = REPO_ROOT / "traces"
    sqlite_path: Path = REPO_ROOT / "claimlens.sqlite3"

    # Retrieval.
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_max_tokens: int = 500
    chunk_overlap_tokens: int = 80
    rrf_k: int = 60

    # Data generation.
    random_seed: int = 20260812

    @property
    def use_mock_llm(self) -> bool:
        """True when no API key is present. The demo must run without one."""
        return not self.gemini_api_key

    def rpm_for(self, model: str) -> int:
        return self.rpm_flash_lite if "lite" in model else self.rpm_flash


settings = Settings()
