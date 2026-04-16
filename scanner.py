import pandas as pd
import ta
from pybit.unified_trading import HTTP
from config import *

session = HTTP(testnet=BYBIT_TESTNET, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

def get_top_coins(limit=TOP_COINS_LIMIT):
    tickers = session.get_tickers(category="linear")["result"]["list"]
    df = pd.DataFrame(tickers)
    df["turnover24h"] = df["turnover24h"].astype(float)
    return df.nlargest(limit, "turnover24h")["symbol"].tolist()

def get_market_data(symbol):
    try:
        # 1h Kerzen
        resp = session.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        df = pd.DataFrame(resp["result"]["list"],
                          columns=['timestamp','open','high','low','close','volume','turnover'])
        for col in ['open','high','low','close']:
            df[col] = df[col].astype(float)
        df = df.iloc[::-1].reset_index(drop=True)

        # Indikatoren
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        df['ema20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
        df['ema50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()
        df['atr'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()

        last = df.iloc[-1]
        return {
            "symbol": symbol,
            "price": round(last['close'], 4),
            "rsi": round(last['rsi'], 2),
            "atr": round(last['atr'], 4),
            "ema20": round(last['ema20'], 4),
            "ema50": round(last['ema50'], 4),
        }
    except Exception as e:
        print(f"Fehler bei {symbol}: {e}")
        return None