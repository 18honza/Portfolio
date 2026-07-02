"""Tiny JSON persistence layer for portfolio, trade plans and research files."""
import json
from pathlib import Path
from typing import Any

from src import config


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return default


def _save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def load_manual_portfolio() -> dict:
    return _load_json(config.PORTFOLIO_FILE, {"cash_czk": 0.0, "positions": []})


def save_manual_portfolio(portfolio: dict) -> None:
    _save_json(config.PORTFOLIO_FILE, portfolio)


def load_meta() -> dict:
    """Per-ticker trade plans: hard_stop, sell1, sell1_pct, sell2, catalyst, type, thesis."""
    return _load_json(config.META_FILE, {})


def save_meta(meta: dict) -> None:
    _save_json(config.META_FILE, meta)


def load_ticker_map() -> dict:
    """Manual overrides: Trading212 ticker (or short name) -> Yahoo Finance ticker."""
    return _load_json(config.TICKER_MAP_FILE, {})


def load_plays() -> dict:
    return _load_json(config.PLAYS_FILE, {})
