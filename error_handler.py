"""
Error handling utilities for podcast generation
"""

import logging
from typing import Optional, Dict, Any


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PodcastGenerationError(Exception):
    """Base exception for podcast generation errors"""
    pass


class OllamaConnectionError(PodcastGenerationError):
    """Raised when Ollama connection fails"""
    pass


class ModelNotFoundError(PodcastGenerationError):
    """Raised when specified model is not available"""
    pass


class AudioGenerationError(PodcastGenerationError):
    """Raised when audio generation fails"""
    pass


class ScriptValidationError(PodcastGenerationError):
    """Raised when generated script fails validation"""
    pass


def handle_ollama_error(error: Exception) -> Dict[str, Any]:
    """
    Handle Ollama-related errors
    
    Args:
        error: The exception that occurred
        
    Returns:
        Error response dictionary
    """
    logger.error(f"Ollama error: {str(error)}")
    
    if "connection" in str(error).lower():
        return {
            'success': False,
            'error': 'Cannot connect to Ollama. Please ensure Ollama is running.',
            'suggestion': 'Download from https://ollama.com/download'
        }
    elif "model" in str(error).lower():
        return {
            'success': False,
            'error': 'Model not found. Please pull the model first.',
            'suggestion': 'Run: ollama pull llama2'
        }
    else:
        return {
            'success': False,
            'error': f'Ollama error: {str(error)}',
            'suggestion': 'Check Ollama logs for details'
        }


def handle_audio_error(error: Exception) -> Dict[str, Any]:
    """
    Handle audio generation errors
    
    Args:
        error: The exception that occurred
        
    Returns:
        Error response dictionary
    """
    logger.error(f"Audio generation error: {str(error)}")
    
    return {
        'success': False,
        'error': f'Audio generation failed: {str(error)}',
        'suggestion': 'Ensure ffmpeg is installed and audio directories exist'
    }


def validate_input(content: str, title: Optional[str] = None) -> Optional[str]:
    """
    Validate user input
    
    Args:
        content: Blog content
        title: Optional title
        
    Returns:
        Error message if validation fails, None otherwise
    """
    if not content or not content.strip():
        return "Content cannot be empty"
    
    if len(content) < 50:
        return "Content is too short. Please provide at least 50 characters."
    
    if len(content) > 50000:
        return "Content is too long. Please limit to 50,000 characters."
    
    if title and len(title) > 200:
        return "Title is too long. Please limit to 200 characters."
    
    return None


def log_generation_stats(stats: Dict[str, Any]) -> None:
    """
    Log podcast generation statistics
    
    Args:
        stats: Dictionary containing generation statistics
    """
    logger.info(f"Podcast generated - Type: {stats.get('podcast_type')}, "
                f"Audience: {stats.get('audience')}, "
                f"Script length: {stats.get('script_length')} chars")
