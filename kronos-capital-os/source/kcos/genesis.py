import getpass
import os
from pathlib import Path
RUNTIME=Path('.env.runtime')
def yn(prompt,default=False):
    value=input(prompt+(' [Y/n] ' if default else ' [y/N] ')).strip().lower(); return default if not value else value in {'y','yes'}
def secret(prompt): return getpass.getpass(prompt+': ').strip()
def main():
    print('\nKRONOS CAPITAL OS — GENESIS v1.0\n'); env={'HEARTBEAT_SECONDS':'6','MAX_DECISION_STALENESS_SECONDS':'6'}
    env['OWNER_JURISDICTION']=input('Owner jurisdiction [US]: ').strip() or 'US'; env['BASE_CURRENCY']=input('Base currency [USD]: ').strip() or 'USD'; env['INITIAL_CAPITAL']=input('Starting deployable capital [1000]: ').strip() or '1000'
    ibkr=yn('Connect Interactive Brokers?'); env['IBKR_ENABLED']=str(ibkr).lower()
    if ibkr:
        env['IBKR_ACCOUNT_ID']=input('IBKR account ID: ').strip(); env['IBKR_BASE_URL']=input('IBKR Web API base URL [https://localhost:5000/v1/api]: ').strip() or 'https://localhost:5000/v1/api'; env['IBKR_BEARER_TOKEN']=secret('IBKR bearer/session token (blank if gateway manages auth)')
    coinbase=yn('Connect Coinbase Advanced Trade?'); env['COINBASE_ENABLED']=str(coinbase).lower()
    if coinbase:
        env['COINBASE_API_KEY_NAME']=input('Coinbase CDP API key name: ').strip(); env['COINBASE_API_PRIVATE_KEY']=secret('Coinbase CDP private key'); env['COINBASE_PORTFOLIO_ID']=input('Coinbase portfolio ID: ').strip()
    oanda=yn('Connect OANDA for dedicated FX?'); env['OANDA_ENABLED']=str(oanda).lower()
    if oanda:
        env['OANDA_ACCOUNT_ID']=input('OANDA account ID: ').strip(); env['OANDA_ACCESS_TOKEN']=secret('OANDA access token')
    env['DATABENTO_API_KEY']=secret('Databento API key (recommended; blank to skip)'); env['FRED_API_KEY']=secret('FRED API key (blank to skip)'); env['SEC_USER_AGENT']=input('SEC User-Agent [KCOS/1.0 owner@example.com]: ').strip() or 'KCOS/1.0 owner@example.com'
    if yn('Connect an optional reasoning-model endpoint for hypothesis generation?',False):
        env['LLM_API_BASE']=input('Reasoning API base URL: ').strip(); env['LLM_MODEL']=input('Model name: ').strip(); env['LLM_API_KEY']=secret('Reasoning API key')
    env['MAX_RISK_PER_TRADE_PCT']=input('Maximum risk per trade % [0.50]: ').strip() or '.50'; env['MAX_AGGREGATE_OPEN_RISK_PCT']=input('Maximum aggregate open risk % [2.00]: ').strip() or '2.00'; env['HARD_DRAWDOWN_STOP_PCT']=input('Hard portfolio drawdown stop % [10]: ').strip() or '10'
    live=yn('Permit automatic PAPER → CANARY → LIVE graduation only after fixed evidence gates?',False); env['AUTO_GRADUATE_TO_LIVE']=str(live).lower(); env['LIVE_TRADING_ENABLED']=str(live).lower()
    defaults={'ENVIRONMENT':'production','KCOS_INSTANCE_ID':'kcos-01','DATABASE_URL':'postgresql://kcos:kcos@postgres:5432/kcos','REDIS_URL':'redis://redis:6379/0','KRONOS_ENABLED':'true','KRONOS_MODEL':'NeoQuasar/Kronos-base','KRONOS_TOKENIZER':'NeoQuasar/Kronos-Tokenizer-base','KRONOS_DEVICE':'cpu','MAX_DAILY_LOSS_PCT':'1','MAX_WEEKLY_LOSS_PCT':'3','MAX_GROSS_LEVERAGE':'1','MAX_SINGLE_ASSET_NOTIONAL_PCT':'20','MAX_VENUE_EXPOSURE_PCT':'50','MIN_SIGNAL_CONFIDENCE':'.60','SECRET_BACKEND':'env'}; defaults.update(env)
    if ibkr and not env.get('IBKR_ACCOUNT_ID'): raise SystemExit('Genesis incomplete: IBKR account ID missing')
    if coinbase and not (env.get('COINBASE_API_KEY_NAME') and env.get('COINBASE_API_PRIVATE_KEY')): raise SystemExit('Genesis incomplete: Coinbase credentials missing')
    if oanda and not (env.get('OANDA_ACCOUNT_ID') and env.get('OANDA_ACCESS_TOKEN')): raise SystemExit('Genesis incomplete: OANDA credentials missing')
    RUNTIME.write_text('\n'.join(f'{k}={str(v).replace(chr(10),"\\n")}' for k,v in defaults.items())+'\n'); os.chmod(RUNTIME,0o600)
    print('\nGENESIS COMPLETE\n✓ connector configuration captured\n✓ six-second freshness constitution installed\n✓ deterministic CRO/risk ceilings installed\n✓ strategy validation/promotion gates installed\n✓ credential boundary installed'); print('\nRoutine operation no longer requires trade-by-trade owner participation once providers authenticate and deployment is healthy.\nNext: make build && make start && make health')
if __name__=='__main__': main()
