"""
Utility functions for podcast generation
"""

import re
import os
from typing import List, Dict


def clean_script_text(script: str) -> str:
    """
    Remove unwanted characters and formatting from generated script
    
    Args:
        script: Raw script text from AI model
        
    Returns:
        Cleaned script text
    """
    # Remove emojis
    script = re.sub(r'[^\x00-\x7F]+', '', script)
    
    # Remove stage directions
    script = re.sub(r'\*[^*]+\*', '', script)
    script = re.sub(r'\([^)]+\)', '', script)
    script = re.sub(r'\[[^\]]+\]', '', script)
    
    # Remove music/sound cues
    script = script.replace('[INTRO MUSIC', '').replace('[OUTRO MUSIC', '')
    script = script.replace('[MUSIC]', '').replace('[SOUND', '')
    
    # Clean up extra spaces
    script = re.sub(r'\s+', ' ', script)
    script = re.sub(r' +\n', '\n', script)
    script = re.sub(r'\n+', '\n', script)
    
    return script.strip()


def normalize_speaker_labels(script: str) -> str:
    """
    Standardize speaker labels in script
    
    Args:
        script: Script text with inconsistent labels
        
    Returns:
        Script with normalized labels
    """
    replacements = {
        'Host 1:': 'Alex:',
        'Host 2:': 'Sam:',
        'Host1:': 'Alex:',
        'Host2:': 'Sam:',
        'Host 1 :': 'Alex:',
        'Host 2 :': 'Sam:',
    }
    
    for old, new in replacements.items():
        script = script.replace(old, new)
    
    return script


def validate_script_lines(script: str) -> List[str]:
    """
    Extract and validate script lines
    
    Args:
        script: Complete script text
        
    Returns:
        List of valid script lines
    """
    lines = []
    for line in script.split('\n'):
        line = line.strip()
        if line and ':' in line and len(line) > 10:
            parts = line.split(':', 1)
            if len(parts) == 2 and len(parts[1].strip()) > 5:
                lines.append(line)
    
    return lines


def ensure_directories_exist(directories: List[str]) -> None:
    """
    Create directories if they don't exist
    
    Args:
        directories: List of directory paths to create
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def format_filename(title: str, podcast_type: str, audience: str, extension: str = "txt") -> str:
    """
    Generate standardized filename
    
    Args:
        title: Podcast title
        podcast_type: Type of podcast
        audience: Target audience
        extension: File extension
        
    Returns:
        Formatted filename
    """
    safe_title = title.replace(' ', '_').replace('/', '_').replace('\\', '_')
    return f"podcast_{podcast_type}_{audience}_{safe_title}.{extension}"
