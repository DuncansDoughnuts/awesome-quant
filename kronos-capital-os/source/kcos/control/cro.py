class AutonomousCRO:
    def __init__(self, risk_kernel, stress_engine=None):
        self.risk_kernel = risk_kernel
        self.stress_engine = stress_engine

    def approve(self, intent, account, market_ts, emergency=False):
        return self.risk_kernel.evaluate(intent, account, market_ts, emergency)
