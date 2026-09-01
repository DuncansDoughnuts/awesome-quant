# Kronos Capital OS — Full Autonomous Quantitative Institution

**Canonical lineage: v1.0.0 — full system, not Genesis-only.**

Kronos Capital OS (KCOS) is a persistent, context-aware, cross-asset autonomous quantitative operating system built around the open-source Kronos financial foundation model. Genesis is only the onboarding/birth sequence.

## Full operating loop

`stream events → hot state → ≤6s world sync → trend/regime/market graph → bounded context + institutional memory → Kronos + independent models → alpha ensemble → curiosity/hypotheses → strategy factory → leakage/baseline/walk-forward/cost/robustness validation → alpha marketplace → autonomous CIO → portfolio construction → independent autonomous CRO → deterministic risk → venue execution → reconciliation → P&L attribution/drift → memory/model governance → repeat`

## Included system planes

- Genesis / secure connector onboarding
- continuous event ingestion and six-second maximum decision-state age
- Redis hot state + PostgreSQL durable institutional memory/audit
- bounded context compiler
- cross-asset correlation and lead/lag market graph
- multi-horizon trend mapping
- Kronos asynchronous inference service
- independent factor, volatility, regime and calibration models
- forecast ensemble and alpha fusion
- curiosity engine with hypothesis + counter-hypothesis generation
- multiple on-the-fly strategy variants
- leakage checks, baselines, walk-forward testing, transaction costs and Monte Carlo robustness
- strategy registry with deterministic `RESEARCH → WALK_FORWARD → PAPER → CANARY → LIVE → SCALED` gates
- alpha marketplace and autonomous CIO capital competition
- portfolio covariance/optimization/exposure/hedging modules
- independent autonomous CRO and deterministic risk kernel
- VaR/Expected Shortfall, stress and kill-switch layers
- paper execution plus IBKR, Coinbase and OANDA execution adapters
- Databento, FRED and SEC EDGAR data adapters
- order management, slippage and reconciliation
- treasury policy with no autonomous withdrawal authority by default
- P&L attribution, postmortems, drift detection and model governance
- Prometheus metrics, health/status/emergency APIs
- Docker Compose + systemd 24/7 deployment
- CI and security policy

## Required / recommended connections

Interactive Brokers for broad multi-asset execution; Coinbase Advanced Trade for crypto; Databento for primary live/historical market data; FRED for macro; SEC EDGAR for filings/XBRL; optional OANDA for dedicated FX; PostgreSQL + Redis internally; and a production secrets backend such as Vault/KMS/Secrets Manager.

## Six-second contract

`MAX_DECISION_STALENESS_SECONDS=6`

Market data is intended to stream continuously. Six seconds is the maximum age of a synchronized decision state, not a REST polling cadence. Stale critical state fails closed for new risk.

## Autonomy boundary

KCOS may improve strategies, features, model/ensemble weights, market-graph knowledge, research artifacts and gated execution algorithms. It may not self-relax raw credential permissions, absolute risk ceilings, validation authority, audit history, emergency-stop semantics, or withdrawal/transfer authority.

## Contributors

- [@sheldonibm](https://github.com/sheldonibm)
- [@sheldonos](https://github.com/sheldonos)

## Important

The earlier `Genesis v0.1` archive was an incomplete foundation build and is deprecated. The canonical project lineage is now the full v1.0 system described above. KCOS does not claim a pre-proven profitable strategy; live capital eligibility depends on actual evidence produced by the validation pipeline. Automated trading can lose capital.