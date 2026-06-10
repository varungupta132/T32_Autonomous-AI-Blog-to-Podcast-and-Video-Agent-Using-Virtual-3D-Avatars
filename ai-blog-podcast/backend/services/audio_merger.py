from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

class AudioMerger:
    """Merge multiple audio segments into final podcast with professional effects"""
    
    def __init__(self, silence_duration: int = 800):
        """
        Args:
            silence_duration: Milliseconds of silence between clips (default 800ms for natural pauses)
        """
        self.silence_duration = silence_duration
    
    def merge(self, audio_files: List[Path], output_path: Path) -> tuple[Path, float]:
        """
        Merge audio files sequentially with natural pauses and professional effects
        
        Returns:
            (output_path, duration_in_seconds)
        """
        if not audio_files:
            raise ValueError("No audio files to merge")
        
        logger.info(f"Merging {len(audio_files)} audio segments...")
        
        # Create silence segment for natural pauses
        silence = AudioSegment.silent(duration=self.silence_duration)
        
        # Start with first audio
        combined = AudioSegment.from_file(audio_files[0])
        combined = self._apply_effects(combined)
        
        # Add remaining audio files with silence
        for i, audio_file in enumerate(audio_files[1:], 1):
            try:
                audio = AudioSegment.from_file(audio_file)
                audio = self._apply_effects(audio)
                combined = combined + silence + audio
                logger.info(f"Merged segment {i+1}/{len(audio_files)}")
            except Exception as e:
                logger.error(f"Error loading audio file {audio_file}: {e}")
                continue
        
        # Final normalization and compression
        logger.info("Applying final audio processing...")
        combined = normalize(combined)
        combined = compress_dynamic_range(combined)
        
        # Export final audio with high quality
        logger.info(f"Exporting to {output_path}...")
        combined.export(
            output_path,
            format="mp3",
            bitrate="192k",
            parameters=["-q:a", "0"]  # Highest quality
        )
        
        duration = len(combined) / 1000.0  # Convert to seconds
        
        logger.info(f"✅ Audio merged successfully! Duration: {duration:.1f}s")
        
        return output_path, duration
    
    def _apply_effects(self, audio: AudioSegment) -> AudioSegment:
        """Apply professional audio effects to segment"""
        # Normalize volume
        audio = normalize(audio)
        
        # Compress dynamic range for consistent volume
        audio = compress_dynamic_range(audio)
        
        return audio
    
    @staticmethod
    def get_duration(audio_path: Path) -> float:
        """Get audio duration in seconds"""
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
