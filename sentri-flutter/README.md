# Sentri Flutter App

Minimal, unstyled Flutter app that talks to the Sentri backend end-to-end. Zero visual design work — default Material widgets, default theme. This screen layer gets replaced once the design lands.

## What it does

- **User select** — hardcoded picker for the two demo users from `identity_bridge.json` (`user_001`, `user_002`)
- **Transaction feed** — pulls real history via `GET /debug/profile/{user_id}` and displays it
- **Send money** — form (recipient, amount, memo) that drives the real backend flow:
  - Submit → `POST /transfer`
  - Silent pass → transfer executes immediately, show result
  - Intervene → show explanation text plus Confirm/Cancel buttons
  - Confirm → `POST /transfer/{id}/confirm`, then show result
  - Cancel → hold releases, nothing hits BMONI
- **Transfer result** — whatever the backend returns post-confirm/execute, enough to prove the round trip worked

## Non-negotiable constraints (met)

✅ No client-side signing. No BMONI SDK calls from the device. All transfer execution — including EIP-191/EIP-712 signing — stays on the backend via the server-held `eth_account` keypair.

✅ Sentri's check runs and completes before any transfer reaches BMONI. No code path where the app calls a BMONI endpoint directly — every transfer goes through the `evaluate → hold → confirm` sequence.

✅ No visual design work. Default Material widgets, default theme, zero custom tokens.

✅ Base URL for the backend lives in one config constant (`lib/config.dart`), so pointing it at Railway vs. localhost is a one-line change.

## Setup

### Prerequisites

- Flutter SDK 3.0.0 or later
- Backend running at `http://localhost:8000` (or change `lib/config.dart` to point at Railway)
- Backend must have `DEBUG_ENDPOINTS_ENABLED=true` (default) for `/debug/profile/{user_id}` to work
- At least one bridged identity (`user_001` or `user_002`) properly onboarded (see backend `scripts/bmoni_onboard.py`)

### Install dependencies

```bash
cd sentri-flutter
flutter pub get
```

### Configure backend URL

Edit `lib/config.dart` if your backend is not at `http://localhost:8000`:

```dart
class Config {
  static const String baseUrl = 'https://your-railway-app.railway.app';
  // ...
}
```

### Run

```bash
flutter run
```

Or open in VS Code / Android Studio and hit Run.

## File structure

```
lib/
├── main.dart                    App entrypoint, MaterialApp scaffold
├── config.dart                  Backend URL + demo user IDs (change URL here)
├── models.dart                  Transaction, UserProfile, TransferResponse
├── api_client.dart              HTTP client for /transfer, /debug/profile, /debug/health
└── screens/
    ├── user_select_screen.dart          Hardcoded picker for user_001 / user_002
    ├── transaction_feed_screen.dart     Pulls /debug/profile, shows transaction list
    ├── send_money_screen.dart           Form → POST /transfer, shows hold/confirm UI
    └── transfer_result_screen.dart      Shows final result (BMONI response, explanation)
```

## API endpoints used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/debug/health` | GET | Health check (unused in UI, here for completeness) |
| `/debug/profile/{user_id}` | GET | Fetch transaction history + profile stats |
| `/transfer` | POST | Submit transfer, get verdict (HELD or EXECUTED) |
| `/transfer/{id}/confirm` | POST | Confirm a held transfer |

## Testing the flow

1. **Select user** — tap `user_001` (anomalous cohort) or `user_002` (normal cohort)
2. **View feed** — scroll through historical transactions
3. **Tap send icon** (top-right) → fill form:
   - Recipient: e.g. `user_001_advance_refund_agent` (anomalous) or `user_001_landlord` (normal)
   - Amount: e.g. `5000.00` (large) or `300.00` (normal)
4. **Submit**:
   - If anomalous → explanation screen appears, tap **Confirm Transfer** or **Cancel**
   - If normal → immediately jumps to result screen
5. **Result screen** — shows BMONI response JSON (if executed), triggered reasons, explanation

## Out of scope

- Visual design, animation, branding
- Persistence beyond in-memory session state
- Error-state polish beyond "don't crash"
- Real auth — this is a hardcoded 2-user demo picker
- Any client-side transaction signing or BMONI SDK integration

## Notes

- The transaction feed pulls from `/debug/profile/{user_id}`, which aggregates the full `UserProfile` (all historical transactions across all recipients). The feed just flattens `profile.recipients[*].transactions` and sorts by timestamp descending.
- Amounts are entered as naira (decimal), converted to kobo (`* 100`) before sending to the backend.
- The `destination` field in `POST /transfer` is sent as an empty object (`{}`). For real Nigeria bank payouts, this would carry bank account details; for crypto, a wallet address. Since we're just testing the evaluation flow, an empty destination is fine.
