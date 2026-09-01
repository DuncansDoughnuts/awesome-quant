import numpy as np

from kcos.portfolio_engine.optimizer import PortfolioOptimizer


def test_optimizer_sums_to_one():
    w = PortfolioOptimizer().risk_adjusted_weights(
        [0.1, 0.05], [[0.2, 0.01], [0.01, 0.1]], max_weight=0.8
    )
    assert abs(float(w.sum()) - 1) < 1e-8 and np.all(w >= 0)
