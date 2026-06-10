from pathlib import Path
from typing import List, Dict
import uuid
import logging
from .llm_service import LLMService
from .script_parser import ScriptParser
from .tts_service import TTSService

# Try to use full audio merger, fall back to simple version
try:
    from .audio_merger import AudioMerger
    FULL_AUDIO_SUPPORT = True
except ImportError:
    from .simple_audio_merger import SimpleAudioMerger as AudioMerger
    FULL_AUDIO_SUPPORT = False
    
from config import settings

logger = logging.getLogger(__name__)

if not FULL_AUDIO_SUPPORT:
    logger.warning("FFmpeg not available. Using simplified audio processing. Install FFmpeg for full functionality.")

class PodcastService:
    """Main service orchestrating podcast generation"""
    
    def __init__(self):
        self.llm = LLMService()
        self.parser = ScriptParser()
        self.tts = TTSService()
        self.merger = AudioMerger()
    
    def generate_podcast(
        self,
        blog: str,
        podcast_type: str,
        audience: str,
        language_style: str
    ) -> Dict:
        """
        Complete podcast generation pipeline
        
        Returns:
            {
                "script": str,
                "audio_path": Path,
                "dialogues": List[Dict],
                "speakers": List[str],
                "duration": float,
                "word_count": int
            }
        """
        
        # Step 1: Generate script using LLM
        logger.info("Generating script with LLM...")
        script = self.llm.generate_script(blog, podcast_type, audience, language_style)
        
        # Step 2: Parse script into dialogues
        logger.info("Parsing script...")
        dialogues = self.parser.parse(script)
        
        if not dialogues:
            raise ValueError("Failed to parse script. No valid dialogues found.")
        
        speakers = self.parser.get_speakers(dialogues)
        word_count = self.parser.get_word_count(dialogues)
        
        logger.info(f"Found {len(dialogues)} dialogues from {len(speakers)} speakers")
        
        # Step 3: Generate audio for each dialogue
        logger.info("Generating audio segments...")
        audio_files = self._generate_audio_segments(dialogues)
        
        # Step 4: Merge audio files
        logger.info("Merging audio segments...")
        podcast_id = str(uuid.uuid4())
        output_path = settings.output_dir / f"podcast_{podcast_id}.mp3"
        
        final_audio, duration = self.merger.merge(audio_files, output_path)
        
        # Step 5: Cleanup temp files
        self._cleanup_temp_files(audio_files)
        
        logger.info(f"Podcast generated successfully: {output_path}")
        
        return {
            "script": script,
            "audio_path": final_audio,
            "dialogues": dialogues,
            "speakers": speakers,
            "duration": duration,
            "word_count": word_count
        }
    
    def _generate_audio_segments(self, dialogues: List[Dict]) -> List[Path]:
        """Generate audio file for each dialogue"""
        audio_files = []
        
        for idx, dialogue in enumerate(dialogues):
            speaker = dialogue["speaker"]
            text = dialogue["text"]
            
            # Generate unique filename
            temp_file = settings.temp_dir / f"segment_{idx}_{speaker}.wav"
            
            try:
                audio_path = self.tts.generate_audio(text, speaker, temp_file)
                audio_files.append(audio_path)
                logger.info(f"Generated audio {idx+1}/{len(dialogues)}: {speaker}")
            except Exception as e:
                logger.error(f"Failed to generate audio for dialogue {idx}: {e}")
                # Continue with other dialogues
                continue
        
        return audio_files
    
    def _cleanup_temp_files(self, files: List[Path]):
        """Remove temporary audio files"""
        for file in files:
            try:
                if file.exists():
                    file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file}: {e}")
