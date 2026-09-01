from datetime import datetime,timezone
from .models import RiskDecision
class RiskKernel:
    def __init__(self,cfg): self.cfg=cfg
    def evaluate(self,intent,account,market_ts,emergency_stop=False,aggregate_open_risk_pct=0.0,venue_exposure_pct=0.0):
        now=datetime.now(timezone.utc)
        if emergency_stop and not intent.reduce_only:return RiskDecision(False,'emergency_stop')
        age=(now-market_ts).total_seconds()
        if age>self.cfg.max_decision_staleness_seconds and not intent.reduce_only:return RiskDecision(False,f'stale_market_state:{age:.2f}s')
        if intent.confidence<self.cfg.min_signal_confidence and not intent.reduce_only:return RiskDecision(False,'signal_confidence_below_floor')
        if account.equity<=0:return RiskDecision(False,'non_positive_equity')
        dd=max(0,(account.peak_equity-account.equity)/max(account.peak_equity,1e-9)*100)
        if dd>=self.cfg.hard_drawdown_stop_pct and not intent.reduce_only:return RiskDecision(False,f'hard_drawdown_stop:{dd:.2f}%')
        if account.daily_pnl<=-(self.cfg.max_daily_loss_pct/100)*account.equity and not intent.reduce_only:return RiskDecision(False,'daily_loss_breaker')
        if account.weekly_pnl<=-(self.cfg.max_weekly_loss_pct/100)*account.equity and not intent.reduce_only:return RiskDecision(False,'weekly_loss_breaker')
        if aggregate_open_risk_pct>=self.cfg.max_aggregate_open_risk_pct and not intent.reduce_only:return RiskDecision(False,'aggregate_open_risk_ceiling')
        if venue_exposure_pct>=self.cfg.max_venue_exposure_pct and not intent.reduce_only:return RiskDecision(False,'venue_exposure_ceiling')
        max_risk=account.equity*self.cfg.max_risk_per_trade_pct/100; stop_per=max(abs(intent.reference_price)*max(intent.stop_distance_pct,.0001)/100,1e-8); qty=min(abs(intent.qty),max_risk/stop_per,(account.equity*self.cfg.max_single_asset_notional_pct/100)/max(abs(intent.reference_price),1e-8)); projected=account.gross_exposure+qty*abs(intent.reference_price)
        if projected>account.equity*self.cfg.max_gross_leverage and not intent.reduce_only: qty=min(qty,max(0,account.equity*self.cfg.max_gross_leverage-account.gross_exposure)/max(abs(intent.reference_price),1e-8))
        if qty<=0:return RiskDecision(False,'size_or_leverage_ceiling')
        return RiskDecision(True,'approved',qty,qty*stop_per)
