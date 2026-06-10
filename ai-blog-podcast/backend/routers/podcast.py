from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from models.database import get_db, BlogPodcast
from models.schemas import GenerateRequest, GenerateResponse, HistoryItem, PodcastMetadata
from services.podcast_service import PodcastService

router = APIRouter(prefix="/api", tags=["podcast"])
logger = logging.getLogger(__name__)

podcast_service = PodcastService()

@router.post("/generate", response_model=GenerateResponse)
async def generate_podcast(
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate podcast from blog text"""
    try:
        # Generate podcast
        result = podcast_service.generate_podcast(
            blog=request.blog,
            podcast_type=request.podcast_type,
            audience=request.audience,
            language_style=request.language_style
        )
        
        # Save to database
        podcast = BlogPodcast(
            blog_text=request.blog,
            script=result["script"],
            audio_path=str(result["audio_path"]),
            podcast_type=request.podcast_type,
            audience=request.audience,
            language_style=request.language_style,
            duration=result["duration"],
            speaker_count=len(result["speakers"]),
            word_count=result["word_count"]
        )
        db.add(podcast)
        db.commit()
        db.refresh(podcast)
        
        # Build response
        return GenerateResponse(
            id=podcast.id,
            script=result["script"],
            audio_url=f"/outputs/{result['audio_path'].name}",
            metadata=PodcastMetadata(
                speakers=result["speakers"],
                duration=result["duration"],
                word_count=result["word_count"],
                speaker_count=len(result["speakers"])
            )
        )
    
    except Exception as e:
        logger.error(f"Error generating podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[HistoryItem])
async def get_history(db: Session = Depends(get_db)):
    """Get list of generated podcasts"""
    podcasts = db.query(BlogPodcast).order_by(BlogPodcast.created_at.desc()).limit(50).all()
    
    return [
        HistoryItem(
            id=p.id,
            blog_text=p.blog_text[:200] + "..." if len(p.blog_text) > 200 else p.blog_text,
            podcast_type=p.podcast_type,
            audience=p.audience,
            language_style=p.language_style,
            duration=p.duration,
            created_at=p.created_at,
            audio_url=f"/outputs/{p.audio_path.split('/')[-1]}"
        )
        for p in podcasts
    ]
