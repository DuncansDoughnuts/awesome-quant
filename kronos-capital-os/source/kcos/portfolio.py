from .models import OrderIntent


class PortfolioEngine:
    def intent_from_signal(self, signal, equity, mark):
        if mark <= 0 or signal.score == 0:
            return None
        notional = equity * min(0.10, max(0.0, signal.confidence) * 0.10)
        return OrderIntent(
            signal.strategy_id,
            signal.venue,
            signal.instrument,
            signal.asset_class,
            "BUY" if signal.score > 0 else "SELL",
            notional / mark,
            mark,
            2.0,
            signal.confidence,
        )
