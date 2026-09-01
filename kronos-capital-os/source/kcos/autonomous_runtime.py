from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

from .alpha.fusion import AlphaFusion
from .alpha.marketplace import AlphaMarketplace
from .config import settings
from .connectors.factory import register_execution_connectors
from .context_engine import ContextCompiler
from .control.cio import AutonomousCIO
from .control.cro import AutonomousCRO
from .control.model_governor import ModelGovernor
from .control.research_director import ResearchDirector
from .control.sentinel import Sentinel
from .curiosity import CuriosityEngine
from .data.bar_aggregator import BarAggregator
from .data.bar_store import BarStore
from .execution.paper import PaperVenue
from .execution.reconciliation import Reconciler
from .execution.router import ExecutionRouter
from .market_graph import MarketGraph
from .memory import MemoryStore
from .memory_layers import TieredMemory
from .modeling.ensemble import ForecastEnsemble
from .modeling.factors import FactorModel
from .modeling.kronos_service import KronosInferenceService
from .modeling.regime import RegimeModel
from .modeling.volatility import VolatilityModel
from .models import MarketEvent
from .observability.metrics import (
    CYCLE,
    DECISIONS,
    ORDERS,
    STALE_CONNECTORS,
    WORLD_VERSION,
)
from .portfolio import PortfolioEngine
from .realtime.watchdog import ConnectorWatchdog
from .reasoning.provider import ReasoningProvider
from .research.autonomous_lab import AutonomousLab
from .research.promotion import PromotionEngine
from .research.strategy_registry import StrategyRegistry
from .risk.stress import StressEngine
from .risk_kernel import RiskKernel
from .state import HotState
from .strategy_factory import StrategyFactory
from .trend_engine import TrendEngine


