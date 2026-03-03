"""
🎙️ STANDALONE AI PODCAST GENERATOR
Complete audio generation system in ONE file
No external dependencies from other folders - everything is here!

Author: AI Assistant
Date: March 3, 2026
"""

import re
from pathlib import Path
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# ============================================================================
# CONFIGURATION
# ============================================================================

# ElevenLabs API Key
ELEVENLABS_API_KEY = "sk_33c17748cbd7ba62cc21225bb2e995d33844a7671dd4f115"

# Voice mapping for different speakers
VOICE_MAP = {
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

# Output directories
OUTPUT_DIR = Path("generated_podcasts")
TEMP_DIR = Path("temp_audio")


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def parse_script(script):
    """
    Parse script and extract speakers and dialogues
    
    Args:
        script: Multi-line string with format "Speaker: Dialogue"
        
    Returns:
        List of tuples: [(speaker, dialogue), ...]
    """
    dialogues = []
    lines = script.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if ':' in line and len(line) > 10:
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip()
                dialogue = parts[1].strip()
                if dialogue:
                    dialogues.append((speaker, dialogue))
    
    return dialogues


def get_unique_speakers(dialogues):
    """Get list of unique speakers from dialogues"""
    speakers = list(set([d[0] for d in dialogues]))
    return sorted(speakers)


def detect_emotion(text):
    """
    Detect emotion from text for better voice modulation
    
    Args:
        text: Dialogue text
        
    Returns:
        "excited", "curious", or "neutral"
    """
    text_lower = text.lower()
    
    # Check for excitement indicators
    if any(word in text_lower for word in ['wow', '!', 'amazing', 'incredible', 'kya baat', 'zabardast']):
        return "excited"
    
    # Check for curiosity indicators
    elif any(word in text_lower for word in ['?', 'kya', 'really', 'sach', 'how', 'why']):
        return "curious"
    
    # Default neutral
    else:
        return "neutral"


def generate_audio_segment(client, speaker, text, output_path):
    """
    Generate audio for a single dialogue using ElevenLabs
    
    Args:
        client: ElevenLabs client instance
        speaker: Speaker name (Alex, Sam, etc.)
        text: Dialogue text
        output_path: Where to save the audio file
        
    Returns:
        Path to generated audio file
    """
    # Get voice for speaker (default to Host if not found)
    voice_info = VOICE_MAP.get(speaker, VOICE_MAP["Host"])
    voice_id = voice_info["id"]
    
    # Detect emotion for better voice modulation
    emotion = detect_emotion(text)
    
    # Adjust voice settings based on emotion
    if emotion == "excited":
        settings = VoiceSettings(
            stability=0.4,
            similarity_boost=0.75,
            style=0.6,
            use_speaker_boost=True
        )
    elif emotion == "curious":
        settings = VoiceSettings(
            stability=0.4,
            similarity_boost=0.75,
            style=0.5,
            use_speaker_boost=True
        )
    else:  # neutral
        settings = VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.5,
            use_speaker_boost=True
        )
    
    # Generate audio using ElevenLabs
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=settings
    )
    
    # Save audio to file
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)
    
    return output_path


def merge_audio_files(audio_files, output_file):
    """
    Simple MP3 concatenation without FFmpeg
    
    Args:
        audio_files: List of Path objects to audio files
        output_file: Path where to save merged audio
        
    Returns:
        Path to merged audio file
    """
    with open(output_file, 'wb') as outfile:
        for mp3_file in audio_files:
            with open(mp3_file, 'rb') as infile:
                outfile.write(infile.read())
    
    return output_file


def cleanup_temp_files(files):
    """Delete temporary audio files"""
    for file in files:
        if file.exists():
            file.unlink()


# ============================================================================
# MAIN PODCAST GENERATOR
# ============================================================================

