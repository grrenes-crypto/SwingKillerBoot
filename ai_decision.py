import json
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

def ask_deepseek(data):
    prompt = f"""
Du bist ein Swing-Trading-Experte. Analysiere:
Symbol: {data['symbol']}
Preis: {data['price']}
RSI (1h): {data['rsi']}
ATR: {data['atr']}
EMA20 (1h): {data['ema20']}
EMA50 (1h): {data['ema50']}
Tages-Trend (EMA20 > EMA50): {data['trend_up']}

Der Tages-Trend MUSS aufwärts sein für einen LONG-Trade.
Soll jetzt ein LONG-Trade eröffnet werden? Antworte NUR im JSON-Format:
{{"action": "BUY" oder "HOLD", "confidence": 0.0-1.0, "stop_loss": Zahl, "take_profit": Zahl, "reasoning": "..."}}
"""
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = resp.choices[0].message.content.strip()
        if content.startswith("```"): content = content.split("\n",1)[1].rsplit("\n",1)[0]
        return json.loads(content)
    except Exception as e:
        print(f"DeepSeek Fehler: {e}")
        return None
