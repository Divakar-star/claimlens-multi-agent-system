"""Generates the synthetic corpus: 12 policies, 120 claims, 60 golden cases.

Why synthetic: free-tier Gemini may retain prompts for training, so no real
claim text can touch the API. Generating the data also lets the corpus be
adversarial on purpose -- cross-referenced policy documents that defeat
keyword-only and embedding-only search, and claims whose narrative contradicts
the policy_type they were filed under.

Everything is deterministic from settings.random_seed. Running this twice
produces byte-identical files, so the generated data can be committed and a
reviewer never has to run it.

Prose lives in _policy_source.py and _claim_source.py; this file is the
algorithm. Usage: `make data`.
"""

from __future__ import annotations

import json
import random
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from _claim_source import INCIDENTS  # noqa: E402
from _policy_source import POLICIES  # noqa: E402

from claimlens.config import settings  # noqa: E402

# Section headings, in render order. The slugs derived from these are half of
# every chunk id, so changing this list invalidates every golden label.
SECTIONS = [
    "Coverage Summary",
    "What Is Covered",
    "Exclusions",
    "Deductible and Limits",
    "Interaction With Other Coverages",
    "Conditions and Claims Handling",
    "Definitions",
]

# Distribution required by task.md 3, Phase 1. Enforced by assert_distribution().
TARGET_COUNTS = {"covered": 48, "excluded": 30, "ambiguous": 24, "high_value": 18}
TOTAL_CLAIMS = 120
GOLDEN_SIZE = 60
CONTRADICTION_COUNT = 12  # 10% of claims, carved out of the ambiguous bucket

# Narrative furniture. Kept dull on purpose: the incident core carries the
# facts, these carry the register.
OPENERS = {
    "terse": ["", "Reporting a claim. ", "Claim details below. "],
    "plain": [
        "I want to report what happened. ",
        "Here is what happened. ",
        "Submitting this claim for damage to my property. ",
    ],
    "rambling": [
        "I am not sure I am filling this in right so bear with me, but here goes. ",
        "Sorry this is long, I want to make sure you have the full picture. ",
        "I have been meaning to call about this since it happened, so apologies for "
        "the delay in getting it written down. ",
    ],
    "formal": [
        "I write to notify you of a loss under the above policy. ",
        "Please accept this as formal notification of a claim. ",
    ],
}

FOLLOWUPS = [
    "I took photographs at the time and can send them over.",
    "My partner was with me and saw the whole thing.",
    "I reported it the same day, or as close to it as I could manage.",
    "The neighbours came out and one of them helped me sort it out.",
    "I have kept every receipt connected with this.",
    "Nobody was hurt, which is the main thing.",
    "It was late in the evening and the light was poor.",
    "This has never happened to me before in twenty years of driving.",
    "I called the emergency line first and they told me to submit it here.",
    "The person who came out said they see this sort of thing constantly.",
    "I have not had anything repaired yet because I wanted to check with you first.",
    "There is a written estimate from a local firm if you need to see it.",
    "I am not trying to make more of this than it is, I just want it dealt with.",
    "Honestly the whole thing has been a nightmare to sort out.",
    "I checked the policy documents before submitting but could not work out where "
    "this falls.",
    "My work has been disrupted by this and I would like it settled quickly.",
    "The weather that week was bad across the whole area.",
    "I have been with you a long time and have not claimed before.",
]

CLOSERS = [
    "Please let me know what you need from me.",
    "Happy to provide anything else that helps.",
    "I would appreciate a decision as soon as possible.",
    "Let me know if I have missed anything.",
    "Thanks for looking at this.",
    "",
]

AMOUNT_PHRASINGS = [
    "The estimate I have is ${amount:,.0f}.",
    "I am claiming ${amount:,.0f} in total.",
    "The quote came to ${amount:,.0f}.",
    "Repair costs are around ${amount:,.0f} based on what I have been told.",
    "Total loss on the schedule is ${amount:,.0f}.",
]

# Deterministic typo substitutions, applied to a fixed fraction of narratives so
# the corpus is not uniformly well written.
TYPOS = [
    ("the ", "teh "), ("and ", "adn "), ("because", "becuase"),
    ("received", "recieved"), ("definitely", "definately"), ("I am", "Im"),
    ("it is", "its"), ("would", "wold"),
]

