import asyncio
from ..models import ConnectorState,MarketEvent
class DatabentoFeed:
    name="databento"
    def __init__(self,api_key,subscription): self.api_key=api_key; self.subscription=subscription; self.connected=False
    async def health(self): return ConnectorState.CONNECTED if self.connected else ConnectorState.RECONNECTING
    async def run(self,on_event):
        import databento as db
        loop=asyncio.get_running_loop()
        def sync():
            c=db.Live(key=self.api_key)
            c.subscribe(dataset=self.subscription["dataset"],schema=self.subscription.get("schema","trades"),stype_in=self.subscription.get("stype_in","raw_symbol"),symbols=self.subscription["symbols"])
            self.connected=True
            for rec in c:
                px=getattr(rec,"price",getattr(rec,"close",None))
                if px is None: continue
                px=float(px)
                if px>1e8: px/=1e9
                symbol=str(getattr(rec,"symbol",getattr(rec,"instrument_id","UNKNOWN")))
                asyncio.run_coroutine_threadsafe(on_event(MarketEvent("DATABENTO",symbol,"UNKNOWN",px)),loop).result()
        await asyncio.to_thread(sync)
