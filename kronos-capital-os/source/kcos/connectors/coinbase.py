from ..models import AccountState,ConnectorState
class CoinbaseConnector:
    name='coinbase'
    def __init__(self,client): self.client=client
    async def health(self):
        try:self.client.get_accounts(limit=1); return ConnectorState.CONNECTED
        except Exception:return ConnectorState.DEGRADED
    async def account_state(self):
        accounts=self.client.get_accounts(); cash=0.0
        for a in getattr(accounts,'accounts',[]) or []:
            if getattr(a,'currency','') in ('USD','USDC'): cash+=float(getattr(getattr(a,'available_balance',None),'value',0) or 0)
        return AccountState(cash,cash,0,0,0,max(cash,1),[])
    async def place_order(self,intent,approved_qty):
        return self.client.market_order(client_order_id=intent.metadata.get('client_order_id',intent.strategy_id),product_id=intent.instrument,side=intent.side,base_size=str(approved_qty))
