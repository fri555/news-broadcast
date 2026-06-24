"""User preferences API — server-side JSON file storage."""
import json
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/preferences", tags=["preferences"])

DATA_DIR = Path(__file__).parent.parent / "data" / "prefs"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class CompanionSettings(BaseModel):
    name: str = "小暖"
    personality: str = "亲和温暖"
    voiceId: str = "mimo_default"
    voiceA: str = "茉莉"
    voiceB: str = "Milo"
    speed: float = 1.0
    addressAs: str = "朋友"


class UserPreferences(BaseModel):
    userId: str = "default"
    interests: list[str] = ["科技", "财经", "国际", "AI", "创投"]
    newsSources: list[str] = []
    pushTimes: list[str] = ["8:00", "18:00", "22:00"]
    theme: str = "theme-warm"
    companion: CompanionSettings = CompanionSettings()


def _file(user_id: str) -> Path:
    safe = user_id.replace("/", "_").replace("..", "_") or "default"
    return DATA_DIR / f"{safe}.json"


def _read(user_id: str) -> dict:
    f = _file(user_id)
    if f.exists():
        return json.loads(f.read_text())
    return {}


def _write(user_id: str, data: dict):
    _file(user_id).write_text(json.dumps(data, ensure_ascii=False, indent=2))


@router.get("/{user_id}")
async def get_prefs(user_id: str) -> dict:
    """Load user preferences from server storage."""
    data = _read(user_id)
    if not data:
        # Return defaults
        defaults = UserPreferences(userId=user_id)
        return defaults.model_dump()
    return data


@router.put("/{user_id}")
async def save_prefs(user_id: str, prefs: dict):
    """Save user preferences to server storage."""
    existing = _read(user_id)
    existing.update(prefs)
    existing["userId"] = user_id
    _write(user_id, existing)
    return {"status": "ok", "userId": user_id}
