from ..config import settings
from .ibkr import IbkrConnector
from .oanda import OandaConnector


def register_execution_connectors(router):
    if settings.ibkr_enabled and settings.ibkr_account_id:
        router.register(
            "IBKR",
            IbkrConnector(
                settings.ibkr_base_url,
                settings.ibkr_account_id,
                settings.ibkr_bearer_token,
                settings.ibkr_verify_tls,
            ),
        )
    if (
        settings.oanda_enabled
        and settings.oanda_account_id
        and settings.oanda_access_token
    ):
        router.register(
            "OANDA",
            OandaConnector(
                settings.oanda_base_url,
                settings.oanda_stream_url,
                settings.oanda_account_id,
                settings.oanda_access_token,
            ),
        )
    if (
        settings.coinbase_enabled
        and settings.coinbase_api_key_name
        and settings.coinbase_api_private_key
    ):
        try:
            from coinbase.rest import RESTClient

            from .coinbase import CoinbaseConnector

            router.register(
                "COINBASE",
                CoinbaseConnector(
                    RESTClient(
                        api_key=settings.coinbase_api_key_name,
                        api_secret=settings.coinbase_api_private_key,
                    )
                ),
            )
        except Exception:
            pass
    for a in ("EQUITY", "ETF", "OPTION", "FUTURE", "RATE", "COMMODITY", "INDEX"):
        router.map_asset_class(a, "IBKR")
    if "OANDA" in router.venues:
        router.map_asset_class("FX", "OANDA")
    elif "IBKR" in router.venues:
        router.map_asset_class("FX", "IBKR")
    if "COINBASE" in router.venues:
        router.map_asset_class("CRYPTO", "COINBASE")
    elif "IBKR" in router.venues:
        router.map_asset_class("CRYPTO", "IBKR")
    return router
