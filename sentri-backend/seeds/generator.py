"""Cohort-aware seed data generator for scorer unit tests.

Produces 10 freelancer/cross-border-earner personas with 100+ transactions each.
Each persona's history ends with a handful of deliberately injected "cohort"
transactions that isolate a single anomaly dimension (or a known combination
of dimensions) so scorer tests can assert on each signal independently.

Run with: python -m seeds.generator
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SEED = 42
DATA_PATH = Path(__file__).resolve().parent / "data.json"
_WAT = ZoneInfo("Africa/Lagos")

# "Today" for the purposes of seed generation. Transactions span the 6 months
# before this date; cohort/test-case transactions land on this date itself so
# they are always the most recent thing in a persona's history.
#
# All scorer unit tests freeze wall-clock time to a cohort's own designed
# timestamp (see test_scorer.py / test_transfer.py), so they're unaffected by
# this constant's absolute value -- only relative day_offsets matter to them.
# But live /transfer calls score against real datetime.now(timezone.utc) with
# no override (sentri/api/transfer.py), and sentri/scorer/amount.py's
# AMOUNT_DRIFT compares volatility in the *real* last 0-30 days against the
# real prior 31-90 days. Since every persona's cohort test-case transaction
# is injected at day_offset=0 (i.e. exactly at this date), once real
# wall-clock time is within ~30 days of this constant, that deliberately
# anomalous cohort transaction sits inside the live "recent" window and
# inflates volatility enough to fire AMOUNT_DRIFT on *any* live transfer for
# that persona, regardless of the transfer's own amount or recipient (found
# live 2026-07-30, see PROOF_OF_WORK.md). Kept 90+ days behind the date this
# was last bumped so it stays outside both drift windows (drift resolves to
# None, i.e. never fires) for real transfers for months going forward --
# re-bump if it starts drifting back inside 30 days of real "now".
_REFERENCE_DATE = datetime(2026, 4, 1, tzinfo=_WAT)
_HISTORY_WINDOW_DAYS = 181

# Mix of Yoruba/Igbo/Hausa names. Personas are professional freelancers /
# cross-border earners, not first-time-digital users.
NAMES = [
    "Adaeze Okonkwo",
    "Oluwaseun Adebayo",
    "Ibrahim Suleiman",
    "Chiamaka Eze",
    "Folake Adeyemi",
    "Aisha Muhammad",
    "Emeka Nwosu",
    "Tolulope Ogundipe",
    "Fatima Bello",
    "Chinedu Okafor",
]

# Favor Lagos tech hubs (Yaba, Lekki, Lagos) with a couple of Abuja/PH entries.
LOCATIONS = [
    "Yaba",
    "Lekki",
    "Lagos",
    "Abuja",
    "Yaba",
    "Lekki",
    "Lagos",
    "Port Harcourt",
    "Abuja",
    "Lekki",
]

# Persona 10 (index 9) is the expat_returning_funds / no-social-graph persona
# used for Cohort F.
ARCHETYPES = [
    "remote_developer",
    "freelance_designer",
    "crypto_trader",
    "content_creator",
    "consultant",
    "expat_returning_funds",
    "remote_developer",
    "freelance_designer",
    "crypto_trader",
    "expat_returning_funds",
]

_OFFRAMP_ARCHETYPES = {"crypto_trader", "expat_returning_funds"}

# ~25% airtime/data, ~10% ride-hailing, ~15% food delivery, ~15% P2P
# (family + friends), ~15% one-off merchant/subscription, ~10% utility,
# ~10% inbound stablecoin/USD off-ramp (crypto_trader / expat_returning_funds
# only). Do not deviate without a comment: this is the spec's realistic mix
# for freelancer/cross-border-earner transaction volumes.
_BASE_CATEGORY_WEIGHTS: dict[str, float] = {
    "airtime_data": 0.25,
    "ride_hailing": 0.10,
    "food_delivery": 0.15,
    "p2p_family": 0.06,
    "p2p_friend": 0.09,
    "subscription_merchant": 0.15,
    "utility": 0.10,
    "offramp": 0.10,
}

# Naira ranges per category, per spec. Amounts are inclusive integer naira
# and converted to kobo (x100) at generation time.
_AMOUNT_RANGES_NAIRA: dict[str, tuple[int, int]] = {
    "airtime_data": (500, 10_000),
    "ride_hailing": (1_500, 12_000),
    "food_delivery": (2_500, 18_000),
    "p2p_family": (5_000, 150_000),
    "p2p_friend": (2_000, 50_000),
    "subscription_merchant": (5_000, 40_000),
    "utility": (8_000, 40_000),
    "offramp": (50_000, 800_000),
}

_MEMOS: dict[str, list[str]] = {
    "airtime_data": [
        "MTN data bundle top-up",
        "Airtime recharge",
        "Glo data plan",
        "Weekend data bundle",
    ],
    "ride_hailing": [
        "Bolt ride to client meeting",
        "Uber to coworking space",
        "Bolt ride home",
    ],
    "food_delivery": [
        "Chowdeck lunch order",
        "Jumia Food dinner",
        "Glovo delivery",
    ],
    "p2p_family": [
        "Family upkeep",
        "Support for mum",
        "Family remittance",
    ],
    "p2p_friend": [
        "Owed for lunch",
        "Splitting event costs",
        "Friend support",
    ],
    "subscription_merchant": [
        "Figma subscription",
        "Notion team plan",
        "GitHub Copilot",
        "AWS bill",
        "Google Workspace",
    ],
    "utility": [
        "Electricity bill",
        "DSTV subscription renewal",
    ],
    "offramp": [
        "USDT off-ramp - client payment",
        "Freelance client payment (USD)",
        "Binance P2P sell",
    ],
    "landlord": ["Monthly rent payment"],
}

_MERCHANT_POOLS: dict[str, list[str]] = {
    "airtime_data": ["mtn_airtime", "glo_data_bundle", "airtel_recharge", "nine_mobile_data"],
    "ride_hailing": ["bolt", "uber"],
    "food_delivery": ["chowdeck", "jumia_food", "glovo"],
    # "spaces_and_co_coworking" is deliberately excluded here: it is reserved
    # for Cohort D (a persona's *first* coworking payment).
    "subscription_merchant": ["figma", "notion", "github", "aws", "google_workspace", "canva"],
    "offramp": ["binance_p2p", "usdt_offramp_service", "chipper_cash_usd"],
}

_COWORKING_RECIPIENT = "spaces_and_co_coworking"


def _utility_recipient_for_location(location: str) -> str:
    if location in ("Lagos", "Yaba"):
        return "ikedc_utility"
    if location == "Lekki":
        return "ekedc_utility"
    return "utility_provider_disco"


def _normalize_category_weights(include_offramp: bool) -> dict[str, float]:
    weights = dict(_BASE_CATEGORY_WEIGHTS)
    if include_offramp:
        return weights
    offramp_weight = weights.pop("offramp")
    remaining_total = 1.0 - offramp_weight
    return {category: weight / remaining_total for category, weight in weights.items()}


def _pick_wat_hour(rng: random.Random) -> int:
    # Freelancers do not match a clean 9-5. ~40% work-hours, ~30% evenings,
    # ~20% late night (client-timezone calls), ~10% edge hours. This wide
    # baseline is intentional: it keeps the hour_deviation signal from being
    # trivially over-tuned against a narrow "normal" window.
    roll = rng.random()
    if roll < 0.40:
        return rng.randint(9, 17)
    if roll < 0.70:
        return rng.randint(18, 22)
    if roll < 0.90:
        return rng.choice([23, 0, 1])
    return rng.randint(3, 8)


def _recent_day_offset(rng: random.Random, low: int = 1, high: int = _HISTORY_WINDOW_DAYS) -> int:
    # Skew toward smaller offsets (more recent) so recency decay is baked in.
    span = high - low
    skewed = rng.random() ** 1.6
    return low + int(skewed * span)


def _timestamp_from(day_offset: int, hour: int, minute: int, second: int) -> int:
    local_date = _REFERENCE_DATE - timedelta(days=day_offset)
    dt = datetime(
        local_date.year, local_date.month, local_date.day, hour, minute, second, tzinfo=_WAT
    )
    return int(dt.timestamp())


class _PersonaRecipients:
    """Recipient pools for a single persona's organic transaction history."""

    def __init__(self, user_id: str, location: str, archetype: str, rng: random.Random) -> None:
        self.family_recipient = f"{user_id}_family_mother"
        self.landlord_recipient = f"{user_id}_landlord"
        num_friends = rng.randint(2, 4)
        self.friend_recipients = [f"{user_id}_friend_{i}" for i in range(num_friends)]
        self.utility_recipient = _utility_recipient_for_location(location)
        self.include_offramp = archetype in _OFFRAMP_ARCHETYPES

    def pool_for(self, category: str) -> list[str]:
        if category == "p2p_family":
            return [self.family_recipient]
        if category == "p2p_friend":
            return self.friend_recipients
        if category == "utility":
            return [self.utility_recipient]
        return _MERCHANT_POOLS[category]


