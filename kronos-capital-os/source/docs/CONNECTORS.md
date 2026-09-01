# Connectors

Verified against official provider documentation on 2026-09-01.

## Required for the recommended build

### Interactive Brokers
Broad execution for entitled equities/options/futures/FX and account state.

Genesis inputs:
- account ID
- authentication/session setup
- Web API base URL
- market-data entitlements

KCOS must maintain an authenticated brokerage session for `/iserver` trading functions.
IBKR WebSocket market-data subscriptions require proactive renewal; the runtime watchdog should renew well before the documented expiration window.

Docs:
- https://www.interactivebrokers.com/docs/web-api/authentication/sessions
- https://www.interactivebrokers.com/docs/web-api/v1/ws/market-data/market-data-request
- https://www.interactivebrokers.com/docs/web-api/authentication/oauth-2/introduction

### Coinbase Advanced Trade
Crypto execution.

Genesis inputs:
- CDP API key name
- CDP private key
- portfolio ID

Recommended key permissions: view, trade, and do NOT enable transfer/withdrawal for ordinary trading. Use IP allowlisting.

Docs:
- https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/rest-api
- https://docs.cdp.coinbase.com/api-reference/authentication

### Databento
Preferred streaming/historical market data. Genesis input: `DATABENTO_API_KEY`. Use streaming subscriptions for the real-time path, plus intraday replay after disconnections.

Docs:
- https://databento.com/docs/api-reference-live
- https://databento.com/docs/getting-started/build-first-app

### FRED
Macro data. Genesis input: `FRED_API_KEY`.

### SEC EDGAR
Public submissions/XBRL APIs require no API key. Supply a declared User-Agent.

### OANDA v20
Optional dedicated FX venue. Inputs: account ID + personal access token.

## Internal infrastructure connectors
- PostgreSQL: durable memory, audit, strategy/hypothesis lineage
- Redis: hot state, connector health, six-second cycle state
- Vault/KMS/Secrets Manager: production secrets
- alert webhook/email: owner exception notifications

## Treasury
Prefer `owner bank → approved funding rail → broker/exchange → trading-only API key`. Do not expose unrestricted bank credentials or withdrawal keys to research/strategy agents.
