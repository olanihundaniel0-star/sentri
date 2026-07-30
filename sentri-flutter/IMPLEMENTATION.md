# Sentri Flutter Implementation Summary

## What was built

A minimal, unstyled Flutter app that talks to the Sentri backend end-to-end, satisfying all non-negotiable constraints for the 30 Jul 3pm deadline.

## Non-negotiable constraints (verification)

### ✅ No client-side signing
- **Requirement**: No BMONI SDK calls from the device for anything that touches money. All transfer execution — including EIP-191/EIP-712 signing — stays on the backend via the server-held `eth_account` keypair.
- **Implementation**: Flutter is a pure HTTP client. Zero crypto libraries, zero signing code. Every transfer goes through `POST /transfer` → backend signs server-side → `POST /transfer/{id}/confirm` → backend submits to BMONI.
- **Verification**: Check `lib/api_client.dart` — only `http.get()` and `http.post()` calls. No `web3dart`, no `eth_sig_util`, no keypair generation.

### ✅ Sentri's check runs before BMONI
- **Requirement**: Sentri's check runs and completes before any transfer reaches BMONI. No code path where the app calls a BMONI transfer endpoint directly.
- **Implementation**: The backend's `POST /transfer` runs the full `evaluate()` pipeline (Tier 1 + Tier 2) internally before constructing any BMONI withdrawal proposal. If `should_intervene()` fires, the transfer is held without ever touching BMONI. Only `POST /transfer/{id}/confirm` or a silent-pass execute path actually call `bmoni_client.transfer()`.
- **Verification**: Check `sentri-backend/sentri/api/transfer.py` lines 126-135 — `evaluate()` is called first, and only if `verdict.kind == VerdictKind.INTERVENE` is the transfer held. Otherwise it executes via `_execute()` which calls the real `BMONIClient.transfer()`.

### ✅ No visual design work
- **Requirement**: Default Material widgets, default theme, zero custom tokens. This screen layer gets replaced once the design lands.
- **Implementation**: Every screen uses stock `Scaffold`, `AppBar`, `ListTile`, `TextFormField`, `ElevatedButton`, `OutlinedButton`. No custom `ThemeData`, no color overrides, no fonts, no animations.
- **Verification**: Check `lib/main.dart` — `ThemeData(useMaterial3: true)` with zero customization. Check any screen file — pure Material components with no styling beyond what Flutter defaults provide.

### ✅ Base URL lives in one config constant
- **Requirement**: Base URL for the backend lives in one config constant, so pointing it at Railway vs. localhost is a one-line change.
- **Implementation**: `lib/config.dart` exports `Config.baseUrl = 'http://localhost:8000'`. Change it to Railway's URL and rebuild.
- **Verification**: `lib/api_client.dart` constructor takes `baseUrl` defaulting to `Config.baseUrl`. Every HTTP call uses `this.baseUrl`.

## Screens / flows implemented

### 1. User select (`lib/screens/user_select_screen.dart`)
Hardcoded `ListView` of the two bridged demo users (`user_001`, `user_002`) from `Config.demoUsers`. Tap → navigate to transaction feed for that user.

### 2. Transaction feed (`lib/screens/transaction_feed_screen.dart`)
- On load: `GET /debug/profile/{user_id}` → parse `UserProfile` → flatten all `recipients[*].transactions` → sort by timestamp descending → display in `ListView`
- Pull-to-refresh re-fetches profile
- App bar send icon → navigate to send money screen
- If send completes, `Navigator.pop(context, true)` triggers a reload

### 3. Send money (`lib/screens/send_money_screen.dart`)
Form with:
- Recipient ID (`TextFormField`)
- Amount in naira (`TextFormField`, converted to kobo on submit via `* 100`)
- Memo (optional)

On submit:
- `POST /transfer` with `TransferRequest` body
- If `response.status == "held"`:
  - Show explanation + triggered reasons
  - Offer **Confirm Transfer** button → `POST /transfer/{id}/confirm`
  - Offer **Cancel** button → clears hold, back to form
- If `response.status == "executed"`:
  - Jump directly to result screen

### 4. Transfer result (`lib/screens/transfer_result_screen.dart`)
- Shows `response.status`, `explanation`, `triggered_reasons`
- If `bmoni_result` is present (real transfer executed), show the raw JSON
- **Back to Feed** button → pops with `true` flag to trigger feed reload

## API endpoints used

| Endpoint | Method | Purpose | Implementation |
|----------|--------|---------|----------------|
| `/debug/health` | GET | Health check | `api_client.dart` line 66, unused in UI |
| `/debug/profile/{user_id}` | GET | Fetch full transaction history + profile stats | `api_client.dart` line 18 |
| `/transfer` | POST | Submit transfer, get verdict (HELD or EXECUTED) | `api_client.dart` line 28 |
| `/transfer/{id}/confirm` | POST | Confirm a held transfer | `api_client.dart` line 54 |

