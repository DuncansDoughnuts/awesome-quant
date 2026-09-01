import argparse,asyncio,threading,uvicorn
from .api import app
from .autonomous_runtime import AutonomousRuntime
def serve_api(): uvicorn.run(app,host='0.0.0.0',port=8080,log_level='info')
def main():
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=['runtime','research','genesis'],nargs='?',default='runtime'); mode=p.parse_args().mode
    if mode=='genesis':
        from .genesis import main as g; return g()
    if mode=='research':
        from .research.worker import run; return asyncio.run(run())
    threading.Thread(target=serve_api,daemon=True).start(); asyncio.run(AutonomousRuntime().run_forever())
if __name__=='__main__':main()
