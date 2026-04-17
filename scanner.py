import pandas as pd
import ta
import time
import requests
from pybit.unified_trading import HTTP
from config import *

class TimeSyncHTTP(HTTP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_offset = 0
        self._sync_time()

    def _sync_time(self):
        try:
            response = requests.get("https://api.bybit.com/v5/market/time")
            server_time = int(response.json()["result"]["timeSecond"])
            local_time = int(time.time())
            self.time_offset = server_time - local_time
            print(f"🕒 Zeitsynchronisation: Offset={self.time_offset}s")
        except Exception as e:
            print(f"⚠️ Zeitsynchronisation fehlgeschlagen: {e}")

    def _get_timestamp(self):
        return str(int((time.time() + self.time_offset) * 1000))

    def _submit_request(self, method, path, params):
        timestamp = self._get_timestamp()
        recv_window = "5000"
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        signature_payload = timestamp + self.api_key + recv_window + param_str
        import hmac
        import hashlib
        signature = hmac.new(
            bytes(self.api_secret, "utf-8"),
            bytes(signature_payload, "utf-8"),
            hashlib.sha256
        ).hexdigest()
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": recv_window,
        }
        url = f"https://api.bybit.com{path}"
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params)
        else:
            resp = requests.post(url, headers=headers, json=params)
        return resp.json()

session = TimeSyncHTTP(testnet=BYBIT_TESTNET, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

def get_top_coins(limit=TOP_COINS_LIMIT):
    tickers = session.get_tickers(category="linear")["result"]["list"]
    df = pd.DataFrame(tickers)
    df["turnover24h"] = df["turnover24h"].astype(float)
    return df.nlargest(limit, "turnover24h")["symbol"].tolist()

def get_daily_trend(symbol):
    try:
        resp = session.get_kline(category="linear", symbol=symbol, interval="D", limit=100)
        df = pd.DataFrame(resp["result"]["list"],
                          columns=['timestamp','open','high','low','close','volume','turnover'])
        df['close'] = df['close'].astype(float)
        df = df.iloc[::-1].reset_index(drop=True)
        df['ema20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
        df['ema50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()
        return df['ema20'].iloc[-1] > df['ema50'].iloc[-1]
    except:
        return False

def get_market_data(symbol):
    try:
        resp = session.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        df = pd.DataFrame(resp["result"]["list"],
                          columns=['timestamp','open','high','low','close','volume','turnover'])
        for col in ['open','high','low','close']:
            df[col] = df[col].astype(float)
        df = df.iloc[::-1].reset_index(drop=True)

        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        df['ema20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
        df['ema50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()
        df['atr'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'],
                                                   close=df['close'], window=14).average_true_range()

        last = df.iloc[-1]
        trend_up = get_daily_trend(symbol)

        return {
            "symbol": symbol,
            "price": round(last['close'], 4),
            "rsi": round(last['rsi'], 2),
            "atr": round(last['atr'], 4),
            "ema20": round(last['ema20'], 4),
            "ema50": round(last['ema50'], 4),
            "trend_up": trend_up
        }
    except Exception as e:
        print(f"Fehler bei {symbol}: {e}")
        return None
