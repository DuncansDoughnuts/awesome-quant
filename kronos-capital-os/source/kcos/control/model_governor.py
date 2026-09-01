class ModelGovernor:
    def allocation_multiplier(self,calibration_haircut,drift_score): return max(0.0,min(1.0,float(calibration_haircut)*(1-min(1.0,float(drift_score)))))
    def should_disable(self,drift_score,calibration_haircut): return drift_score>1.0 or calibration_haircut<.3
