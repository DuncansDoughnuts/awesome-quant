from kcos.domain import StrategyStage
from kcos.research.promotion import PromotionEngine


def test_sequential_promotion():
    p = PromotionEngine()
    assert (
        p.next_stage("RESEARCH", {"leakage_flags": 0, "oos_observations": 100})
        == StrategyStage.WALK_FORWARD
    )
    assert (
        p.next_stage("RESEARCH", {"leakage_flags": 0, "oos_observations": 20})
        == StrategyStage.RESEARCH
    )
