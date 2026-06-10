from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from config import settings
from models.database import init_db
from routers import podcast

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# FastAPI app
app = FastAPI(
    title="AI Blog-to-Podcast Agent",
    description="Convert blog posts into podcast audio with virtual avatars",
    version="1.0.0"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for audio outputs
app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")

# Routers
app.include_router(podcast.router)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")
    logger.info(f"Server starting on port {settings.backend_port}")

@app.get("/")
async def root():
    return {"message": "AI Blog-to-Podcast Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
