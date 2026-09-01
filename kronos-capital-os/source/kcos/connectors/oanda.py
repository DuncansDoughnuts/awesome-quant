import json

import httpx

from ..models import AccountState, ConnectorState, MarketEvent


class OandaConnector:
    name = "oanda"

    def __init__(self, base_url, stream_url, account_id, token):
        self.base_url = base_url.rstrip("/")
        self.stream_url = stream_url.rstrip("/")
        self.account_id = account_id
        self.headers = {"Authorization": f"Bearer {token}"}

    async def health(self):
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(
                f"{self.base_url}/v3/accounts/{self.account_id}/summary",
                headers=self.headers,
            )
            return ConnectorState.CONNECTED if r.is_success else ConnectorState.DEGRADED

    async def account_state(self):
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                f"{self.base_url}/v3/accounts/{self.account_id}/summary",
                headers=self.headers,
            )
            r.raise_for_status()
            a = r.json()["account"]
            eq = float(a["NAV"])
            cash = float(a.get("balance", eq))
            return AccountState(eq, cash, 0, 0, 0, eq, [])

    async def place_order(self, intent, approved_qty):
        units = approved_qty if intent.side == "BUY" else -approved_qty
        body = {
            "order": {
                "units": str(int(units)),
                "instrument": intent.instrument,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT",
            }
        }
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                f"{self.base_url}/v3/accounts/{self.account_id}/orders",
                headers=self.headers,
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def run_prices(self, on_event, instruments):
        url = f"{self.stream_url}/v3/accounts/{self.account_id}/pricing/stream"
        async with httpx.AsyncClient(timeout=None) as c:
            async with c.stream(
                "GET",
                url,
                headers=self.headers,
                params={"instruments": ",".join(instruments)},
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    m = json.loads(line)
                    if m.get("type") != "PRICE":
                        continue
                    bids, asks = m.get("bids") or [], m.get("asks") or []
                    if bids and asks:
                        bid = float(bids[0]["price"])
                        ask = float(asks[0]["price"])
                        await on_event(
                            MarketEvent(
                                "OANDA",
                                m["instrument"],
                                "FX",
                                (bid + ask) / 2,
                                bid=bid,
                                ask=ask,
                            )
                        )
