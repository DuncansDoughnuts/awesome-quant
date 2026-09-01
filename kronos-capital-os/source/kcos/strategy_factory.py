import hashlib
from dataclasses import dataclass,asdict
from .domain import StrategyRecord
@dataclass(slots=True)
class StrategySpec: strategy_id:str; hypothesis_id:str; universe:list[str]; asset_class:str; features:list[str]; entry_rules:list[str]; exit_rules:list[str]; max_holding_seconds:int=86400; stage:str='RESEARCH'; metadata:dict|None=None
class StrategyFactory:
    def from_hypothesis(self,hypothesis_id,subject,asset_class,features,venue='PAPER'):
        sid='STRAT-'+hashlib.sha1(f'{hypothesis_id}:{subject}:{asset_class}:{features}'.encode()).hexdigest()[:12].upper(); return StrategySpec(sid,hypothesis_id,[subject],asset_class,features,['ensemble_confidence >= minimum','expected_edge_after_costs > 0','regime_eligible == true'],['expected_edge_after_costs <= 0','risk_reduction_required == true','regime_eligible == false'],metadata={'venue':venue})
    def variants_from_hypothesis(self,hypothesis_id,subject,asset_class,venue='PAPER'):
        feature_sets=[['kronos','momentum','regime','cross_asset'],['kronos','reversal','reversal_primary','regime'],['momentum','cross_asset','regime','volatility']]; return [self.from_hypothesis(hypothesis_id+f'-{i}',subject,asset_class,features,venue) for i,features in enumerate(feature_sets,1)]
    def record(self,spec,metrics=None):
        d=asdict(spec); return StrategyRecord(spec.strategy_id,1,spec.stage,spec.asset_class,spec.universe,spec.hypothesis_id,d,metrics or {})