ATTACHMENT_POOL = [
    ["photos"], ["photos", "estimate"], ["police_report", "photos"],
    ["estimate"], [], ["photos", "receipt"], ["police_report"],
    ["invoice", "photos"], ["inspection_report"], ["photos", "estimate", "receipt"],
]


def slugify(text: str) -> str:
    """Chunk ids are built from these, so this must stay stable across phases."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render_policy(policy: dict) -> str:
    """Renders one policy document as markdown.

    Numbers are substituted from the structured fields rather than typed into
    the prose, so the document a model reads and the figures coverage_rules.py
    computes with cannot drift apart.
    """
    fmt = {"limit": policy["limit"], "deductible": policy["deductible"]}
    parts = [
        f"# {policy['title']}",
        "",
        f"**Form {policy['form']}** | Policy ID `{policy['policy_id']}`",
        "",
        "## Coverage Summary",
        "",
        policy["summary"],
        "",
        "## What Is Covered",
        "",
        policy["covered"],
        "",
        "## Exclusions",
        "",
        "The following are excluded from coverage under this form:",
        "",
    ]
    for i, exc in enumerate(policy["exclusions"], start=1):
        parts.append(f"{i}. {exc}")
    parts += [
        "",
        "## Deductible and Limits",
        "",
        policy["limits_note"].format(**fmt),
        "",
        "## Interaction With Other Coverages",
        "",
        policy["interaction"],
        "",
        "## Conditions and Claims Handling",
        "",
        policy["conditions"],
        "",
        "## Definitions",
        "",
    ]
    for term, definition in policy["definitions"]:
        parts.append(f"**{term}.** {definition}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def valid_chunk_ids() -> set[str]:
    """Every chunk id the corpus can legitimately produce.

    Golden labels are checked against this set, so a typo in a label fails at
    generation time rather than silently depressing citation_recall later.
    """
    return {
        f"{p['slug']}#{slugify(section)}"
        for p in POLICIES
        for section in SECTIONS
    }


def word_count(text: str) -> int:
    return len(text.split())


def apply_typos(text: str, rng: random.Random) -> str:
    out = text
    for find, repl in rng.sample(TYPOS, k=3):
        out = out.replace(find, repl, 1)
    return out


def build_narrative(core: str, amount: float, rng: random.Random) -> str:
    """Assembles a 60-250 word first-person narrative around an incident core.

    Register is chosen first because it decides length: terse claimants write
    two sentences, rambling ones pad. Filler is then added until the word count
    clears the floor, and truncated if it would breach the ceiling.
    """
    register = rng.choice(["terse", "plain", "plain", "rambling", "rambling", "formal"])
    filler_target = {"terse": 2, "plain": 3, "rambling": 6, "formal": 4}[register]

    body = [rng.choice(OPENERS[register]) + core]
    pool = rng.sample(FOLLOWUPS, k=min(filler_target + 3, len(FOLLOWUPS)))
    body.append(rng.choice(AMOUNT_PHRASINGS).format(amount=amount))

    i = 0
    while word_count(" ".join(body)) < 60 and i < len(pool):
        body.append(pool[i])
        i += 1
    while i < filler_target and word_count(" ".join(body)) < 220 and i < len(pool):
        body.append(pool[i])
        i += 1

    closer = rng.choice(CLOSERS)
    if closer and word_count(" ".join(body)) + word_count(closer) <= 250:
        body.append(closer)

    text = " ".join(s for s in body if s).strip()
    if register == "rambling" and rng.random() < 0.6:
        text = apply_typos(text, rng)
    words = text.split()
    if len(words) > 250:
        text = " ".join(words[:250])
    return text


def category_amount(category: str, rng: random.Random, policy: dict) -> float:
    """High-value claims must clear AUTO_DECIDE_MAX_USD; the rest must not.

    This is what makes the ceiling testable: the escalation metric is
    meaningless if the two groups overlap around the threshold.
    """
    ceiling = settings.auto_decide_max_usd
    if category == "high_value":
        return round(rng.uniform(ceiling * 1.2, ceiling * 8), 2)
    upper = min(policy["limit"] if policy["limit"] else 2000, ceiling * 0.75)
    upper = max(upper, 400)
    return round(rng.uniform(150, upper), 2)


def plan_categories() -> dict[str, dict[str, int]]:
    """Per-policy-type category counts that hit the global distribution exactly.

    Six types carry 3 excluded and 1 high-value, six carry 2 and 2. Both add to
    10 claims per type, 120 overall, and the global totals land on the required
    40/25/20/15 split without any rounding slack.
    """
    plan = {}
    for i, policy in enumerate(POLICIES):
        heavy_exclusion = i % 2 == 0
        plan[policy["policy_type"]] = {
            "covered": 4,
            "excluded": 3 if heavy_exclusion else 2,
            "ambiguous": 2,
            "high_value": 1 if heavy_exclusion else 2,
        }
    return plan


def generate_claims(rng: random.Random) -> list[dict]:
    """Builds the 120 claims.

    One of the two ambiguous claims per policy type is a contradiction case --
    the narrative describes a peril belonging to a different form than the one
    the claim was filed under. That is 12 claims, the required 10%, and they are
    the cases the Reviewer agent exists to catch.
    """
    plan = plan_categories()
    base_time = datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc)
    rows: list[dict] = []
    n = 0

    for policy in POLICIES:
        ptype = policy["policy_type"]
        pool = INCIDENTS[ptype]
        for category, count in plan[ptype].items():
            for j in range(count):
                is_contradiction = category == "ambiguous" and j == 1
                source_key = "contradiction" if is_contradiction else category
                cores = pool[source_key]
                core = cores[j % len(cores)]

                amount = category_amount(category, rng, policy)
                n += 1
                rows.append({
                    "claim_id": f"CLM-{n:04d}",
                    "submitted_at": (
                        base_time + timedelta(
                            days=rng.randint(0, 180), minutes=rng.randint(0, 600)
                        )
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "policy_id": policy["policy_id"],
                    "policy_type": ptype,
                    "claimant_narrative": build_narrative(core["text"], amount, rng),
                    "claimed_amount_usd": amount,
                    "attachments": rng.choice(ATTACHMENT_POOL),
                    "prior_claims_count": rng.choices(
                        [0, 1, 2, 3], weights=[55, 27, 13, 5]
                    )[0],
                    # Internal labels. Stripped before writing claims.jsonl -- a
                    # claim arriving from a claimant does not come pre-labelled.
                    "_category": category,
                    "_contradiction": is_contradiction,
                    "_mention": core["mention"],
                    "_chunks": core["chunks"],
                })

    rows.sort(key=lambda r: r["claim_id"])
    return rows


def expected_labels(row: dict) -> tuple[str, str]:
    """Maps a claim category to its expected route and final decision.

    route is what the Router should do with the claim; decision is what the
    system should ultimately conclude.

      covered     -> standard / approve
      excluded    -> standard / deny
      ambiguous   -> deep / escalate      (arguable coverage, low confidence)
      high_value  -> escalate / escalate  (above AUTO_DECIDE_MAX_USD, never auto)
      contradiction -> escalate / escalate (narrative contradicts policy_type)
    """
    if row["_contradiction"]:
        return "escalate", "escalate"
    return {
        "covered": ("standard", "approve"),
        "excluded": ("standard", "deny"),
        "ambiguous": ("deep", "escalate"),
        "high_value": ("escalate", "escalate"),
    }[row["_category"]]


def build_golden(claims: list[dict], rng: random.Random) -> list[dict]:
    """Labels 60 of the 120 claims.

    Every contradiction case is included: they are the hardest cases and the
    ones that justify having a Reviewer at all. The remainder is a stratified
    half of each category, so the golden set carries the same distribution as
    the full corpus.
    """
    by_cat: dict[str, list[dict]] = {}
    for row in claims:
        by_cat.setdefault(row["_category"], []).append(row)

    chosen: list[dict] = [r for r in claims if r["_contradiction"]]
    chosen_ids = {r["claim_id"] for r in chosen}

    for category, target in TARGET_COUNTS.items():
        want = target // 2
        have = len([r for r in chosen if r["_category"] == category])
        candidates = [r for r in by_cat[category] if r["claim_id"] not in chosen_ids]
        rng.shuffle(candidates)
        for row in candidates[: max(0, want - have)]:
            chosen.append(row)
            chosen_ids.add(row["claim_id"])

    chosen.sort(key=lambda r: r["claim_id"])

    golden = []
    for row in chosen:
        route, decision = expected_labels(row)
        if row["_contradiction"]:
            note = (
                f"Narrative describes a peril governed by another form; claim was "
                f"filed under {row['policy_type']}."
            )
        else:
            note = {
                "covered": "Clearly within the coverage grant of the filed form.",
                "excluded": "Squarely within a stated exclusion.",
                "ambiguous": "Genuinely arguable; a competent adjuster would hesitate.",
                "high_value": (
                    f"Claimed amount ${row['claimed_amount_usd']:,.0f} exceeds the "
                    f"auto-decide ceiling of ${settings.auto_decide_max_usd:,.0f}."
                ),
            }[row["_category"]]
        golden.append({
            "claim_id": row["claim_id"],
            "expected_route": route,
            "expected_decision": decision,
            "required_policy_chunks": row["_chunks"],
            "rationale_must_mention": row["_mention"],
            "notes": note,
        })
    return golden


def assert_distribution(claims: list[dict], golden: list[dict]) -> None:
    """Fails generation if the corpus does not match the specified distribution.

    This runs inside `make data` rather than in the test suite because a corpus
    that violates it should never reach disk in the first place.
    """
    assert len(claims) == TOTAL_CLAIMS, f"expected {TOTAL_CLAIMS} claims, got {len(claims)}"
    assert len(golden) == GOLDEN_SIZE, f"expected {GOLDEN_SIZE} golden, got {len(golden)}"

    counts: dict[str, int] = {}
    for row in claims:
        counts[row["_category"]] = counts.get(row["_category"], 0) + 1
    for category, target in TARGET_COUNTS.items():
        assert counts.get(category) == target, (
            f"{category}: expected {target} ({target / TOTAL_CLAIMS:.0%}), "
            f"got {counts.get(category)}"
        )

    contradictions = [r for r in claims if r["_contradiction"]]
    assert len(contradictions) == CONTRADICTION_COUNT, (
        f"expected {CONTRADICTION_COUNT} contradiction narratives, "
        f"got {len(contradictions)}"
    )

    ceiling = settings.auto_decide_max_usd
    for row in claims:
        amount = row["claimed_amount_usd"]
        if row["_category"] == "high_value":
            assert amount > ceiling, f"{row['claim_id']}: high_value {amount} <= {ceiling}"
        else:
            assert amount <= ceiling, f"{row['claim_id']}: {amount} > {ceiling}"
        words = word_count(row["claimant_narrative"])
        assert 60 <= words <= 250, f"{row['claim_id']}: narrative is {words} words"

    valid = valid_chunk_ids()
    for case in golden:
        for chunk in case["required_policy_chunks"]:
            assert chunk in valid, f"{case['claim_id']}: unknown chunk id {chunk!r}"

    golden_ids = {c["claim_id"] for c in golden}
    for row in contradictions:
        assert row["claim_id"] in golden_ids, (
            f"{row['claim_id']}: contradiction case missing from golden set"
        )

    for policy in POLICIES:
        words = word_count(render_policy(policy))
        assert 400 <= words <= 900, f"{policy['slug']}: policy is {words} words"
        assert len(policy["exclusions"]) >= 3, f"{policy['slug']}: needs 3+ exclusions"
        others = [p["form"] for p in POLICIES if p["slug"] != policy["slug"]]
        text = render_policy(policy)
        assert any(form in text for form in others), (
            f"{policy['slug']}: no cross-reference to another form"
        )


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    rng = random.Random(settings.random_seed)

    settings.policies_dir.mkdir(parents=True, exist_ok=True)
    for policy in POLICIES:
        out = settings.policies_dir / f"{policy['slug']}.md"
        out.write_text(render_policy(policy), encoding="utf-8", newline="\n")

    claims = generate_claims(rng)
    golden = build_golden(claims, rng)
    assert_distribution(claims, golden)

    public = [{k: v for k, v in row.items() if not k.startswith("_")} for row in claims]
    write_jsonl(settings.claims_path, public)
    write_jsonl(settings.golden_path, golden)

    counts: dict[str, int] = {}
    for row in claims:
        counts[row["_category"]] = counts.get(row["_category"], 0) + 1

    print(f"policies : {len(POLICIES)} -> {settings.policies_dir}")
    print(f"claims   : {len(public)} -> {settings.claims_path}")
    for category, count in sorted(counts.items()):
        print(f"           {category:<11} {count:>3}  ({count / len(claims):.0%})")
    print(f"           contradiction {len([r for r in claims if r['_contradiction']]):>2}"
          f"  ({CONTRADICTION_COUNT / len(claims):.0%})")
    print(f"golden   : {len(golden)} -> {settings.golden_path}")
    print(f"chunk ids: {len(valid_chunk_ids())} addressable sections")


if __name__ == "__main__":
    main()
