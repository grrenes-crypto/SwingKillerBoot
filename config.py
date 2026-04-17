import os
from dotenv import load_dotenv

load_dotenv()

# Bybit API
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
BYBIT_TESTNET = os.getenv("BYBIT_TESTNET", "true").lower() == "true"

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"

# Qdrant (optional)
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# Trading-Parameter
TOP_COINS_LIMIT = 15
RISK_PERCENT_PER_TRADE = 2.0
ATR_STOP_MULTIPLIER = 1.5
ATR_TP_MULTIPLIER = 3.0

# Swing-Trading Erweiterungen
MAX_OPEN_POSITIONS = 3
TRAILING_ACTIVATION = 1.5
TRAILING_DISTANCE = 0.5
POSITIONS_FILE = "positions.json"

# Dynamischer Hebel Einstellungen
BASE_LEVERAGE = 5.0
MIN_LEVERAGE = 2.0
MAX_LEVERAGE = 20.0

# Guthaben‑Check
MIN_BALANCE_FOR_SCAN = 50.0
