import json
import os
from scanner import session  # <-- DAS IST DIE EINZIGE ÄNDERUNG
from config import *

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_positions(positions):
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)

def update_trailing_stop(symbol, current_price):
    positions = load_positions()
    if symbol not in positions:
        return
    pos = positions[symbol]
    entry = pos['entry_price']
    highest = pos.get('highest_price', entry)
    if current_price > highest:
        highest = current_price
        pos['highest_price'] = highest
        if (highest - entry) / entry * 100 >= TRAILING_ACTIVATION:
            new_sl = highest * (1 - TRAILING_DISTANCE / 100)
            if new_sl > pos['stop_loss']:
                pos['stop_loss'] = new_sl
                session.set_trading_stop(category="linear", symbol=symbol, side="Buy", stopLoss=str(round(new_sl, 4)))
                print(f"🔄 Trailing Stop für {symbol} auf {new_sl:.4f} angehoben")
        save_positions(positions)

def calculate_leverage(atr):
    if atr <= 0:
        return BASE_LEVERAGE
    dynamic = BASE_LEVERAGE * (BASE_LEVERAGE / atr)
    return max(MIN_LEVERAGE, min(MAX_LEVERAGE, dynamic))

def set_leverage_for_symbol(symbol, leverage):
    try:
        session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=str(leverage),
            sellLeverage=str(leverage)
        )
        print(f"🔧 Hebel für {symbol} auf {leverage:.1f}x gesetzt")
    except Exception as e:
        print(f"❌ Fehler beim Setzen des Hebels für {symbol}: {e}")

def execute_trade(symbol, decision):
    positions = load_positions()

    if symbol in positions:
        print(f"⏸️ {symbol} bereits im Trade – überspringe")
        return

    if len(positions) >= MAX_OPEN_POSITIONS:
        print(f"⏸️ Maximale Positionen ({MAX_OPEN_POSITIONS}) erreicht")
        return

    if decision["action"] != "BUY":
        print(f"⏸️ {symbol}: HOLD")
        return

    price = decision.get("price", 0)
    sl = decision["stop_loss"]
    tp = decision["take_profit"]

    atr = decision.get("atr", 0)
    leverage = calculate_leverage(atr)
    set_leverage_for_symbol(symbol, leverage)

    bal = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
    equity = float(bal["result"]["list"][0]["totalEquity"])
    risk = equity * (RISK_PERCENT_PER_TRADE / 100)
    qty = risk / abs(price - sl)

    if qty * price < 5:
        print(f"⚠️ Order zu klein für {symbol}")
        return

    try:
        session.place_order(category="linear", symbol=symbol, side="Buy", orderType="Market", qty=str(round(qty,3)))
        session.set_trading_stop(category="linear", symbol=symbol, side="Buy", stopLoss=str(sl), takeProfit=str(tp))
        print(f"✅ Trade {symbol}: {round(qty,3)} @ {price} | SL: {sl} | TP: {tp}")

        positions[symbol] = {
            'entry_price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'quantity': round(qty, 3),
            'highest_price': price
        }
        save_positions(positions)

    except Exception as e:
        print(f"❌ Trade Fehler {symbol}: {e}")
