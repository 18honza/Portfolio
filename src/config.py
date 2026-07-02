import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
RESEARCH_DIR = ROOT / "research"
CACHE_DIR = DATA_DIR / ".cache"

PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
META_FILE = DATA_DIR / "positions_meta.json"
TICKER_MAP_FILE = DATA_DIR / "ticker_map.json"
PLAYS_FILE = RESEARCH_DIR / "plays.json"

ACCOUNT_CURRENCY = "CZK"
DEFAULT_RISK_FREE = 0.035  # ~CNB repo territory; adjustable in the sidebar
DEFAULT_BENCHMARK = "SPY"
PRICE_CACHE_TTL = 300  # seconds — prices auto-refresh on this cadence

T212_API_KEY = os.getenv("T212_API_KEY", "")
T212_BASE_URL = os.getenv("T212_BASE_URL", "https://live.trading212.com/api/v0")
