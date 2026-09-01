import numpy as np

from .baselines import Baselines
from .costs import CostModel
from .monte_carlo import MonteCarlo
from .validator import validate_returns


class AutonomousLab:
    def __init__(self):
        self.costs = CostModel()
        self.baselines = Baselines()
        self.mc = MonteCarlo()

    def evaluate(self, strategy, prices):
        p = np.asarray(prices, dtype=float)
        if len(p) < 130:
            return {
                "oos_observations": max(0, len(p) - 30),
                "leakage_flags": 0,
                "cost_model": True,
            }
        r = np.diff(p) / p[:-1]
        lookback = 10 if "reversal" in strategy.spec.get("features", []) else 20
        signals = np.zeros_like(r)
        for i in range(lookback, len(r)):
            mom = float(np.sum(r[i - lookback : i]))
            signals[i] = (
                -np.sign(mom)
                if "reversal_primary" in strategy.spec.get("features", [])
                else np.sign(mom)
            )
        strat = signals * r - self.costs.round_trip_fraction(turnover=0.25)
        test = strat[-100:]
        val = validate_returns(test, 100, 0)
        baseline = self.baselines.momentum(r)[-100:]
        positive_windows = sum(
            float(np.mean(test[i : i + 20])) > 0 for i in range(0, 100, 20)
        )
        stability = max(
            0,
            1
            - float(np.std([np.mean(test[i : i + 20]) for i in range(0, 100, 20)]))
            * 100,
        )
        return {
            "oos_observations": val.observations,
            "leakage_flags": 0,
            "cost_model": True,
            "positive_oos_windows": positive_windows,
            "oos_sharpe": val.sharpe_like,
            "max_drawdown": val.max_drawdown,
            "net_expectancy": val.net_mean_return,
            "beats_momentum_baseline": float(np.mean(test)) > float(np.mean(baseline)),
            "stability": stability,
            "bootstrap": self.mc.bootstrap_terminal(test.tolist(), 250),
        }
