from collections import defaultdict, deque


class TieredMemory:
    def __init__(self, durable_store, hot_items=1000, warm_items=10000):
        self.durable = durable_store
        self.hot = defaultdict(lambda: deque(maxlen=hot_items))
        self.warm = defaultdict(lambda: deque(maxlen=warm_items))

    def observe(self, subject, event):
        self.hot[subject].append(event)
        self.warm[subject].append(event)

    def institutionalize(self, subject, summary, evidence=None, confidence=0.5):
        self.durable.remember("institutional", subject, summary, evidence, confidence)

    def packet(self, subject, hot_n=20, warm_n=20, cold_n=8):
        return {
            "hot": list(self.hot[subject])[-hot_n:],
            "warm": list(self.warm[subject])[-warm_n:],
            "institutional": self.durable.recall(subject, cold_n),
        }
