import asyncio

from ..config import settings
from ..memory import MemoryStore
from ..state import HotState
from .promotion import PromotionEngine
from .strategy_registry import StrategyRegistry


async def run():
    state = HotState(settings.redis_url)
    memory = MemoryStore(settings.database_url)
    registry = StrategyRegistry(settings.database_url)
    promotion = PromotionEngine()
    while True:
        await state.set_heartbeat("research")
        try:
            for s in registry.list():
                nxt = promotion.next_stage(s.stage, s.metrics)
                if nxt.value != s.stage:
                    old = s.stage
                    s.stage = nxt.value
                    registry.upsert(s)
                    memory.audit(
                        settings.kcos_instance_id,
                        "strategy_promoted",
                        {"strategy_id": s.strategy_id, "from": old, "to": s.stage},
                    )
        except Exception as exc:
            try:
                memory.audit(
                    settings.kcos_instance_id,
                    "research_worker_error",
                    {"error": repr(exc)},
                )
            except Exception:
                pass
        await asyncio.sleep(10)
