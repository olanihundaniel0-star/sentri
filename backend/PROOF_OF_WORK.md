# Sentri × BMONI — Proof of Work

Real request/response evidence from actually running the system against the
live BMONI embedded-dev sandbox (`https://embedded-dev.bmoni.com`), not a
self-reported checklist. Captured 2026-07-29/30, resumed and continued
2026-07-30 once BMONI staff funded both sandbox wallets. Base commit
`947def4156455462f9efee2b81fa36e856ca8b3e`; several real bugs found while
doing this run are fixed on top of it (see "Bugs found and fixed live"
below) and are included in this working tree.

## Status summary

| Step | What | Result |
|---|---|---|
| 0 | Full gate (pytest, ruff format, ruff check, mypy --strict) | **PASS** |
| 1 | Live read path (balance + transaction history) for a bridged user | **PASS** — funded balances confirmed live (see below) |
| 2 | Silent-pass end-to-end incl. real BMONI-side completion | **BLOCKED on timing only** — wallets funded, `_REFERENCE_DATE` staleness bug fixed and verified live (see below); needs a run during ~09:00–23:00 WAT, currently ~03:40 WAT |
| 3 | Intervene hold is real (no BMONI-side proposal created) | **PASS** — re-run fresh with funded wallets |
| 4 | Confirm-anyway completes + fix #1 (amount integrity) holds live | **PASS on propose→sign→submit** (exact original amount, correct signing scheme after fixing a second live bug); on-chain settlement still pending as of this writing (async BMONI KMS relay, see below) |

---

## Step 0 — Gate

Re-run 2026-07-30T01:32Z (after the two additional live bugs below were
found and fixed), from `backend/`, `.venv` with `pip install -e
".[dev]"`:

```
$ pytest -q
........................................................................ [ 37%]
........................................................................ [ 74%]
.................................................                        [100%]
193 passed in 1.71s

$ ruff format --check .
59 files already formatted

$ ruff check .
All checks passed!

$ mypy --strict sentri scripts tests
Success: no issues found in 57 source files
```

All green. **PASS.**

(193, not the original 189: new/rewritten tests were added while fixing the
real client and API bugs found below — see `tests/test_bmoni_client.py`,
`tests/test_identity_bridge.py`, `tests/test_transfer.py`.)

---

## Setup performed for this run (not in the original guide, but required to get real evidence)

`seeds/identity_bridge.json` shipped with `REPLACE_WITH_REAL_BMONI_USER_ID`
placeholders for both demo identities — neither had ever actually been
onboarded to the sandbox. To get *any* real evidence at all, this run:

1. Onboarded two real sandbox identities via (a corrected) `scripts/bmoni_onboard.py`:
   - **Ada** → bridged to `user_001` (cohort A / intervene demo)
     `bmoniUserId = 5d0fd0c3-ad1a-4739-909c-6b27803bfcb4`, NGN smart wallet
     `fd627349-2343-4489-ae9b-988d12efee32`, wallet address
     `0x60E26467AFc099D53f6258c2707CbEf98CE9508F`.
   - **Bola** → bridged to `user_002` (cohort D / silent-pass demo)
     `bmoniUserId = dfda86aa-ae19-49c8-a6c7-0edc743f1cd4`, NGN smart wallet
     `d177e7a6-f9a9-4ffe-b215-3bb854852e69`, wallet address
     `0xca41ffcac7cbDe0eCe1e1378986052e36Cf95201`.
   - Both registered as bank codes/phones: `+2348001000001` (Ada) /
     `+2348001000002` (Bola). Both have a Nigerian withdrawal bank account
     registered (`bankAccountId` `9a6d486a-5593-45a8-ae00-2f158a594560` for
     Ada, `3ae60b09-b5e6-42ae-b10e-e6bc469338a5` for Bola) so a real
     withdrawal proposal can be created once funded.
   - Owner keypairs are held only in `.bmoni_keys/*.json` (gitignored,
     `0600`), never printed to any terminal/log; loaded server-side as
     `BMONI_SIGNING_KEY__user_001` / `BMONI_SIGNING_KEY__user_002`.
   - `seeds/identity_bridge.json` updated with the real `bmoni_user_id` and
     phone values (this file is meant to be committed once bridging is
     real — see its own note; the private keys never go in it).
