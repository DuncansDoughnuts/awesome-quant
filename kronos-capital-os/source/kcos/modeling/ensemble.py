from ..domain import Forecast


class ForecastEnsemble:
    def __init__(self, weights=None):
        self.weights = weights or {
            "kronos": 0.4,
            "momentum": 0.2,
            "reversal": 0.1,
            "regime": 0.2,
            "cross_asset": 0.1,
        }

    def combine(self, instrument, horizon, components, calibration_haircut=1.0):
        total = weight = conf = 0.0
        for name, item in components.items():
            w = float(self.weights.get(name, 0))
            if not item or w <= 0:
                continue
            total += w * float(item.get("expected_return", 0))
            conf += w * float(item.get("confidence", 0.5))
            weight += w
        if weight == 0:
            return Forecast(instrument, horizon, 0, 0.5, 0, source="ensemble")
        er = total / weight
        c = max(0.01, min(0.99, conf / weight * calibration_haircut))
        dp = max(0.01, min(0.99, 0.5 + er * 10))
        return Forecast(
            instrument,
            horizon,
            er,
            dp,
            c,
            source="ensemble",
            metadata={"components": components},
        )
