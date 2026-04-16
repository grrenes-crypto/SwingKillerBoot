from scanner import get_top_coins, get_market_data
from ai_decision import ask_deepseek
from executor import execute_trade

def run():
    print("🔍 Starte Swing-Scan...")
    coins = get_top_coins()
    for sym in coins:
        data = get_market_data(sym)
        if not data: continue
        decision = ask_deepseek(data)
        if not decision: continue
        decision["price"] = data["price"]
        print(f"{sym}: {decision['action']} (Conf: {decision['confidence']})")
        execute_trade(sym, decision)

if __name__ == "__main__":
    run()