def _make_transaction(
    amount_naira: float,
    day_offset: int,
    hour: int,
    minute: int,
    second: int,
    recipient_id: str,
    memo: str,
    currency: str = "NGN",
    cross_border: bool = False,
) -> dict[str, Any]:
    return {
        "amount_kobo": int(round(amount_naira * 100)),
        "timestamp": _timestamp_from(day_offset, hour, minute, second),
        "recipient_id": recipient_id,
        "currency": currency,
        "cross_border": cross_border,
        "memo": memo,
    }


def _generate_organic_transactions(
    recipients: _PersonaRecipients, rng: random.Random
) -> list[dict[str, Any]]:
    weights = _normalize_category_weights(recipients.include_offramp)
    categories = list(weights.keys())
    category_weights = list(weights.values())

    transactions: list[dict[str, Any]] = []
    for _ in range(94):
        category = rng.choices(categories, weights=category_weights, k=1)[0]
        recipient_id = rng.choice(recipients.pool_for(category))
        low, high = _AMOUNT_RANGES_NAIRA[category]
        amount_naira = rng.randint(low, high)
        memo = rng.choice(_MEMOS[category])
        day_offset = _recent_day_offset(rng)
        hour = _pick_wat_hour(rng)
        minute = rng.randint(0, 59)
        second = rng.randint(0, 59)

        if category == "offramp":
            currency = rng.choices(["USDT", "USD", "NGN"], weights=[0.5, 0.35, 0.15], k=1)[0]
            transactions.append(
                _make_transaction(
                    amount_naira,
                    day_offset,
                    hour,
                    minute,
                    second,
                    recipient_id,
                    memo,
                    currency=currency,
                    cross_border=True,
                )
            )
        else:
            transactions.append(
                _make_transaction(
                    amount_naira, day_offset, hour, minute, second, recipient_id, memo
                )
            )

    # Six monthly rent payments to a dedicated, high-volume recurring
    # recipient. This builds the "known recipient, high familiarity" history
    # that Cohort E's landlord payment tests amount_z_recipient against.
    for month in range(6):
        day_offset = min(_HISTORY_WINDOW_DAYS - 1, 1 + month * 30)
        amount_naira = 300_000 + rng.randint(-10_000, 10_000)
        hour = rng.randint(9, 17)
        minute = rng.randint(0, 59)
        second = rng.randint(0, 59)
        transactions.append(
            _make_transaction(
                amount_naira,
                day_offset,
                hour,
                minute,
                second,
                recipients.landlord_recipient,
                _MEMOS["landlord"][0],
            )
        )

    return transactions


