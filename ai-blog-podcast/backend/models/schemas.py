from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class GenerateRequest(BaseModel):
    blog: str = Field(..., max_length=10000)
    podcast_type: str = Field(..., pattern="^(single|cohost|multi)$")
    audience: str = Field(..., pattern="^(india|global)$")
    language_style: str = Field(..., pattern="^(english|hinglish)$")

class SpeakerDialogue(BaseModel):
    speaker: str
    text: str

class PodcastMetadata(BaseModel):
    speakers: List[str]
    duration: float
    word_count: int
    speaker_count: int

class GenerateResponse(BaseModel):
    id: int
    script: str
    audio_url: str
    metadata: PodcastMetadata

class HistoryItem(BaseModel):
    id: int
    blog_text: str
    podcast_type: str
    audience: str
    language_style: str
    duration: float
    created_at: datetime
    audio_url: str
    
    class Config:
        from_attributes = True
