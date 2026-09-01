from . import *
from ..models import AccountState,ConnectorState
class PaperVenue:
    name="paper"
    def __init__(self,equity=1000): self.equity=equity; self.orders=[]
    async def health(self): return ConnectorState.CONNECTED
    async def account_state(self): return AccountState(self.equity,self.equity,0,0,0,self.equity,[])
    async def place_order(self,intent,approved_qty):
        order={"status":"FILLED_SIMULATED","instrument":intent.instrument,"side":intent.side,"qty":approved_qty,"price":intent.reference_price,"strategy_id":intent.strategy_id}; self.orders.append(order); return order
    async def cancel_all(self): self.orders.clear()