## Models

### `Transaction` (`lib/models.dart`)
Maps backend's `Transaction` dataclass:
- `amountKobo: int`
- `timestamp: DateTime`
- `recipientId: String`
- `currency: String`
- `memo: String?`
- `displayAmount: String` — computed property that formats kobo as `₦1,234.56`

### `UserProfile` (`lib/models.dart`)
Maps backend's `UserProfile`:
- `userId: String`
- `recipients: Map<String, RecipientRollup>`
- `globalMeanKobo, globalStdKobo: double`
- `hourHistogram: List<int>`
- `currenciesSeen: List<String>`
- `allTransactions: List<Transaction>` — computed property that flattens all `recipients[*].transactions` and sorts by timestamp descending

### `TransferResponse` (`lib/models.dart`)
Maps backend's `TransferResponse`:
- `status: String` — "held" or "executed"
- `transferId: String?`
- `explanation: String?`
- `triggeredReasons: List<String>`
- `bmoniResult: Map<String, dynamic>?`
- `isHeld, isExecuted: bool` — computed properties

## Out of scope (as required)

- Visual design, animation, or branding
- Persistence beyond in-memory session state
- Error-state polish beyond "don't crash" (shows snackbars, retry buttons)
- Real auth — this is a hardcoded 2-user demo picker
- Any client-side transaction signing or BMONI SDK integration

## Testing checklist

1. **Start backend**: `cd sentri-backend && uvicorn sentri.api.main:app --reload`
2. **Verify bridged identities**: Check `seeds/identity_bridge.json` has real `bmoni_user_id` values for `user_001` and `user_002` (not `REPLACE_*` placeholders)
3. **Verify signing keys**: Env vars `BMONI_SIGNING_KEY__user_001` and `BMONI_SIGNING_KEY__user_002` are set
4. **Run Flutter**: `cd sentri-flutter && flutter run`
5. **Test silent pass** (user_002, normal cohort):
   - Select `user_002`
   - Tap send icon
   - Recipient: `user_002_colleague` (or any familiar recipient from their history)
   - Amount: `300.00` (normal range)
   - Submit → should jump directly to result screen with `status: executed`
6. **Test intervene** (user_001, anomalous cohort):
   - Select `user_001`
   - Tap send icon
   - Recipient: `user_001_advance_refund_agent` (unfamiliar)
   - Amount: `5000.00` (large)
   - Submit → should show explanation screen
   - Tap **Confirm Transfer** → result screen with BMONI response JSON
7. **Test cancel**:
   - Same as intervene test, but tap **Cancel** instead → back to form, nothing hits BMONI

## Files created

```
sentri-flutter/
├── README.md                                         Setup + usage instructions
├── IMPLEMENTATION.md                                 This file
├── pubspec.yaml                                      Flutter project config
├── analysis_options.yaml                             Linter config
├── .gitignore                                        Standard Flutter gitignore
├── lib/
│   ├── main.dart                                     App entrypoint
│   ├── config.dart                                   Backend URL + demo user list
│   ├── models.dart                                   Transaction, UserProfile, TransferResponse
│   ├── api_client.dart                               HTTP client for backend API
│   └── screens/
│       ├── user_select_screen.dart                   Hardcoded user picker
│       ├── transaction_feed_screen.dart              GET /debug/profile, show list
│       ├── send_money_screen.dart                    Form → POST /transfer → hold/confirm UI
│       └── transfer_result_screen.dart               Show final result
└── android/                                          Minimal Android platform config
    ├── build.gradle
    ├── settings.gradle
    ├── gradle.properties
    └── app/
        ├── build.gradle
        └── src/main/
            ├── AndroidManifest.xml
            ├── kotlin/.../MainActivity.kt
            └── res/values/styles.xml
```

## Next steps (design team handoff)

1. **Visual design drop-in**: Replace `lib/screens/*.dart` with styled versions. `lib/models.dart` and `lib/api_client.dart` stay untouched.
2. **Theme customization**: Edit `lib/main.dart` `ThemeData` to add brand colors, typography, etc.
3. **Navigation polish**: Consider a proper bottom nav bar, drawer, or tab bar instead of the current linear push/pop flow.
4. **Error handling**: Wrap API calls in better error UX (modals, retry logic, offline state).
5. **Loading states**: Add skeleton loaders, shimmers, or better progress indicators.
6. **Assets**: Add logo, custom icons, splash screen via `flutter_native_splash` and `flutter_launcher_icons`.
7. **iOS support**: Add `ios/` platform config (currently Android-only for minimal demo).

## Dependencies

- `http: ^1.1.0` — HTTP client for backend API
- `intl: ^0.19.0` — Date formatting in transaction feed
- `flutter_lints: ^3.0.0` — Linter rules (dev dependency)

Zero crypto libraries, zero native platform channels, zero custom UI packages.
