from scanner import get_top_coins, get_market_data
from ai_decision import ask_deepseek
from executor import execute_trade, load_positions, update_trailing_stop
from config import BYBIT_TESTNET, BYBIT_API_KEY, BYBIT_API_SECRET, MIN_BALANCE_FOR_SCAN
from pybit.unified_trading import HTTP

session = HTTP(testnet=BYBIT_TESTNET, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

def check_balance():
    try:
        bal = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        equity = float(bal["result"]["list"][0]["totalEquity"])
        print(f"💰 Aktuelles Guthaben: {equity:.2f} USDT")
        
        if equity < MIN_BALANCE_FOR_SCAN:
            print(f"⚠️ Guthaben zu niedrig für Scan (min. {MIN_BALANCE_FOR_SCAN} USDT) – breche ab.")
            return False
        return True
    except Exception as e:
        print(f"❌ Fehler beim Abrufen des Guthabens: {e}")
        return False

def run():
    print("🔍 Starte Swing-Scan...")
    
    if not check_balance():
        return

    positions = load_positions()
    for symbol in positions:
        try:
            resp = session.get_tickers(category="linear", symbol=symbol)
            current_price = float(resp["result"]["list"][0]["lastPrice"])
            update_trailing_stop(symbol, current_price)
        except Exception as e:
            print(f"Fehler beim Update von {symbol}: {e}")

    coins = get_top_coins()
    for sym in coins:
        data = get_market_data(sym)
        if not data: 
            continue
        decision = ask_deepseek(data)
        if not decision: 
            continue
        decision["price"] = data["price"]
        decision["atr"] = data["atr"]
        print(f"{sym}: {decision['action']} (Conf: {decision['confidence']})")
        execute_trade(sym, decision)

if __name__ == "__main__":
    run()
