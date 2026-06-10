from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()

class BlogPodcast(Base):
    __tablename__ = "blog_podcasts"
    
    id = Column(Integer, primary_key=True, index=True)
    blog_text = Column(Text, nullable=False)
    script = Column(Text, nullable=False)
    audio_path = Column(String, nullable=False)
    podcast_type = Column(String, nullable=False)  # single, cohost, multi
    audience = Column(String, nullable=False)  # india, global
    language_style = Column(String, nullable=False)  # english, hinglish
    duration = Column(Float, default=0.0)
    speaker_count = Column(Integer, default=1)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