# Cohort sequence per persona. Persona 10 (expat_returning_funds, no exposed
# social graph) uses Cohort F in place of Cohort A: F is "the same test as A"
# but specifically for the no-graph case, so there is no need to also emit a
# redundant A for that persona. Every other persona emits A-E, so across the
# full dataset all six cohorts (A-F) are represented.
_DEFAULT_COHORT_SEQUENCE = ["A", "B", "C", "D", "E"]
_NO_GRAPH_COHORT_SEQUENCE = ["F", "B", "C", "D", "E"]

_COHORT_HOUR = {"A": 14, "B": 3, "C": 23, "D": 11, "E": 10, "F": 14}
_COHORT_MINUTE = {"A": 0, "B": 0, "C": 30, "D": 0, "E": 0, "F": 0}
_COHORT_NARRATIVE_MEMO = {
    "A": "URGENT ADVANCE REFUND",
    "B": "family emergency",
    "C": "recruiter signing bonus",
    "D": "workspace subscription",
    "E": "rent transfer to landlord",
    "F": "URGENT ADVANCE REFUND",
}
_COHORT_AMOUNT_NAIRA = {
    "A": 2_000_000,
    "B": 15_000,
    "C": 320_000,
    "D": 25_000,
    "E": 500_000,
    "F": 2_000_000,
}
_COHORT_EXPECTED_FIRES = {"A": True, "B": True, "C": True, "D": False, "E": True, "F": True}
_COHORT_NOTES = {
    "A": "New recipient + high amount z-score at a normal hour.",
    "B": "New recipient + normal amount at a 03:00 hour.",
    "C": "New recipient + borderline amount and borderline (23:30) hour together.",
    "D": "New recipient (first coworking payment) but normal amount/hour: should pass silently.",
    "E": "Known, frequent recipient (landlord) but amount is well above their usual ~NGN300k: "
    "familiarity is high, so amount_z_recipient may fire on its own without other signals.",
    "F": "Same shape as Cohort A, but persona has no exposed social graph (proximity is None); "
    "amount_z should still fire independently.",
}


