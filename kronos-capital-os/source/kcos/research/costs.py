class CostModel:
    def __init__(self,commission_bps=.5,spread_bps=1.0,slippage_bps=1.0): self.commission_bps=commission_bps; self.spread_bps=spread_bps; self.slippage_bps=slippage_bps
    def round_trip_fraction(self,turnover=1.0): return turnover*(self.commission_bps*2+self.spread_bps+self.slippage_bps*2)/10000.0
