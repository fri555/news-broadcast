from pydantic import BaseModel, Field
from typing import Optional, Literal


# ── 新闻 ──────────────────────────────────────────────────

class NewsItem(BaseModel):
    id: str
    title: str
    summary: str = ""
    detail: dict = Field(default_factory=dict)
    read_aloud: str = ""          # 口语化播报文本（TTS 用）
    image: str = ""
    source: str = ""
    sourceUrl: str = "#"
    topic: str = "综合"           # 领域分类
    category: str = ""            # 兼容旧字段（topic 别名）
    publishedAt: str = ""
    hot_value: str = ""           # 热度值
    isRead: bool = False


# ── 播客 / 双主播 ─────────────────────────────────────────

class BroadcastScriptLine(BaseModel):
    speaker: Literal["A", "B"]
    text: str


class BroadcastResult(BaseModel):
    script: list[BroadcastScriptLine]
    voice_a: str
    voice_b: str
    total_chars: int
    estimated_minutes: float
    cached: bool = False
    cache_time: str = ""


class BroadcastNewsItem(BaseModel):
    title: str
    summary: str = ""
    source: str = ""
    topic: str = ""


class BroadcastRequest(BaseModel):
    news: list[BroadcastNewsItem]


# ── 播客兼容旧模型 ────────────────────────────────────────

class PodcastChapter(BaseModel):
    id: str
    title: str
    startTime: int


class TranscriptLine(BaseModel):
    speaker: str
    text: str
    startTime: int
    endTime: int


class PodcastHost(BaseModel):
    name: str
    gender: Literal["female", "male"]
    voiceColor: str


class PodcastEpisode(BaseModel):
    id: str
    title: str
    date: str
    duration: int
    hosts: list[PodcastHost]
    chapters: list[PodcastChapter]
    transcript: list[TranscriptLine]


# ── AI 追问 ───────────────────────────────────────────────

class AskRequest(BaseModel):
    message: str
    context: Optional[dict] = None
    history: list[dict] = []


class ChatMessage(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: int
    context: Optional[dict] = None


# ── TTS ───────────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    rate: str = "+4%"
    pitch: str = "+3Hz"
    style: str = "news"   # news | hostA | hostB | answer


# ── 领域 ──────────────────────────────────────────────────

class TopicsResponse(BaseModel):
    all: list[str]
    defaults: list[str]