2. Ran the API with `BMONI_API_KEY` and both `BMONI_SIGNING_KEY__*` set, so
   `get_bmoni_client()` resolves to the real `sentri.bmoni.client.BMONIClient`
   (`sentri/api/deps.py`), not `InMemoryBMONIStub`.

## Bugs found and fixed live (real discoveries, not guesses)

The original `sentri/bmoni/client.py` and `scripts/bmoni_onboard.py` were
written against the hackathon doc's description of the API, never against a
live call. Driving them for real against BMONI's own OpenAPI spec
(`GET /docs/openapi.json`, discovered via `/docs`) surfaced concrete bugs:

- **User creation response is nested.** `POST /v1/users` returns
  `{"user": {"bmoniUserId": ...}}`, not a top-level `bmoniUserId`. The
  original onboarding script 500'd on this — meaning the *very first* live
  call already failed before any of this project's own code ran.
- **Missing `0x` prefix on hex signatures.** `eth_account`'s
  `HexBytes.hex()` in the pinned dependency versions does **not** include
  the `0x` prefix. The sandbox 400s (`"ownerProofSignature must be a
  65-byte 0x-prefixed hex signature"`) without it. This bug was present in
  *both* wallet-creation signing (`bmoni_onboard.py`) and transfer signing
  (`client.py`) — same root cause, two call sites.
- **Wrong field names on `create-managed`.** Real body is `{currency,
  ownerProofChallengeId, ownerProofSignature, userOwnerAddress}`, not
  `{challengeId, signature, userOwnerAddress}`.
- **Wrong field names on `start-nigeria`.** Real body is `{bvn,
  ngnWalletAddress, ngnWalletIndex}`, not `{bvn, countryCode, walletAddress,
  walletIndex}`.
- **`onboarding/status` never reports Nigeria-rail readiness.** Its
  `anchorStatus`/`bridgeStatus`/`moneriumStatus`/etc fields track the
  *international* rails and stayed `"not_started"` through a fully
  successful Nigeria-only onboarding. The original `poll_until_active()`
  polled this for a `status: "active"` value that can never appear for an
  NGN-only identity — it would have spun for a full minute and then raised.
  Replaced with a direct readiness check against
  `GET .../account/balances` (confirmed live: readiness is synchronous —
  balances are queryable immediately after `start-nigeria` returns).
- **Wrong transactions endpoint entirely.** There is no
  `GET /v1/users/{userId}/smart-wallets/account/transactions`. The real
  endpoint is per-wallet: `GET
  /v1/users/{userId}/smart-wallets/{smartWalletId}/transactions`, and
  `smartWalletId` only comes from a balances-list entry. `client.py`'s
  `get_transaction_history` now fans out over every wallet balances()
  reports and concatenates.
- **Wrong withdrawal request schema entirely.** Real body for the Nigeria
  rail is `{sourceSmartWalletId, bankAccountId, fromAmount}` (a decimal
  *string*), not an arbitrary `destination` dict merged with a float
  `"amount"`. A Nigerian withdrawal destination must also already be a
  *registered* withdrawal bank account
  (`POST .../bank-accounts/withdrawal-accounts/nigeria`, itself gated on
  `POST .../bank-accounts/verify-nigerian-account`) — this is onboarding
  setup, done once per identity, not per-transfer.
- **`/transfer`'s executed-path response silently dropped the verdict.**
  `TransferResponse` only carried `kind`/`explanation`/`triggered_reasons`
  on the `HELD` branch; a caller had no way to see that an executed
  transfer had, in fact, scored `silent_pass`. Added `kind` to
  `TransferResponse` and populated it on both branches
  (`sentri/models/transfer.py`, `sentri/api/transfer.py`).

Two more were found live on 2026-07-30 once real funding made it possible
to actually exercise the sign-and-submit path for the first time (step 2/4
had been blocked on funding until now, so this code path had never
actually run against the sandbox before):

