from kcos.risk.tail import TailRisk


def test_expected_shortfall_nonnegative_loss_measure():
    x = TailRisk().var_es([-0.1, -0.05, 0.01, 0.02, 0.03])
    assert x["expected_shortfall"] >= x["var"] or x["expected_shortfall"] >= 0
