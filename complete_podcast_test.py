"""
Complete Podcast Audio Generation Test
Automatically detects speakers and generates natural conversation
"""

import sys
import re
from pathlib import Path

sys.path.append('ai-blog-podcast/backend')

from services.tts_service import TTSService

def parse_script(script):
    """Parse script and extract speakers and dialogues"""
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
    """Get list of unique speakers"""
    speakers = list(set([d[0] for d in dialogues]))
    return sorted(speakers)

def simple_merge_mp3(input_files, output_file):
    """Simple MP3 concatenation"""
    with open(output_file, 'wb') as outfile:
        for mp3_file in input_files:
            with open(mp3_file, 'rb') as infile:
                outfile.write(infile.read())
    return output_file

def generate_podcast(script, output_name="podcast"):
    """Generate complete podcast from script"""
    
    print("🎙️ AI Podcast Generator - Complete Test\n")
    print("="*50)
    
    # Parse script
    print("\n📝 Step 1: Parsing Script...")
    dialogues = parse_script(script)
    speakers = get_unique_speakers(dialogues)
    
    print(f"✅ Found {len(dialogues)} dialogues")
    print(f"✅ Speakers: {', '.join(speakers)}")
    
    # Initialize TTS
    print("\n🎤 Step 2: Initializing TTS Service...")
    tts = TTSService()
    print("✅ TTS Service ready with ElevenLabs")
    
    # Generate audio segments
    print("\n🎵 Step 3: Generating Audio Segments...")
    temp_dir = Path("ai-blog-podcast/backend/temp")
    temp_dir.mkdir(exist_ok=True)
    
    audio_files = []
    
    for i, (speaker, dialogue) in enumerate(dialogues):
        output_path = temp_dir / f"{output_name}_segment_{i}_{speaker}.mp3"
        
        # Show progress
        emotion = tts.detect_emotion(dialogue)
        print(f"\n   [{i+1}/{len(dialogues)}] {speaker} ({emotion})")
        print(f"   💬 {dialogue[:60]}{'...' if len(dialogue) > 60 else ''}")
        
        try:
            tts.generate_audio(dialogue, speaker, output_path)
            audio_files.append(output_path)
            print(f"   ✅ Generated: {output_path.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print(f"\n✅ Generated {len(audio_files)}/{len(dialogues)} audio segments")
    
    # Merge audio
    print("\n🔧 Step 4: Merging Audio...")
    output_dir = Path("ai-blog-podcast/backend/outputs")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{output_name}.mp3"
    
    simple_merge_mp3(audio_files, output_file)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    
    print(f"✅ Merged successfully!")
    print(f"📁 Output: {output_file}")
    print(f"💿 Size: {file_size:.2f} MB")
    
    # Cleanup
    print("\n🧹 Step 5: Cleaning up temp files...")
    for file in audio_files:
        if file.exists():
            file.unlink()
    print("✅ Cleanup complete")
    
    # Summary
    print("\n" + "="*50)
    print("🎉 PODCAST GENERATION COMPLETE!")
    print("="*50)
    print(f"\n📊 Summary:")
    print(f"   • Speakers: {len(speakers)}")
    print(f"   • Dialogues: {len(dialogues)}")
    print(f"   • Audio Segments: {len(audio_files)}")
    print(f"   • Output File: {output_file.name}")
    print(f"   • File Size: {file_size:.2f} MB")
    print(f"\n🎧 Play your podcast:")
    print(f"   {output_file.absolute()}")
    
    return output_file


# Test Script 1: Hinglish Co-host (AI Topic)
SCRIPT_1 = """
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
SCRIPT_2 = """
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
SCRIPT_3 = """
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


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🎙️  COMPLETE PODCAST AUDIO GENERATION TEST")
    print("="*60)
    
    print("\nWhich test would you like to run?")
    print("1. Hinglish Co-host (AI Topic) - 8 dialogues")
    print("2. English Co-host (Technology) - 8 dialogues")
    print("3. Multi-speaker (3 people) - 13 dialogues")
    print("4. All tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        generate_podcast(SCRIPT_1, "hinglish_cohost")
    elif choice == "2":
        generate_podcast(SCRIPT_2, "english_cohost")
    elif choice == "3":
        generate_podcast(SCRIPT_3, "multi_speaker")
    elif choice == "4":
        print("\n🚀 Running all tests...\n")
        generate_podcast(SCRIPT_1, "test1_hinglish_cohost")
        print("\n" + "="*60 + "\n")
        generate_podcast(SCRIPT_2, "test2_english_cohost")
        print("\n" + "="*60 + "\n")
        generate_podcast(SCRIPT_3, "test3_multi_speaker")
    else:
        print("❌ Invalid choice!")
        sys.exit(1)
    
    print("\n✨ All done! Enjoy your podcasts! ✨\n")
