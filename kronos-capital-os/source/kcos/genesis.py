import getpass
import os
from pathlib import Path

RUNTIME = Path(".env.runtime")


def yn(prompt: str, default: bool = False) -> bool:
    value = input(prompt + (" [Y/n] " if default else " [y/N] ")).strip().lower()
    return default if not value else value in {"y", "yes"}


def secret(prompt: str) -> str:
    return getpass.getpass(prompt + ": ").strip()


def _serialize_env(values: dict[str, str]) -> str:
    lines = []
    for key, value in values.items():
        escaped = str(value).replace("\n", "\\n")
        lines.append(f"{key}={escaped}")
    return "\n".join(lines) + "\n"


def main() -> None:
    print("\nKRONOS CAPITAL OS — GENESIS v1.0 (PAPER PRODUCTION)\n")
    env = {
        "HEARTBEAT_SECONDS": "6",
        "MAX_DECISION_STALENESS_SECONDS": "6",
        "LIVE_TRADING_ENABLED": "false",
        "AUTO_GRADUATE_TO_LIVE": "false",
    }
    env["OWNER_JURISDICTION"] = input("Owner jurisdiction [US]: ").strip() or "US"
    env["BASE_CURRENCY"] = input("Base currency [USD]: ").strip() or "USD"
    env["INITIAL_CAPITAL"] = (
        input("Starting simulated capital [1000]: ").strip() or "1000"
    )

    ibkr = yn("Connect Interactive Brokers for account/market-data access?")
    env["IBKR_ENABLED"] = str(ibkr).lower()
    if ibkr:
        env["IBKR_ACCOUNT_ID"] = input("IBKR account ID: ").strip()
        env["IBKR_BASE_URL"] = (
            input("IBKR Web API base URL [https://localhost:5000/v1/api]: ").strip()
            or "https://localhost:5000/v1/api"
        )
        env["IBKR_BEARER_TOKEN"] = secret(
            "IBKR bearer/session token (blank if gateway manages auth)"
        )

    coinbase = yn("Connect Coinbase Advanced Trade for account/market-data access?")
    env["COINBASE_ENABLED"] = str(coinbase).lower()
    if coinbase:
        env["COINBASE_API_KEY_NAME"] = input("Coinbase CDP API key name: ").strip()
        env["COINBASE_API_PRIVATE_KEY"] = secret("Coinbase CDP private key")
        env["COINBASE_PORTFOLIO_ID"] = input("Coinbase portfolio ID: ").strip()

    oanda = yn("Connect OANDA for FX market-data/account access?")
    env["OANDA_ENABLED"] = str(oanda).lower()
    if oanda:
        env["OANDA_ACCOUNT_ID"] = input("OANDA account ID: ").strip()
        env["OANDA_ACCESS_TOKEN"] = secret("OANDA access token")

    env["DATABENTO_API_KEY"] = secret("Databento API key (recommended; blank to skip)")
    env["FRED_API_KEY"] = secret("FRED API key (blank to skip)")
    env["SEC_USER_AGENT"] = (
        input("SEC User-Agent [KCOS/1.0 owner@example.com]: ").strip()
        or "KCOS/1.0 owner@example.com"
    )

    if yn("Connect an optional reasoning-model endpoint for hypothesis generation?"):
        env["LLM_API_BASE"] = input("Reasoning API base URL: ").strip()
        env["LLM_MODEL"] = input("Model name: ").strip()
        env["LLM_API_KEY"] = secret("Reasoning API key")

    env["MAX_RISK_PER_TRADE_PCT"] = (
        input("Maximum simulated risk per trade % [0.50]: ").strip() or ".50"
    )
    env["MAX_AGGREGATE_OPEN_RISK_PCT"] = (
        input("Maximum simulated aggregate open risk % [2.00]: ").strip() or "2.00"
    )
    env["HARD_DRAWDOWN_STOP_PCT"] = (
        input("Hard simulated portfolio drawdown stop % [10]: ").strip() or "10"
    )

    defaults = {
        "ENVIRONMENT": "production-paper",
        "KCOS_INSTANCE_ID": "kcos-01",
        "DATABASE_URL": "postgresql://kcos:kcos@postgres:5432/kcos",
        "REDIS_URL": "redis://redis:6379/0",
        "KRONOS_ENABLED": "true",
        "KRONOS_MODEL": "NeoQuasar/Kronos-base",
        "KRONOS_TOKENIZER": "NeoQuasar/Kronos-Tokenizer-base",
        "KRONOS_DEVICE": "cpu",
        "MAX_DAILY_LOSS_PCT": "1",
        "MAX_WEEKLY_LOSS_PCT": "3",
        "MAX_GROSS_LEVERAGE": "1",
        "MAX_SINGLE_ASSET_NOTIONAL_PCT": "20",
        "MAX_VENUE_EXPOSURE_PCT": "50",
        "MIN_SIGNAL_CONFIDENCE": ".60",
        "SECRET_BACKEND": "env",
    }
    defaults.update(env)

    if ibkr and not env.get("IBKR_ACCOUNT_ID"):
        raise SystemExit("Genesis incomplete: IBKR account ID missing")
    if coinbase and not (
        env.get("COINBASE_API_KEY_NAME") and env.get("COINBASE_API_PRIVATE_KEY")
    ):
        raise SystemExit("Genesis incomplete: Coinbase credentials missing")
    if oanda and not (env.get("OANDA_ACCOUNT_ID") and env.get("OANDA_ACCESS_TOKEN")):
        raise SystemExit("Genesis incomplete: OANDA credentials missing")

    RUNTIME.write_text(_serialize_env(defaults), encoding="utf-8")
    os.chmod(RUNTIME, 0o600)
    print(
        "\nGENESIS COMPLETE\n"
        "✓ connector configuration captured\n"
        "✓ six-second freshness constitution installed\n"
        "✓ deterministic CRO/risk ceilings installed\n"
        "✓ strategy validation/promotion gates installed\n"
        "✓ PAPER execution enforced; live trading disabled\n"
        "✓ credential file restricted to owner permissions"
    )
    print("\nNext: make build && make start && make health")


if __name__ == "__main__":
    main()
