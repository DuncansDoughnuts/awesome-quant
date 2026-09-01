from __future__ import annotations
import asyncio,time
import pandas as pd
from .calibration import CalibrationTracker
from ..kronos_adapter import KronosAdapter
class KronosInferenceService:
    def __init__(self,model,tokenizer,device='cpu',min_bars=64,interval_seconds=60,pred_len=12): self.adapter=KronosAdapter(model,tokenizer,device); self.min_bars=min_bars; self.interval=interval_seconds; self.pred_len=pred_len; self.cache={}; self.last_run={}; self.inflight=set(); self.calibration={}
    def cached_component(self,instrument):
        item=self.cache.get(instrument); return None if not item else {'expected_return':item['expected_return'],'confidence':item['confidence']}
    async def maybe_schedule(self,instrument,bars):
        if len(bars)<self.min_bars or instrument in self.inflight:return
        now=time.time()
        if now-self.last_run.get(instrument,0)<self.interval:return
        self.inflight.add(instrument); self.last_run[instrument]=now; asyncio.create_task(self._run(instrument,list(bars)))
    async def _run(self,instrument,bars):
        try:
            df=pd.DataFrame(bars).set_index('timestamp'); last=df.index[-1]; future=pd.date_range(last,periods=self.pred_len+1,freq='1min',inclusive='right').to_series(index=None); result=await asyncio.to_thread(self.adapter.forecast,df,future,self.pred_len,5); tracker=self.calibration.setdefault(instrument,CalibrationTracker()); haircut=tracker.haircut(); er=float(result['expected_return']); self.cache[instrument]={'expected_return':er,'confidence':max(.05,min(.9,(.5+abs(er)*5)*haircut)),'path':result.get('path',[]),'ts':time.time()}
        except Exception as exc:self.cache[instrument]={'expected_return':0.0,'confidence':0.0,'error':repr(exc),'ts':time.time()}
        finally:self.inflight.discard(instrument)