def generate_podcast(script, output_name="podcast", cleanup=True):
    """
    Generate complete podcast from script
    
    Args:
        script: Multi-line string with "Speaker: Dialogue" format
        output_name: Name for output file (without extension)
        cleanup: Whether to delete temp files after merging
        
    Returns:
        Path to generated podcast MP3 file
    """
    
    print("🎙️ AI PODCAST GENERATOR")
    print("="*60)
    
    # Step 1: Parse script
    print("\n📝 Step 1: Parsing Script...")
    dialogues = parse_script(script)
    speakers = get_unique_speakers(dialogues)
    
    if not dialogues:
        print("❌ Error: No valid dialogues found in script!")
        print("   Format should be: Speaker: Dialogue")
        return None
    
    print(f"✅ Found {len(dialogues)} dialogues")
    print(f"✅ Speakers: {', '.join(speakers)}")
    
    # Step 2: Initialize ElevenLabs client
    print("\n🎤 Step 2: Initializing TTS Service...")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    print("✅ ElevenLabs client ready")
    
    # Step 3: Create directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Step 4: Generate audio segments
    print("\n🎵 Step 3: Generating Audio Segments...")
    audio_files = []
    
    for i, (speaker, dialogue) in enumerate(dialogues):
        output_path = TEMP_DIR / f"{output_name}_segment_{i}_{speaker}.mp3"
        
        # Show progress
        emotion = detect_emotion(dialogue)
        print(f"\n   [{i+1}/{len(dialogues)}] {speaker} ({emotion})")
        print(f"   💬 {dialogue[:60]}{'...' if len(dialogue) > 60 else ''}")
        
        try:
            generate_audio_segment(client, speaker, dialogue, output_path)
            audio_files.append(output_path)
            print(f"   ✅ Generated: {output_path.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    if not audio_files:
        print("\n❌ Error: No audio segments were generated!")
        return None
    
    print(f"\n✅ Generated {len(audio_files)}/{len(dialogues)} audio segments")
    
    # Step 5: Merge audio
    print("\n🔧 Step 4: Merging Audio...")
    output_file = OUTPUT_DIR / f"{output_name}.mp3"
    
    merge_audio_files(audio_files, output_file)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    print(f"✅ Merged successfully!")
    print(f"📁 Output: {output_file}")
    print(f"💿 Size: {file_size:.2f} MB")
    
    # Step 6: Cleanup
    if cleanup:
        print("\n🧹 Step 5: Cleaning up temp files...")
        cleanup_temp_files(audio_files)
        print("✅ Cleanup complete")
    
    # Summary
    print("\n" + "="*60)
    print("🎉 PODCAST GENERATION COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   • Speakers: {len(speakers)}")
    print(f"   • Dialogues: {len(dialogues)}")
    print(f"   • Audio Segments: {len(audio_files)}")
    print(f"   • Output File: {output_file.name}")
    print(f"   • File Size: {file_size:.2f} MB")
    print(f"\n🎧 Play your podcast:")
    print(f"   {output_file.absolute()}")
    
    return output_file


# ============================================================================
# TEST SCRIPTS
# ============================================================================

# Test Script 1: Hinglish Co-host (AI Topic)
SCRIPT_HINGLISH = """
Alex: Acha toh dekho yaar, aaj hum AI ke baare mein baat karte hain!

Sam: Wow! Bilkul sahi! AI bahut interesting topic hai yaar.

Alex: Dekho, AI ka matlab hai machines bhi soch sakti hain aur seekh sakti hain.

Sam: Really? Aur yeh technology ab har jagah use ho rahi hai?

Alex: Exactly! Education mein, healthcare mein, business mein - har jagah AI ka use ho raha hai.

Sam: Amazing! Toh humein AI ko responsibly use karna chahiye, right?

Alex: Bilkul sahi! Thank you sabko sunne ke liye.

Sam: Shukriya! Phir milenge, take care!
"""

# Test Script 2: English Co-host (Technology)
SCRIPT_ENGLISH = """
Alex: Welcome everyone to our technology podcast!

Sam: Thanks for having me! I'm excited to discuss AI today.

Alex: AI is transforming how we work and live every single day.

Sam: Absolutely! From voice assistants to self-driving cars, it's everywhere.

Alex: The future of AI looks incredibly promising, doesn't it?

Sam: Yes! But we must ensure ethical development and responsible use.

Alex: Well said! Thanks for joining us today.

Sam: Thank you! See you next time, everyone!
"""

# Test Script 3: Multi-speaker (3 people)
SCRIPT_MULTI = """
Alex: Hello everyone! Today we have a special guest with us.

Sam: Hi! I'm so excited to be here talking about AI.

Jordan: Thanks for inviting me! AI is my favorite topic.

Alex: Jordan, can you explain what machine learning is?

Jordan: Sure! Machine learning is when computers learn from data without explicit programming.

Sam: That's fascinating! So computers can actually learn on their own?

Jordan: Exactly! They identify patterns and make decisions based on that data.

Alex: Amazing! This technology is revolutionizing every industry.

Sam: I can see why AI is so important for our future.

Jordan: Absolutely! The possibilities are truly endless.

Alex: Thank you both for this wonderful discussion!

Sam: It was great! Thanks for having us.

Jordan: My pleasure! Looking forward to next time.
"""


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🎙️  STANDALONE PODCAST GENERATOR")
    print(" Everything in ONE file - No external dependencies!")
    print("="*60)
    
    print("\nWhich test would you like to run?")
    print("1. Hinglish Co-host (AI Topic) - 8 dialogues")
    print("2. English Co-host (Technology) - 8 dialogues")
    print("3. Multi-speaker (3 people) - 13 dialogues")
    print("4. Custom script (paste your own)")
    print("5. All tests")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        generate_podcast(SCRIPT_HINGLISH, "hinglish_cohost")
        
    elif choice == "2":
        generate_podcast(SCRIPT_ENGLISH, "english_cohost")
        
    elif choice == "3":
        generate_podcast(SCRIPT_MULTI, "multi_speaker")
        
    elif choice == "4":
        print("\n📝 Paste your script (format: Speaker: Dialogue)")
        print("Press Enter twice when done:\n")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        custom_script = "\n".join(lines)
        
        if custom_script.strip():
            output_name = input("\nOutput filename (without .mp3): ").strip() or "custom_podcast"
            generate_podcast(custom_script, output_name)
        else:
            print("❌ No script provided!")
            
    elif choice == "5":
        print("\n🚀 Running all tests...\n")
        generate_podcast(SCRIPT_HINGLISH, "test1_hinglish")
        print("\n" + "="*60 + "\n")
        generate_podcast(SCRIPT_ENGLISH, "test2_english")
        print("\n" + "="*60 + "\n")
        generate_podcast(SCRIPT_MULTI, "test3_multi")
        
    else:
        print("❌ Invalid choice!")
    
    print("\n✨ All done! Check 'generated_podcasts' folder! ✨\n")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
USAGE EXAMPLES:

1. Run from command line:
   python standalone_podcast_generator.py

2. Use in your code:
   from standalone_podcast_generator import generate_podcast
   
   script = '''
   Alex: Hello everyone!
   Sam: Hi there!
   '''
   
   generate_podcast(script, "my_podcast")

3. Custom script:
   script = '''
   Host: Welcome to the show!
   Alex: Thanks for having me!
   Sam: Excited to be here!
   '''
   
   podcast_file = generate_podcast(script, "custom_show")
   print(f"Generated: {podcast_file}")

4. Available speakers:
   - Host (Male, Professional)
   - Alex (Male, Friendly)
   - Sam (Female, Warm)
   - Jordan (Male, Expert)
   - Casey (Female, Curious)

5. Emotion detection:
   - "Wow!" or "Amazing!" → Excited voice
   - "Really?" or "Kya?" → Curious voice
   - Normal text → Neutral voice

6. Output location:
   - Podcasts saved in: generated_podcasts/
   - Temp files in: temp_audio/ (auto-deleted)

7. Requirements:
   pip install elevenlabs

That's it! Everything else is in this file!
"""
