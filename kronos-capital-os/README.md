# Kronos Capital OS — Genesis

Autonomous, context-aware, cross-asset quantitative operating system built around the open-source
Kronos financial K-line foundation model.

**Upstream:** https://github.com/shiyu-coder/Kronos  
**Pinned commit:** `67b630e67f6a18c9e9be918d9b4337c960db1e9a`

## Core loop

`observe → map → retrieve context → detect regime → forecast → generate hypotheses → validate →
allocate → deterministic risk gate → execute → reconcile → attribute → learn`

The owner completes **Genesis** once by supplying account-specific information and API credentials.
Routine operation is autonomous after deployment. Provider-required MFA, KYC, reauthorization,
credential expiry, or legal/account actions remain owner exception events.

## Six-second operating contract

`MAX_DECISION_STALENESS_SECONDS=6`

Market feeds should stream continuously. Every six seconds at the latest KCOS performs a full
synchronization/decision cycle. Material events can trigger evaluation immediately.

If critical market/account state is older than six seconds, **new risk is forbidden** until state
is synchronized again.

## Developmental states

`NEWBORN → OBSERVER → RESEARCHER → PAPER → CANARY → LIVE → SCALED`

Promotion is evidence-based. Strategy-generation systems cannot skip gates.

## Start

```bash
cp .env.example .env
make bootstrap
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,marketdata]"
make genesis
make build
make start
make health
```

See the source package inside `Kronos_Capital_OS_Genesis_v0.1.zip` for connector, architecture, Genesis, and 24/7 deployment documentation.

## Project contributors

- [@sheldonibm](https://github.com/sheldonibm)
- [@sheldonos](https://github.com/sheldonos)

## Recommended initial connectors

- Interactive Brokers — broad execution
- Coinbase Advanced Trade — crypto execution
- Databento — live/historical market data
- FRED — macro data
- SEC EDGAR — public filings/XBRL, no API key required
- Optional OANDA — dedicated FX
- PostgreSQL — durable memory/audit/strategy lineage
- Redis — hot state/event bus
- Vault/KMS/Secrets Manager — production secrets
- 24/7 Linux/Docker host

Do not give strategy/reasoning agents unrestricted bank or withdrawal credentials.

This is an engineering foundation, not a guarantee of returns. Automated trading can lose money.
