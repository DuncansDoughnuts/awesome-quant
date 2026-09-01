class ContextCompiler:
    def __init__(self, memory, graph=None):
        self.memory = memory
        self.graph = graph

    def compile(
        self,
        instrument,
        hot_state,
        portfolio_state,
        model_state,
        regime_state,
        orders=None,
    ):
        neighbors = (
            self.graph.neighbors(instrument)
            if self.graph and hasattr(self.graph, "neighbors")
            else {}
        )
        mem = (
            self.memory.packet(instrument)
            if hasattr(self.memory, "packet")
            else {"institutional": self.memory.recall(instrument, 6)}
        )
        return {
            "instrument": instrument,
            "world_version": hot_state.get("world_version"),
            "market_delta": hot_state.get("delta", {}),
            "market": hot_state.get("market", {}),
            "regime": regime_state,
            "models": model_state,
            "portfolio": portfolio_state,
            "orders": orders or [],
            "related_markets": neighbors,
            "memory": mem,
        }