class AutonomousRuntime:
    def __init__(self):
        self.hot = HotState(settings.redis_url)
        self.durable = MemoryStore(settings.database_url)
        self.memory = TieredMemory(self.durable)
        self.bars = BarStore()
        self.ohlcv = BarAggregator(60)
        self.graph = MarketGraph()
        self.context = ContextCompiler(self.memory, self.graph)
        self.trends = TrendEngine()
        self.vol = VolatilityModel()
        self.regimes = RegimeModel()
        self.factors = FactorModel()
        self.ensemble = ForecastEnsemble()
        self.kronos = (
            KronosInferenceService(
                settings.kronos_model, settings.kronos_tokenizer, settings.kronos_device
            )
            if settings.kronos_enabled
            else None
        )
        self.fusion = AlphaFusion()
        self.marketplace = AlphaMarketplace()
        self.curiosity = CuriosityEngine()
        self.factory = StrategyFactory()
        self.registry = StrategyRegistry(settings.database_url)
        self.promotion = PromotionEngine()
        self.lab = AutonomousLab()
        self.reasoner = ReasoningProvider(
            settings.llm_api_base, settings.llm_api_key, settings.llm_model
        )
        self.portfolio = PortfolioEngine()
        self.risk = RiskKernel(settings)
        self.cio = AutonomousCIO()
        self.cro = AutonomousCRO(self.risk, StressEngine())
        self.research_director = ResearchDirector()
        self.model_governor = ModelGovernor()
        self.sentinel = Sentinel()
        self.execution = register_execution_connectors(ExecutionRouter())
        self.paper = PaperVenue(settings.initial_capital)
        self.execution.register("PAPER", self.paper)
        self.reconciler = Reconciler()
        self.watchdog = ConnectorWatchdog(settings.max_decision_staleness_seconds)
        self.last_event = {}
        self.prev_price = {}
        self.world_version = 0

    async def start_feeds(self):
        tasks = []
        if (
            settings.oanda_enabled
            and settings.oanda_account_id
            and settings.oanda_access_token
        ):
            try:
                feed = self.execution.get("OANDA")
                symbols = [
                    s.strip() for s in settings.oanda_symbols.split(",") if s.strip()
                ]
                tasks.append(
                    asyncio.create_task(feed.run_prices(self.on_market_event, symbols))
                )
            except Exception:
                pass
        if (
            settings.databento_api_key
            and settings.databento_dataset
            and settings.databento_symbols
        ):
            try:
                from .connectors.databento_feed import DatabentoFeed

                sub = {
                    "dataset": settings.databento_dataset,
                    "schema": settings.databento_schema,
                    "symbols": [
                        s.strip()
                        for s in settings.databento_symbols.split(",")
                        if s.strip()
                    ],
                }
                tasks.append(
                    asyncio.create_task(
                        DatabentoFeed(settings.databento_api_key, sub).run(
                            self.on_market_event
                        )
                    )
                )
            except Exception:
                pass
        return tasks

    async def on_market_event(self, event: MarketEvent):
        prev = self.prev_price.get(event.instrument)
        self.prev_price[event.instrument] = event.price
        self.last_event[event.instrument] = event
        self.world_version += 1
        WORLD_VERSION.set(self.world_version)
        self.bars.update(event.instrument, event.price, event.volume)
        self.ohlcv.update(event)
        self.memory.observe(event.instrument, asdict(event))
        self.watchdog.seen(event.venue, event.ts)
        if prev and prev > 0:
            self.graph.update_return(event.instrument, event.price / prev - 1)
        await self.hot.set_json(
            f"market:{event.instrument}",
            asdict(event),
            ttl=max(30, int(settings.max_decision_staleness_seconds * 5)),
        )
        if self.kronos:
            await self.kronos.maybe_schedule(
                event.instrument, self.ohlcv.bars(event.instrument)
            )
        if event.metadata.get("material_event") or (
            prev and abs(event.price / prev - 1) > 0.01
        ):
            await self.evaluate(event.instrument, "event_trigger")

    def _components(self, instrument):
        prices = self.bars.closes(instrument, 400)
        trend = self.trends.summarize(prices)
        vol = self.vol.ewma(prices)
        regime = self.regimes.classify(trend, vol)
        mom = self.factors.momentum(prices, 20)
        rev = self.factors.reversal(prices, 10)
        neigh = self.graph.neighbors(instrument)
        cross = (
            (sum(v["correlation"] for v in neigh.values()) / len(neigh) * mom * 0.25)
            if neigh
            else 0
        )
        comps = {
            "momentum": {
                "expected_return": mom * 0.2,
                "confidence": min(0.9, 0.5 + abs(mom) * 5),
            },
            "reversal": {
                "expected_return": rev * 0.1,
                "confidence": min(0.8, 0.5 + abs(rev) * 3),
            },
            "regime": {"expected_return": mom * 0.1, "confidence": regime.confidence},
            "cross_asset": {
                "expected_return": cross,
                "confidence": 0.55 if neigh else 0.2,
            },
        }
        if self.kronos and self.kronos.cached_component(instrument):
            comps["kronos"] = self.kronos.cached_component(instrument)
        return prices, trend, vol, regime, comps

    async def _research_surprise(self, instrument, prices, forecast):
        if len(prices) < 30:
            return
        recent = prices[-1] / prices[-6] - 1
        surprise = abs(recent - forecast.expected_return)
        if surprise < 0.01:
            return
        obs = {
            "surprises": [
                {
                    "magnitude": surprise,
                    "economic_relevance": min(1, abs(recent) * 20),
                    "confidence_gap": 1 - forecast.confidence,
                    "hypothesis": f"{instrument} has a regime-conditioned residual that may contain tradable information.",
                    "counter": f"{instrument} residual is noise after realistic costs and multiple-testing correction.",
                }
            ]
        }
        for h in self.research_director.prioritize(
            self.curiosity.generate(instrument, obs), 3
        ):
            for spec in self.factory.variants_from_hypothesis(
                h.hypothesis_id, instrument, self.last_event[instrument].asset_class
            ):
                try:
                    self.registry.upsert(
                        self.factory.record(
                            spec,
                            {
                                "leakage_flags": 0,
                                "oos_observations": 0,
                                "cost_model": True,
                            },
                        )
                    )
                except Exception:
                    pass
            self.durable.remember(
                "hypothesis",
                instrument,
                h.statement,
                {"counter": h.counter_hypothesis, "priority": h.priority},
                0.5,
            )

    def _research_candidates(self, instrument, prices):
        try:
            for s in self.registry.list():
                if instrument not in s.universe or s.stage not in {
                    "RESEARCH",
                    "WALK_FORWARD",
                }:
                    continue
                metrics = self.lab.evaluate(s, prices)
                s.metrics.update(metrics)
                nxt = self.promotion.next_stage(s.stage, s.metrics)
                s.stage = nxt.value
                self.registry.upsert(s)
        except Exception as exc:
            self.durable.audit(
                settings.kcos_instance_id,
                "autonomous_lab_error",
                {"instrument": instrument, "error": repr(exc)},
            )

    def _strategies(self, instrument):
        try:
            return [
                s
                for s in self.registry.list()
                if s.enabled
                and instrument in s.universe
                and s.stage in {"PAPER", "CANARY", "LIVE", "SCALED"}
            ]
        except Exception:
            return []

    async def _execute_strategy(
        self, s, event, forecast, regime, allocation_weight=1.0
    ):
        paper = s.stage == "PAPER" or not settings.live_trading_enabled
        venue = self.execution.for_asset_class(s.asset_class, paper=paper)
        account = await venue.account_state()
        signal = self.fusion.signal(
            s.strategy_id,
            getattr(venue, "name", "PAPER").upper(),
            event.instrument,
            s.asset_class,
            forecast,
            1.0,
            1.5,
        )
        intent = self.portfolio.intent_from_signal(signal, account.equity, event.price)
        if not intent:
            return None
        intent.qty *= max(0.01, min(1.0, allocation_weight))
        intent.venue = getattr(venue, "name", "PAPER").upper()
        intent.metadata.update(s.spec.get("metadata") or {})
        emergency = (await self.hot.emergency_stop_state()).get("enabled", False)
        decision = self.cro.approve(intent, account, event.ts, emergency)
        if not decision.approved:
            self.durable.audit(
                settings.kcos_instance_id,
                "risk_veto",
                {
                    "strategy_id": s.strategy_id,
                    "instrument": event.instrument,
                    "reason": decision.reason,
                },
            )
            return None
        result = await venue.place_order(intent, decision.approved_qty)
        ORDERS.labels(
            venue=intent.venue, status=str(result.get("status", "SUBMITTED"))
        ).inc()
        self.durable.audit(
            settings.kcos_instance_id,
            "order_submitted",
            {
                "strategy_id": s.strategy_id,
                "instrument": event.instrument,
                "qty": decision.approved_qty,
                "risk_dollars": decision.risk_dollars,
                "result": result,
            },
        )
        return result

    async def evaluate(self, instrument, reason="heartbeat"):
        event = self.last_event.get(instrument)
        if not event:
            return None
        prices, trend, vol, regime, components = self._components(instrument)
        forecast = self.ensemble.combine(instrument, 6, components)
        await self._research_surprise(instrument, prices, forecast)
        self._research_candidates(instrument, prices)
        DECISIONS.inc()
        strategies = self._strategies(instrument)
        ranks = self.marketplace.rank(strategies)
        allocations = {
            x["strategy_id"]: x["target_weight"] for x in self.cio.propose(ranks, {})
        }
        packet = self.context.compile(
            instrument,
            {"world_version": self.world_version, "market": asdict(event), "delta": {}},
            {"equity": getattr(self, "last_equity", settings.initial_capital)},
            {"forecast": asdict(forecast)},
            asdict(regime),
        )
        results = []
        for st in strategies:
            try:
                r = await self._execute_strategy(
                    st, event, forecast, regime, allocations.get(st.strategy_id, 0.0)
                )
                results.append(
                    {
                        "strategy_id": st.strategy_id,
                        "allocation": allocations.get(st.strategy_id, 0.0),
                        "result": r,
                    }
                )
            except Exception as exc:
                self.durable.audit(
                    settings.kcos_instance_id,
                    "execution_error",
                    {
                        "strategy_id": st.strategy_id,
                        "instrument": instrument,
                        "error": repr(exc),
                    },
                )
        payload = {
            "id": uuid.uuid4().hex,
            "instrument": instrument,
            "reason": reason,
            "world_version": self.world_version,
            "context_packet": packet,
            "trend": trend,
            "volatility": vol,
            "regime": asdict(regime),
            "forecast": asdict(forecast),
            "strategy_results": results,
        }
        self.durable.audit(settings.kcos_instance_id, "decision_evaluated", payload)
        return payload

    async def heartbeat(self):
        t = time.perf_counter()
        await self.hot.set_heartbeat("runtime")
        for instrument in list(self.last_event):
            await self.evaluate(instrument, "six_second_heartbeat")
        latency = time.perf_counter() - t
        CYCLE.observe(latency)
        required = sorted({e.venue for e in self.last_event.values()})
        stale = self.watchdog.stale(required) if required else []
        STALE_CONNECTORS.set(len(stale))
        sentinel = self.sentinel.evaluate(latency, stale, True)
        cycle = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "latency_seconds": latency,
            "world_version": self.world_version,
            "status": "HEALTHY" if sentinel["healthy"] else "SLA_BREACH",
            "sentinel": sentinel,
        }
        await self.hot.set_json("runtime:last_cycle", cycle, ttl=30)
        self.durable.audit(settings.kcos_instance_id, "heartbeat", cycle)
        return cycle

    async def run_forever(self):
        feed_tasks = await self.start_feeds()
        try:
            while True:
                started = time.monotonic()
                try:
                    await self.heartbeat()
                except Exception as exc:
                    try:
                        self.durable.audit(
                            settings.kcos_instance_id,
                            "runtime_error",
                            {"error": repr(exc)},
                        )
                    except Exception:
                        pass
                await asyncio.sleep(
                    max(0, settings.heartbeat_seconds - (time.monotonic() - started))
                )
        finally:
            for t in feed_tasks:
                t.cancel()
