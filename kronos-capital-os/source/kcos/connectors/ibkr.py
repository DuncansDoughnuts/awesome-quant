import httpx

from ..models import AccountState, ConnectorState


class IbkrConnector:
    name = "ibkr"

    def __init__(self, base_url, account_id, bearer_token=None, verify_tls=False):
        self.base_url = base_url.rstrip("/")
        self.account_id = account_id
        self.verify_tls = verify_tls
        self.headers = (
            {"Authorization": f"Bearer {bearer_token}"} if bearer_token else {}
        )

    async def health(self):
        async with httpx.AsyncClient(verify=self.verify_tls, timeout=5) as c:
            r = await c.get(
                f"{self.base_url}/iserver/auth/status", headers=self.headers
            )
            return (
                ConnectorState.CONNECTED
                if r.is_success and r.json().get("authenticated")
                else ConnectorState.DEGRADED
            )

    async def account_state(self):
        async with httpx.AsyncClient(verify=self.verify_tls, timeout=10) as c:
            r = await c.get(
                f"{self.base_url}/portfolio/{self.account_id}/summary",
                headers=self.headers,
            )
            r.raise_for_status()
            d = r.json()
            eq = float((d.get("netliquidation") or {}).get("amount", 0) or 0)
            cash = float((d.get("totalcashvalue") or {}).get("amount", eq) or eq)
            return AccountState(eq, cash, 0, 0, 0, max(eq, 1), [])

    async def place_order(self, intent, approved_qty):
        conid = intent.metadata.get("conid")
        if not conid:
            raise ValueError("IBKR requires resolved conid")
        payload = {
            "orders": [
                {
                    "acctId": self.account_id,
                    "conid": int(conid),
                    "orderType": "MKT",
                    "side": intent.side,
                    "quantity": approved_qty,
                    "tif": "DAY",
                }
            ]
        }
        async with httpx.AsyncClient(verify=self.verify_tls, timeout=10) as c:
            r = await c.post(
                f"{self.base_url}/iserver/account/{self.account_id}/orders",
                headers=self.headers,
                json=payload,
            )
            r.raise_for_status()
            return r.json()
