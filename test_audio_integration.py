"""
Test script to verify ElevenLabs audio integration
"""

import sys
sys.path.append('ai-blog-podcast/backend')

from services.tts_service import TTSService
from services.audio_merger import AudioMerger
from pathlib import Path

def test_audio_generation():
    """Test audio generation with ElevenLabs"""
    
    print("🎙️ Testing ElevenLabs Audio Integration\n")
    
    # Initialize TTS service
    print("1️⃣ Initializing TTS Service...")
    tts = TTSService()
    print("✅ TTS Service initialized\n")
    
    # Test script
    test_dialogues = [
        ("Alex", "Acha toh dekho yaar, aaj hum AI ke baare mein baat karte hain!"),
        ("Sam", "Wow! Bilkul sahi! AI bahut interesting topic hai."),
        ("Alex", "Dekho, AI ka matlab hai machines bhi soch sakti hain."),
        ("Sam", "Really? Aur yeh technology ab har jagah use ho rahi hai?"),
    ]
    
    # Generate audio segments
    print("2️⃣ Generating audio segments...")
    audio_files = []
    temp_dir = Path("ai-blog-podcast/backend/temp")
    temp_dir.mkdir(exist_ok=True)
    
    for i, (speaker, text) in enumerate(test_dialogues):
        output_path = temp_dir / f"test_segment_{i}_{speaker}.mp3"
        print(f"   Generating: {speaker}: {text[:40]}...")
        
        try:
            tts.generate_audio(text, speaker, output_path, "hinglish")
            audio_files.append(output_path)
            print(f"   ✅ Generated: {output_path.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print(f"\n✅ Generated {len(audio_files)} audio segments\n")
    
    # Merge audio
    print("3️⃣ Merging audio segments...")
    merger = AudioMerger()
    output_dir = Path("ai-blog-podcast/backend/outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_podcast.mp3"
    
    try:
        final_path, duration = merger.merge(audio_files, output_path)
        print(f"✅ Audio merged successfully!")
        print(f"📁 Output: {final_path}")
        print(f"⏱️  Duration: {duration:.1f} seconds\n")
    except Exception as e:
        print(f"❌ Merge error: {e}")
        return False
    
    # Cleanup temp files
    print("4️⃣ Cleaning up temp files...")
    for file in audio_files:
        if file.exists():
            file.unlink()
    print("✅ Cleanup complete\n")
    
    print("🎉 Test completed successfully!")
    print(f"🎧 Play the podcast: {output_path}")
    
    return True

if __name__ == "__main__":
    success = test_audio_generation()
    sys.exit(0 if success else 1)
