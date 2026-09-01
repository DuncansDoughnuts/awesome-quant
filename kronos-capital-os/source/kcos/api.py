from fastapi import FastAPI,Response
from prometheus_client import generate_latest,CONTENT_TYPE_LATEST
from .config import settings
from .state import HotState
app=FastAPI(title='Kronos Capital OS',version='1.0.0'); state=HotState(settings.redis_url)
@app.get('/health')
async def health():
    cycle=await state.get_json('runtime:last_cycle',{}); return {'ok':cycle.get('status')!='SLA_BREACH','instance_id':settings.kcos_instance_id,'live_trading_enabled':settings.live_trading_enabled,'max_decision_staleness_seconds':settings.max_decision_staleness_seconds,'cycle':cycle}
@app.get('/status')
async def status(): return {'cycle':await state.get_json('runtime:last_cycle',{}),'emergency_stop':await state.emergency_stop_state()}
@app.get('/metrics')
def metrics(): return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
@app.post('/emergency-stop')
async def emergency_stop(reason:str='owner_request'): await state.emergency_stop(True,reason); return {'ok':True,'emergency_stop':True,'reason':reason}
@app.post('/emergency-resume')
async def emergency_resume(): await state.emergency_stop(False,''); return {'ok':True,'emergency_stop':False}