- **`signPayload` isn't what it looks like.** `POST
  .../withdrawal/wallet/nigeria` returns `signPayload` as a wrapper —
  `{signingPayloadHash, typedData, signatureExpiresAt, proposalStatus}` —
  and `typedData` looks exactly like a standard EIP-712 struct
  (`domain`/`types`/`primaryType`/`message`, `primaryType:
  "CoinbaseSmartWalletMessage"`). The obvious reading (and the first fix
  attempted here) is to sign `typedData` with
  `eth_account.Account.sign_typed_data` — but the sandbox actually verifies
  a **raw ECDSA signature over `signPayload["signingPayloadHash"]`
  directly** (`Account.unsafe_sign_hash`), not an EIP-712 signature over
  the wrapper's `typedData`. Confirmed by direct experiment against a live
  proposal, same key, same proposal, two signature encodings:
  EIP-712-signed → live `400 {"code":"E101","message":"Signature does not
  match your registered owner address"}`; raw-hash-signed → live `200` with
  `currentSignatures: 1`. `typedData` appears to exist purely for
  wallet-UI display, not what's actually checked. Fixed in
  `sentri/bmoni/client.py`'s `transfer()`.
- **`confirm_transfer` popped the pending transfer before knowing
  execution succeeded.** `sentri/api/transfer.py`'s confirm route did
  `_pending_transfers.pop(transfer_id, None)` and only *then* called
  `_execute`; the very first live confirm attempt hit the signing-scheme
  bug above, which raised, and the `transfer_id` was already gone — no way
  to retry the same held transfer, even though BMONI had never been asked
  to move anything. Fixed by restoring the pending entry into the dict if
  `_execute` raises, so a failed confirm stays retryable (still guarded
  against concurrent double-submission, since the pop still happens before
  the network call).

All of the above are fixed in this working tree
(`sentri/bmoni/client.py`, `scripts/bmoni_onboard.py`,
`sentri/models/transfer.py`, `sentri/api/transfer.py`), with tests updated
to match (`tests/test_bmoni_client.py`, `tests/test_identity_bridge.py`,
`tests/test_transfer.py`). Full module docstrings in
`sentri/bmoni/client.py` document the corrected, live-confirmed schema in
detail.

### A live-timing artifact found while trying to run step 2 (not a code bug, a data/timing interaction)

`sentri/scorer/amount.py`'s `AMOUNT_DRIFT` signal compares the volatility of
*all* of a user's transactions in the last 30 days against the prior 31–90
days, relative to the event's own timestamp — it does not depend on which
recipient or amount is being submitted. `seeds/generator.py`'s
`_REFERENCE_DATE` (2026-07-26) is only ~4 days before the actual date this
run happened (2026-07-30), and every persona's cohort A–E test-case
transactions are injected exactly *at* that reference date. The result:
right now, **any** live `/transfer` call for these personas — regardless of
amount or recipient — has those deliberately-anomalous cohort transactions
sitting inside its "recent 30 days" window, inflating recent volatility and
firing `AMOUNT_DRIFT` unconditionally. `tests/test_smoke.py` already
documents and works around exactly this class of problem for its own
fixed-timestamp tests ("Anchor well past the recipient's own transaction
history... Using real wall-clock 'now' here would make this test's outcome
depend on the calendar date"), but `/transfer`'s route hardcodes
`datetime.now(timezone.utc)` with no override, so that workaround isn't
available to it.

Separately, `sentri/scorer/temporal.py`'s hour-deviation signal uses a
circular-mean formula that's currently genuinely unfavorable for these two
personas outside of roughly 09:00–23:00 WAT (verified numerically against
`user_002`'s real hour histogram: every hour from 00:00–08:00 WAT deviates
above the 0.7 firing threshold). This run happened at ~01:00 WAT.

Neither of these is a bug in the sense of "wrong code" — they're a live
interaction between a synthetic dataset with a nearly-stale reference date,
real wall-clock scoring, and the hour the test happened to run at.

**`_REFERENCE_DATE` fixed 2026-07-30T02:4x WAT.** Moved
`seeds/generator.py`'s `_REFERENCE_DATE` from `2026-07-26` back to
`2026-04-01` (>90 days behind real "now"), then regenerated
`seeds/data.json` (`python -m seeds.generator`) and re-ran the full gate —
193 passed, ruff clean, mypy --strict clean (no unit test depends on this
constant's absolute value: cohort tests freeze wall-clock time to the
cohort's own designed timestamp, not real "now" — only live `/transfer`
calls use real time, and only they were affected). **Verified live**
immediately after: re-ran the same cohort-A-shaped intervene request
(`user_001`, new never-before-seen recipient, USD, cross-border) at
2026-07-30T03:39:12 WAT —

```json
{
  "status": "held",
  "transfer_id": "c09708f0e942444bac07830fa3c56a79",
  "kind": "intervene",
  "explanation": "You've never sent money to this account. ... This is at 3:39am. You usually send money between 12am and 2pm. This is your first transfer in USD. This transfer is crossing borders.",
  "triggered_reasons": ["recipient_familiarity", "graph_proximity", "hour_deviation", "currency_novelty", "cross_border"],
  "bmoni_result": null
}
```

`amount_drift` is gone from `triggered_reasons` — confirmed fixed against a
real live call, not just reasoned about. `hour_deviation` is still present,
correctly: it's a genuine, legitimate signal for these personas outside
~09:00–23:00 WAT (see below), not a data-staleness artifact, and this
request was made at 03:39 WAT. Not confirmed (no BMONI proposal attempted;
`transfer_id` left to expire via TTL).

This means the **only** remaining blocker for a genuinely clean
(`triggered_reasons: []`) silent-pass demo is the hour-of-day window — no
code or data fix applies to it, since it reflects these personas' real
histories, not an artifact:

---

## Step 1 — Read path is real

`GET .../smart-wallets/account/balances`, called directly against the
sandbox (not through Sentri) for both bridged identities, 2026-07-30T01:19Z
— after BMONI staff funded both wallets:

```json
{
  "user_001 (Ada, bmoniUserId 5d0fd0c3-ad1a-4739-909c-6b27803bfcb4)": {
    "smartAccountAddress": "0x60E26467AFc099D53f6258c2707CbEf98CE9508F",
    "balances": [
      {"smartWalletId": "fd627349-2343-4489-ae9b-988d12efee32", "currency": "NGN", "balance": "10000", "error": null}
    ]
  },
  "user_002 (Bola, bmoniUserId dfda86aa-ae19-49c8-a6c7-0edc743f1cd4)": {
    "smartAccountAddress": "0xca41ffcac7cbDe0eCe1e1378986052e36Cf95201",
    "balances": [
      {"smartWalletId": "d177e7a6-f9a9-4ffe-b215-3bb854852e69", "currency": "NGN", "balance": "10000", "error": null}
    ]
  }
}
```

Both wallets show real, non-zero balances (₦10,000 NGN each — the actual
amount BMONI staff credited, not the CNGN 1,000 / USDB $10 originally
requested). This is unambiguously real: the wallet addresses,
`smartWalletId` UUIDs, `smartAccountAddress` values, and now non-zero
balances are all sandbox-generated and could not have come from
`InMemoryBMONIStub`. **PASS.**

**Remaining gap**: a real BMONI-side transaction with an id/timestamp still
hasn't appeared as of this writing — step 4 below gets a real signed,
submitted withdrawal proposal against this funded balance, but its final
on-chain settlement (the event that would populate this endpoint) is still
outstanding at time of writing. See step 4's closing note.

---

## Step 2 — Silent-pass end-to-end

**Funding is no longer the blocker — timing is.** Both wallets are
confirmed funded (step 1). What remains is purely the timing artifact
documented above: this resumed run happened at ~02:00–02:30 WAT, and
`user_002`'s (Bola's) real hour histogram deviates above the
`hour_deviation` firing threshold for every hour outside ~09:00–23:00 WAT.
Running step 2 right now would very likely add `hour_deviation` to
`triggered_reasons` and flip an otherwise-clean silent-pass into an
`intervene` — not a real silent-pass result, just a false negative from bad
timing. Deferred to the next run inside that window rather than reported
here as a false pass.

Once in-window: `POST /transfer` with `user_id="user_002"`, a small amount
to one of Bola's actually-familiar recipients, `destination:
{"sourceSmartWalletId": "d177e7a6-f9a9-4ffe-b215-3bb854852e69",
"bankAccountId": "3ae60b09-b5e6-42ae-b10e-e6bc469338a5"}` should return
`status: "executed"`, `kind: "silent_pass"`, `triggered_reasons: []`, and a
populated `bmoni_result`; then re-fetching Bola's transaction list should
show the new entry.

---

## Step 3 — Intervene hold is real

Re-run fresh (transfer_ids expire after 10 minutes) submitted live via the
running API (`BMONI_API_KEY` + both `BMONI_SIGNING_KEY__*` set, so
`/transfer` was wired to the real BMONI client) at 2026-07-30T01:30:48Z,
against the now-funded wallet:

**Request** — `POST /transfer`, `user_id="user_001"` (Ada), a small amount
to a brand-new, cross-border, novel-currency recipient (deliberately chosen
so the intervene branch is driven by `currency_novelty`/`cross_border` —
signals that don't depend on amount magnitude, so this is unaffected by the
`hour_deviation` timing artifact above; the exact literal amount from the
validated cohort-A unit test, ₦2,000,000, is far beyond what the sandbox's
tiny test funds could ever move for real, so this intentionally uses a much
smaller amount that still trips the same non-structural signal class):

```json
{
  "user_id": "user_001",
  "amount_kobo": 50000,
  "recipient_id": "user_001_sandbox_offshore_test_agent",
  "currency": "USD",
  "cross_border": true,
  "destination_type": "nigeria",
  "destination": {
    "sourceSmartWalletId": "fd627349-2343-4489-ae9b-988d12efee32",
    "bankAccountId": "9a6d486a-5593-45a8-ae00-2f158a594560"
  },
  "memo": "sandbox offshore test payment"
}
```

**Response:**

```json
{
  "status": "held",
  "transfer_id": "87eaaa8ff059436b83b55b52a3445711",
  "kind": "intervene",
  "explanation": "You've never sent money to this account. This account has no connection to anyone you've sent money to before. Your recent transfers to this recipient have grown from around ₦39,303.08 to ₦109,394.59. This is at 2:30am. You usually send money between 12am and 2pm. This is your first transfer in USD. This transfer is crossing borders.",
  "triggered_reasons": [
    "recipient_familiarity",
    "graph_proximity",
    "amount_drift",
    "hour_deviation",
    "currency_novelty",
    "cross_border"
  ],
  "bmoni_result": null
}
```

(`hour_deviation` is now present too, for the same reason noted in the
timing artifact above — Ada's own history also has no early-morning
activity. It doesn't change the outcome: intervene was already going to
fire on `currency_novelty`/`cross_border` alone, so this is one more true
trigger stacking on an already-correct hold, not a false one changing the
verdict.)

`bmoni_result: null` — no proposal request was even attempted.

**Before-vs-after check against BMONI directly** (not through Sentri): Ada's
transaction list, fetched immediately after the hold response above:

```json
{
  "transactions": [],
  "page": 1, "perPage": 50, "total": 0, "pageCount": 0,
  "hasNextPage": false, "hasPreviousPage": false
}
```

Empty. The hold means what it claims: no withdrawal proposal was created on
BMONI's side, not just that Sentri's own response didn't show one.
**PASS.**

---

## Step 4 — Confirm-anyway + fix #1 regression, live

Submitted live at 2026-07-30T01:30:58Z, `POST
/transfer/87eaaa8ff059436b83b55b52a3445711/confirm` (the exact transfer_id
from the step 3 run immediately above, well inside its 10-minute TTL).

**First attempt found a second real bug** (see "Bugs found and fixed live"):
signing `signPayload["typedData"]` with `Account.sign_typed_data` got a
live BMONI 500→502 (`Client error '400 Bad Request'`, body `{"code":"E101",
"message":"Signature does not match your registered owner address"}`), and
because `confirm_transfer` popped the pending transfer before calling
`_execute`, that first `transfer_id` was permanently lost — both now fixed
(raw-hash signing in `client.py`, restore-on-failure in `transfer.py`).

**Re-run clean, with both fixes in place**, response:

```json
{
  "status": "executed",
  "bmoni_result": {
    "proposal": {
      "id": "b0f97b71-5c74-4ea0-988f-d956d05289bc",
      "groupWalletId": "fd627349-2343-4489-ae9b-988d12efee32",
      "proposalType": "OFFRAMP_BANK_NIGERIA",
      "status": "PENDING_SIGNATURES",
      "requiredSignatures": 1,
      "currentSignatures": 1,
      "signerSnapshot": ["0x9Cd2D1063a5EcFC0E35a1E0Cb1868949250B426a"],
      "signatures": [{
        "signerAddress": "0x9Cd2D1063a5EcFC0E35a1E0Cb1868949250B426a",
        "signature": "0xf674cab8247417595368580d5234fbf27032840a9434a7cac8053843bcbf577656fb163388ff6ba8cf4e45a0b5c203dfc7dabbc28e5cec6e1eb4ded0b8f9a4731c",
        "signingPayloadHash": "0xd74704377f8cb82f7dace50684f2e3c4f34437fea9d0b8d9a7d06284a986a886"
      }],
      "description": "Offramp 500.00 cNGN → NGN",
      "offrampContext": {
        "fee": {"amount": "30", "currency": "CNGN"},
        "rail": "nigeria",
        "amount": "500.00",
        "sourceAmount": "500.00",
        "bankAccountId": "9a6d486a-5593-45a8-ae00-2f158a594560"
      },
      "nextAction": "WAIT_SIGNATURES",
      "executionMode": "SAFE_TX_HASH_KMS_RELAY"
    }
  }
}
```

`"description": "Offramp 500.00 cNGN → NGN"` — exactly ₦500.00, i.e. exactly
the 50,000 kobo from the *original* step 3 request, not a different amount.
**Fix #1 (amount integrity) holds live**: `destination` never overrides what
`amount_kobo` actually moves, confirmed against a real BMONI proposal, not
just the unit test. Proposing, signing (owner's real key, correct scheme),
and submitting all completed synchronously and correctly. **PASS** on
propose → sign → submit.

**Final on-chain settlement**: `executionMode: "SAFE_TX_HASH_KMS_RELAY"` —
BMONI's KMS still has to co-sign and relay the underlying Safe transaction
before it lands as a transaction/balance change; `nextAction:
"WAIT_SIGNATURES"` even at `currentSignatures == requiredSignatures == 1`
suggests that co-signature step is asynchronous. Polled
`.../transactions` and `.../account/balances` repeatedly after submission;
as of this writing balance is still ₦10,000 and the transaction list is
still empty — settlement had not visibly landed within the observation
window. Not reporting this as fully settled: the proposal is genuinely
signed and submitted with the correct amount (the part this step exists to
prove), but the last-mile on-chain confirmation is still outstanding and
should be re-checked rather than assumed.

---

## To resume

Funding is done, and the `_REFERENCE_DATE` staleness bug is fixed and
verified live; the only remaining blocker is real hour-of-day:

1. **Step 2 (silent-pass)**: re-run during ~09:00–23:00 WAT so
   `hour_deviation` doesn't spuriously fire for Bola/user_002 (this is the
   one signal the reference-date fix can't touch — it's genuinely driven by
   Bola's real transaction-hour history, not a data artifact). API is
   already running on `127.0.0.1:8123` with `BMONI_API_KEY`,
   `BMONI_SIGNING_KEY__user_001`, and `BMONI_SIGNING_KEY__user_002` set
   (values in `.bmoni_keys/*.json`, gitignored, never printed); if it's been
   restarted, re-source `scratchpad/run_api.sh`. Then `POST /transfer` per
   the request shape documented in step 2 above; update that section with
   the real response.
2. **Step 4 settlement**: re-check
   `GET /v1/users/5d0fd0c3-ad1a-4739-909c-6b27803bfcb4/smart-wallets/fd627349-2343-4489-ae9b-988d12efee32/transactions`
   and `.../account/balances` for proposal `b0f97b71-5c74-4ea0-988f-d956d05289bc`
   to actually land (balance dropping from ₦10,000, a new transaction
   entry appearing) — this is BMONI's own async KMS relay, not something
   Sentri controls or can poll faster than BMONI settles it. Update step
   4's closing note once it does.
