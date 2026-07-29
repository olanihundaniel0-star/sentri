# Sentri

## What is Sentri

Sentri is an AI security coprocessor backend. It evaluates financial transactions against a user's behavioral profile, computes deterministic deviation signals, and synthesizes human-readable explanations — acting as a second opinion layer before money moves.

## Quickstart

```bash
# Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install the package with dev dependencies
pip install -e ".[dev]"

# Copy environment template and set your API key (optional — see below)
cp .env.example .env

# Generate the seed dataset (10 personas, 100+ transactions each, cohort test cases)
python -m seeds.generator

# Run the tests
pytest

# Start the API
uvicorn sentri.api.main:app --reload
```

`ANTHROPIC_API_KEY` is optional. If it's unset, `/evaluate` still works end-to-end —
explanations are rendered by the deterministic template synthesizer
(`sentri/synthesizer/template.py`) instead of Claude. Set the key to get
LLM-synthesized explanations, with the template as an automatic fallback if
Claude's output ever fails validation (`sentri/synthesizer/validator.py`).

The server must be started from the `sentri-backend/` directory (or with it on
`PYTHONPATH`) — the default BMONI stub loads `seeds/data.json` relative to the
current working directory.

## Architecture

Sentri is organized into layered modules:

| Layer | Package | Role |
|-------|---------|------|
| Models | `sentri/models/` | Dataclasses — the type spine (`Transaction`, `UserProfile`, `DeviationVector`, `Verdict`) |
| Canonical | `sentri/canonical/` | Timestamp and numeric canonicalization |
| Graph | `sentri/graph/` | Profile builder and signal computation (familiarity, proximity) |
| Scorer | `sentri/scorer/` | Deterministic Tier 1 deviation scoring |
| Synthesizer | `sentri/synthesizer/` | Tier 2 LLM explanation synthesis |
| BMONI | `sentri/bmoni/` | Adapter interface and in-memory stub |
| API | `sentri/api/` | Thin FastAPI layer |

Configuration lives in `sentri/config.py`. Seed data for development is in `seeds/`.

For the full implementation plan, see the project architecture document in the repository root.

## Running tests

```bash
pytest
```

With coverage (optional):

```bash
pytest --cov=sentri
```

## Calling `/evaluate`

Request body is a `TransactionEvent` (see `sentri/models/transaction.py`). Two
examples against `user_001` from the seed dataset — start the server first
(`uvicorn sentri.api.main:app --reload`), then:

**A normal transaction** — a routine payment to a recipient the user pays
every month, at an amount and hour consistent with their history. Expect
`"kind": "silent_pass"` with no explanation:

```bash
curl -s -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "amount_kobo": 30000000,
    "timestamp": "2027-06-01T11:00:00+01:00",
    "recipient_id": "user_001_landlord",
    "currency": "NGN",
    "cross_border": false
  }' | python3 -m json.tool
```

**An anomalous transaction** — a large, cross-border payment in an unfamiliar
currency to a recipient the user has never paid, at an unusual hour. Expect
`"kind": "intervene"` with a populated `explanation` and `triggered_reasons`:

```bash
curl -s -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "amount_kobo": 500000000,
    "timestamp": "2027-06-01T03:00:00+01:00",
    "recipient_id": "user_001_advance_refund_agent",
    "currency": "USD",
    "cross_border": true
  }' | python3 -m json.tool
```

Both examples use a fixed `timestamp` roughly a year past the seed data's own
date range, rather than "now" — the amount-drift signal looks at the 90 days
*around the transaction's own timestamp*, so anchoring it past all seed
history keeps these examples deterministic regardless of which day you
actually run the `curl` command. Using today's real date in the `timestamp`
field instead is a legitimate way to call the endpoint, but the exact
`triggered_reasons` for a "normal" transaction can then vary with the
calendar date, since it lands inside the seed data's own noisy recent-history
window. See `tests/test_smoke.py` for the same two cases pinned this way.

Other endpoints:

- `GET /debug/health` — liveness check.
- `GET /debug/profile/{user_id}` — the `UserProfile` built from that user's
  history, as JSON. Both are feature-flagged via
  `config.DEBUG_ENDPOINTS_ENABLED` (default on for MVP; set the env var to
  `false` to 404 them).

## Swapping in the real BMONI client (hackathon day)

Every BMONI interaction goes through the `BMONIClient` Protocol in
[`sentri/bmoni/protocol.py`](sentri/bmoni/protocol.py):

```python
async def get_transaction_history(self, user_id: str) -> list[Transaction]: ...
async def get_social_graph(self, user_id: str) -> Optional[SocialGraph]: ...
async def log_decision(self, user_id: str, event_id: str, decision: str, explanation: Optional[str]) -> None: ...
async def on_transfer_intent_hook(self, callback: Any) -> None: ...
```

`sentri/bmoni/stub.py`'s `InMemoryBMONIStub` is the only class that currently
implements it, backed by `seeds/data.json`. To go live:

1. Write a new class in `sentri/bmoni/` (e.g. `sentri/bmoni/client.py`) that
   implements the same four methods against BMONI's real API — translating
   its responses into `Transaction` / `SocialGraph` objects
   (`sentri/models/transaction.py`, `sentri/models/profile.py`).
2. Point `get_bmoni_client()` in `sentri/api/deps.py` at the new class instead
   of `InMemoryBMONIStub`. That one factory is the sole call site — nothing
   else in `graph/`, `scorer/`, or `synthesizer/` references BMONI directly.
3. If BMONI's real data exposes different or additional fields than the seed
   schema assumes (e.g. richer recipient metadata), the only other place that
   may need adjusting is the `_build_facts()` helper in
   `sentri/api/evaluate.py` — it decides which values the synthesizer is
   allowed to restate.

No other file should need to change. See the final summary below for the
complete list.

test test