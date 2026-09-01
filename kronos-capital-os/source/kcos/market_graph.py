from collections import defaultdict, deque

import numpy as np


class MarketGraph:
    def __init__(self, maxlen=1000):
        self.returns = defaultdict(lambda: deque(maxlen=maxlen))
        self.edges = {}
        self.events = deque(maxlen=5000)

    def update_return(self, instrument, value):
        self.returns[instrument].append(float(value))

    def update_event(self, event):
        self.events.append(event)

    def correlation(self, a, b, window=120):
        xa = list(self.returns[a])[-window:]
        xb = list(self.returns[b])[-window:]
        n = min(len(xa), len(xb))
        if n < 20:
            return None
        x = np.asarray(xa[-n:])
        y = np.asarray(xb[-n:])
        if np.std(x) == 0 or np.std(y) == 0:
            return None
        return float(np.corrcoef(x, y)[0, 1])

    def lead_lag(self, a, b, max_lag=12, window=240):
        xa = np.asarray(list(self.returns[a])[-window:])
        xb = np.asarray(list(self.returns[b])[-window:])
        n = min(len(xa), len(xb))
        if n < 40:
            return None
        xa = xa[-n:]
        xb = xb[-n:]
        best = (0, 0.0)
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                x, y = xa[-lag:], xb[:lag]
            elif lag > 0:
                x, y = xa[:-lag], xb[lag:]
            else:
                x, y = xa, xb
            if len(x) < 20 or np.std(x) == 0 or np.std(y) == 0:
                continue
            c = float(np.corrcoef(x, y)[0, 1])
            if abs(c) > abs(best[1]):
                best = (lag, c)
        return {"lag": best[0], "correlation": best[1]}

    def neighbors(self, instrument, threshold=0.45):
        out = {}
        for other in self.returns:
            if other == instrument:
                continue
            c = self.correlation(instrument, other)
            if c is not None and abs(c) >= threshold:
                out[other] = {
                    "correlation": c,
                    "lead_lag": self.lead_lag(instrument, other),
                }
        return out
