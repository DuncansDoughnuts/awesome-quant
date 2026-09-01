import json

import psycopg
from psycopg.rows import dict_row

from ..domain import StrategyRecord


class StrategyRegistry:
    def __init__(self, dsn):
        self.dsn = dsn

    def upsert(self, s: StrategyRecord):
        sql = "INSERT INTO strategies(strategy_id,version,state,spec,metrics,updated_at) VALUES (%s,%s,%s,%s::jsonb,%s::jsonb,now()) ON CONFLICT(strategy_id) DO UPDATE SET version=excluded.version,state=excluded.state,spec=excluded.spec,metrics=excluded.metrics,updated_at=now()"
        with psycopg.connect(self.dsn) as c:
            c.execute(
                sql,
                (
                    s.strategy_id,
                    s.version,
                    s.stage,
                    json.dumps(s.spec),
                    json.dumps(s.metrics),
                ),
            )

    def list(self):
        with psycopg.connect(self.dsn, row_factory=dict_row) as c:
            rows = c.execute(
                "SELECT strategy_id,version,state,spec,metrics FROM strategies ORDER BY updated_at DESC"
            ).fetchall()
        return [
            StrategyRecord(
                r["strategy_id"],
                r["version"],
                r["state"],
                r["spec"].get("asset_class", "UNKNOWN"),
                r["spec"].get("universe", []),
                r["spec"].get("hypothesis_id"),
                r["spec"],
                r["metrics"],
            )
            for r in rows
        ]
