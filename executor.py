from pybit.unified_trading import HTTP
from config import *

session = HTTP(testnet=BYBIT_TESTNET, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

def execute_trade(symbol, decision):
    if decision["action"] != "BUY":
        print(f"HOLD {symbol}")
        return

    price = decision.get("price", 0)
    sl = decision["stop_loss"]
    tp = decision["take_profit"]

    # Balance
    bal = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
    equity = float(bal["result"]["list"][0]["totalEquity"])
    risk = equity * (RISK_PERCENT_PER_TRADE / 100)
    qty = risk / abs(price - sl)

    if qty * price < 5:
        print(f"Order zu klein für {symbol}")
        return

    try:
        session.place_order(category="linear", symbol=symbol, side="Buy", orderType="Market", qty=str(round(qty,3)))
        session.set_trading_stop(category="linear", symbol=symbol, side="Buy", stopLoss=str(sl), takeProfit=str(tp))
        print(f"✅ Trade {symbol}: {round(qty,3)} @ {price} | SL: {sl} | TP: {tp}")
    except Exception as e:
        print(f"❌ Trade Fehler {symbol}: {e}")