class StressEngine:
    DEFAULT = {
        "equity_crash": {"EQUITY": -0.20, "ETF": -0.15, "CRYPTO": -0.30},
        "rates_shock": {"RATE": -0.08, "EQUITY": -0.08, "CRYPTO": -0.12},
        "crypto_crash": {"CRYPTO": -0.45},
    }

    def run(self, notional_by_asset, scenarios=None):
        out = {}
        for name, shocks in (scenarios or self.DEFAULT).items():
            out[name] = sum(
                float(notional_by_asset.get(a, 0)) * float(shock)
                for a, shock in shocks.items()
            )
        return out
