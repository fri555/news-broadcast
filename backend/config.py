import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── AI 服务 ──────────────────────────────────────────────
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# news-companion 兼容的 OpenAPI 格式 Key（优先用 DEEPSEEK_API_KEY）
API_KEY = os.getenv("API_KEY", "") or DEEPSEEK_API_KEY
API_BASE_URL = os.getenv("API_BASE_URL", "") or DEEPSEEK_BASE_URL + "/v1"
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

# ── TTS 语音 ─────────────────────────────────────────────
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge").lower()  # edge | openai | mimo
TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")
VOICE_A = os.getenv("TTS_VOICE_A", "zh-CN-XiaoxiaoNeural")
VOICE_B = os.getenv("TTS_VOICE_B", "zh-CN-YunxiNeural")

# OpenAI TTS（可选）
OPENAI_TTS_API_KEY = os.getenv("OPENAI_TTS_API_KEY", "")
OPENAI_TTS_BASE_URL = os.getenv("OPENAI_TTS_BASE_URL", "https://api.openai.com/v1")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")
OPENAI_TTS_VOICE_A = os.getenv("OPENAI_TTS_VOICE_A", "nova")
OPENAI_TTS_VOICE_B = os.getenv("OPENAI_TTS_VOICE_B", "onyx")

# ── MiMo TTS（小米，OpenAI 兼容接口）────────────────────
MIMO_TTS_API_KEY = os.getenv("MIMO_TTS_API_KEY", "")
MIMO_TTS_BASE_URL = os.getenv("MIMO_TTS_BASE_URL", "https://api.xiaomimimo.com/v1")
MIMO_TTS_MODEL = os.getenv("MIMO_TTS_MODEL", "mimo-v2.5-tts")
MIMO_TTS_VOICE = os.getenv("MIMO_TTS_VOICE", "mimo_default")
MIMO_TTS_VOICE_A = os.getenv("MIMO_TTS_VOICE_A", "茉莉")
MIMO_TTS_VOICE_B = os.getenv("MIMO_TTS_VOICE_B", "Milo")

# ── 新闻数据源 ───────────────────────────────────────────
DEFAULT_TOPICS = os.getenv("NEWS_TOPICS", "科技,财经,综合").split(",")
MAX_ITEMS_PER_SOURCE = int(os.getenv("MAX_ITEMS_PER_SOURCE", "12"))
BATCH_LIMIT = int(os.getenv("BATCH_LIMIT", "20"))
HOTBOARD_API = os.getenv("HOTBOARD_API", "https://uapis.cn/api/v1/misc/hotboard")
NEWSNOW_BASE_URL = os.getenv("NEWSNOW_BASE_URL", "https://newsnow.busiyi.world")
ENABLE_NEWSNOW = os.getenv("ENABLE_NEWSNOW", "1").lower() not in ("0", "false", "no")
NEWS_CACHE_TTL_HOURS = float(os.getenv("NEWS_CACHE_TTL_HOURS", "2"))
BROADCAST_CACHE_TTL_HOURS = float(os.getenv("BROADCAST_CACHE_TTL_HOURS", "12"))

# ── 预加载 ───────────────────────────────────────────────
ENABLE_PRELOAD = os.getenv("ENABLE_PRELOAD", "1").lower() not in ("0", "false", "no")
PRELOAD_TIMES = os.getenv("PRELOAD_TIMES", "06:00,17:00,21:00")
PRELOAD_TZ = os.getenv("PRELOAD_TZ", "Asia/Shanghai")

# ── RSS 源（兼容旧 news_fetcher）─────────────────────────
NEWS_SOURCES = os.getenv("NEWS_SOURCES", "")


def has_ai() -> bool:
    """检查 AI 服务是否已配置"""
    return bool(API_KEY and API_KEY not in ("", "your_api_key_here"))


def has_mimo_tts() -> bool:
    """检查 MiMo TTS 是否已配置"""
    return bool(MIMO_TTS_API_KEY and MIMO_TTS_API_KEY not in ("", "your_api_key_here"))
