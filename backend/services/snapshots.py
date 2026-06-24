"""Small JSON snapshot helpers for precomputed news and podcast data."""
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config import NEWS_CACHE_TTL_HOURS, BROADCAST_CACHE_TTL_HOURS

DATA_DIR = Path(__file__).parent.parent / "data" / "current"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def news_snapshot_path(topics: list[str], limit: int) -> Path:
    key = ",".join(sorted(topics)) + f"|{limit}"
    return DATA_DIR / f"news-{_safe_name(key)}.json"


def podcast_snapshot_path() -> Path:
    return DATA_DIR / "podcast-latest.json"


def _read_json(path: Path, ttl_hours: float) -> Optional[dict]:
    if not path.exists() or path.stat().st_size <= 10:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        generated_at = data.get("generated_at", "")
        if generated_at:
            ts = datetime.fromisoformat(generated_at)
            if datetime.now() - ts > timedelta(hours=ttl_hours):
                data["is_stale"] = True
            else:
                data["is_stale"] = False
        data["cached"] = True
        return data
    except Exception:
        return None


def read_news_snapshot(topics: list[str], limit: int) -> Optional[dict]:
    return _read_json(news_snapshot_path(topics, limit), NEWS_CACHE_TTL_HOURS)


def read_latest_news_snapshot() -> Optional[dict]:
    paths = sorted(DATA_DIR.glob("news-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths:
        data = _read_json(path, NEWS_CACHE_TTL_HOURS)
        if data and data.get("news"):
            data["cache_fallback"] = True
            return data
    return None


def write_news_snapshot(topics: list[str], limit: int, data: dict) -> None:
    payload = dict(data)
    payload["generated_at"] = datetime.now().isoformat(timespec="seconds")
    payload["is_stale"] = False
    news_snapshot_path(topics, limit).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_podcast_snapshot() -> Optional[dict]:
    return _read_json(podcast_snapshot_path(), BROADCAST_CACHE_TTL_HOURS)


def write_podcast_snapshot(data: dict) -> None:
    payload = dict(data)
    payload["generated_at"] = datetime.now().isoformat(timespec="seconds")
    payload["is_stale"] = False
    podcast_snapshot_path().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
