from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    title = Column(String(300), nullable=True)
    podcast_type = Column(String(20), nullable=False)   # single / co-host / multi-host
    audience = Column(String(20), nullable=False)       # global / indian
    script = Column(Text, nullable=True)
    filename = Column(String(300), nullable=True)
    file_size_mb = Column(Float, nullable=True)
    total_segments = Column(Integer, nullable=True)
    speakers = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")      # pending / done / failed


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