def _cohort_recipient(user_id: str, cohort: str, recipients: _PersonaRecipients) -> str:
    if cohort in ("A", "F"):
        return f"{user_id}_advance_refund_agent"
    if cohort == "B":
        return f"{user_id}_new_contact_b"
    if cohort == "C":
        return f"{user_id}_recruiter_contact"
    if cohort == "D":
        return _COWORKING_RECIPIENT
    if cohort == "E":
        return recipients.landlord_recipient
    raise ValueError(f"unknown cohort: {cohort}")


def _generate_cohort_transactions(
    user_id: str, has_social_graph: bool, recipients: _PersonaRecipients
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sequence = _DEFAULT_COHORT_SEQUENCE if has_social_graph else _NO_GRAPH_COHORT_SEQUENCE

    tail_transactions: list[dict[str, Any]] = []
    test_cases: list[dict[str, Any]] = []
    for cohort in sequence:
        recipient_id = _cohort_recipient(user_id, cohort, recipients)
        memo = f"{_COHORT_NARRATIVE_MEMO[cohort]} [COHORT_{cohort}_TEST]"
        txn = _make_transaction(
            _COHORT_AMOUNT_NAIRA[cohort],
            day_offset=0,
            hour=_COHORT_HOUR[cohort],
            minute=_COHORT_MINUTE[cohort],
            second=0,
            recipient_id=recipient_id,
            memo=memo,
        )
        tail_transactions.append(txn)

        event = {
            "user_id": user_id,
            "amount_kobo": txn["amount_kobo"],
            "timestamp": txn["timestamp"],
            "recipient_id": txn["recipient_id"],
            "currency": txn["currency"],
            "device_id": None,
            "memo": txn["memo"],
            "cross_border": txn["cross_border"],
        }
        test_cases.append(
            {
                "user_id": user_id,
                "cohort": cohort,
                "event": event,
                "expected_fires": _COHORT_EXPECTED_FIRES[cohort],
                "notes": _COHORT_NOTES[cohort],
            }
        )

    return tail_transactions, test_cases


def _build_friends(user_ids: list[str], rng: random.Random) -> dict[str, list[str]]:
    # Persona 10 (last id) has no exposed social graph: exclude it both as a
    # subject and as a candidate friend for anyone else.
    graphed_ids = user_ids[:-1]
    friends: dict[str, list[str]] = {}
    for user_id in graphed_ids:
        candidates = [other for other in graphed_ids if other != user_id]
        num_friends = rng.randint(2, 4)
        friends[user_id] = sorted(rng.sample(candidates, k=num_friends))
    friends[user_ids[-1]] = []
    return friends


def generate_seed_data(seed: int = SEED) -> dict[str, Any]:
    """Build the full deterministic seed dataset (users + cohort test cases)."""
    rng = random.Random(seed)

    user_ids = [f"user_{index + 1:03d}" for index in range(len(NAMES))]
    friends_by_user = _build_friends(user_ids, rng)

    users: list[dict[str, Any]] = []
    test_cases: list[dict[str, Any]] = []

    for index, user_id in enumerate(user_ids):
        location = LOCATIONS[index]
        archetype = ARCHETYPES[index]
        has_social_graph = index != len(NAMES) - 1

        recipients = _PersonaRecipients(user_id, location, archetype, rng)
        organic = _generate_organic_transactions(recipients, rng)
        cohort_tail, persona_test_cases = _generate_cohort_transactions(
            user_id, has_social_graph, recipients
        )

        transactions = organic + cohort_tail
        transactions.sort(key=lambda txn: txn["timestamp"])

        users.append(
            {
                "user_id": user_id,
                "name": NAMES[index],
                "location": location,
                "archetype": archetype,
                "has_social_graph": has_social_graph,
                "friends": friends_by_user[user_id],
                "transactions": transactions,
            }
        )
        test_cases.extend(persona_test_cases)

    return {"users": users, "test_cases": test_cases}


def write_seed_data(path: Path = DATA_PATH, seed: int = SEED) -> Path:
    """Generate seed data and write it to `path` as JSON. Returns the path."""
    data = generate_seed_data(seed)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    written = write_seed_data()
    print(f"wrote seed data to {written}")


if __name__ == "__main__":
    main()
