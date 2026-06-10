"""
Text-to-Speech Service using ElevenLabs API
Professional multi-speaker voice generation
"""

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service with ElevenLabs"""
    
    def __init__(self, api_key: str = None):
        """Initialize TTS service"""
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "sk_33c17748cbd7ba62cc21225bb2e995d33844a7671dd4f115")
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Voice mapping for different speakers
        self.voice_map = {
            "Host": {
                "id": "pNInz6obpgDQGcFmaJgB",  # Adam - Professional male
                "type": "male",
                "personality": "professional"
            },
            "Alex": {
                "id": "pNInz6obpgDQGcFmaJgB",  # Adam - Friendly male
                "type": "male", 
                "personality": "friendly"
            },
            "Sam": {
                "id": "EXAVITQu4vr4xnSDxMaL",  # Bella - Warm female
                "type": "female",
                "personality": "warm"
            },
            "Jordan": {
                "id": "TxGEqnHWrfWFTfGW9XjX",  # Josh - Expert male
                "type": "male",
                "personality": "expert"
            },
            "Casey": {
                "id": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - Curious female
                "type": "female",
                "personality": "curious"
            }
        }
        
        # Default voice settings for natural speech
        self.voice_settings = VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.5,
            use_speaker_boost=True
        )
    
    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text for better voice modulation"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['wow', '!', 'amazing', 'incredible', 'kya baat']):
            return "excited"
        elif any(word in text_lower for word in ['?', 'kya', 'really', 'sach']):
            return "curious"
        else:
            return "neutral"
    
    def generate_audio(self, text: str, speaker: str, output_path: Path, language_style: str = "english") -> Path:
        """
        Generate audio for a dialogue
        
        Args:
            text: Dialogue text
            speaker: Speaker name (Host, Alex, Sam, etc.)
            output_path: Where to save the audio file
            language_style: english or hinglish (not used but kept for compatibility)
            
        Returns:
            Path to generated audio file
        """
        # Get voice for speaker
        voice_info = self.voice_map.get(speaker, self.voice_map["Host"])
        voice_id = voice_info["id"]
        
        # Detect emotion for better voice modulation
        emotion = self.detect_emotion(text)
        
        # Adjust voice settings based on emotion
        settings = VoiceSettings(
            stability=0.5 if emotion == "neutral" else 0.4,
            similarity_boost=0.75,
            style=0.6 if emotion == "excited" else 0.5,
            use_speaker_boost=True
        )
        
        logger.info(f"Generating audio for {speaker} ({emotion}): {text[:50]}...")
        
        try:
            # Generate audio using ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=settings
            )
            
            # Save audio to file
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            logger.info(f"✅ Audio generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise
