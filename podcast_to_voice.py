"""
Podcast Script to Voice Converter
Converts podcast scripts to audio with different voices for different speakers
"""

import ollama
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import re
import os

class PodcastVoiceGenerator:
    def __init__(self):
        os.makedirs("audio_segments", exist_ok=True)
        os.makedirs("final_podcasts", exist_ok=True)
    
    def generate_script(self, blog_content, title, podcast_type, audience="global"):
        """Generate podcast script using Ollama"""
        
        print(f"\n⏳ Step 1: Generating {podcast_type} podcast script...")
        
        # Audience
        if audience == "indian":
            aud = "Natural Hinglish (Hindi+English mix). Indian examples."
        else:
            aud = "Clear professional English. Universal examples."
        
        # Type
        if podcast_type == "single":
            fmt = "Single host speaking. Use 'Host:' label."
        elif podcast_type == "co-host":
            fmt = "Two hosts dialogue. Use 'Alex:' and 'Sam:' labels."
        else:
            fmt = "Three hosts panel. Use 'Alex:', 'Jordan:', 'Casey:' labels."
        
        prompt = f"""
Create a professional podcast script.

FORMAT: {fmt}
AUDIENCE: {aud}

CRITICAL RULES:
1. NO emojis, NO **, NO special symbols
2. ONLY speakable text
3. Clear speaker labels (Host:, Alex:, Sam:)
4. Natural conversation
5. Professional quality

Title: {title}
Content: {blog_content}

Generate clean podcast script:
"""
        
        response = ollama.chat(
            model='llama2',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        script = response['message']['content']
        print(f"✅ Script generated ({len(script)} characters)")
        
        return script
    
    def parse_script(self, script):
        """Parse script into speaker segments"""
        
        print("\n⏳ Step 2: Parsing script into segments...")
        
        segments = []
        lines = script.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has speaker label
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    text = parts[1].strip()
                    
                    # Clean text
                    text = re.sub(r'[\*\[\]\(\)]', '', text)
                    text = text.strip()
                    
                    if text and len(text) > 5:
                        segments.append({
                            'speaker': speaker,
                            'text': text
                        })
        
        print(f"✅ Found {len(segments)} segments")
        return segments
    
    def text_to_speech(self, text, speaker, filename, language='en'):
        """Convert text to speech with speaker-specific settings"""
        
        # Different TTS settings for different speakers
        # Note: gTTS doesn't support different voices, but we can use different languages/speeds
        
        try:
            # For Indian audience, use Hindi-English mix
            if language == 'hi':
                tts = gTTS(text=text, lang='hi', slow=False)
            else:
                tts = gTTS(text=text, lang='en', slow=False)
            
            tts.save(filename)
            audio = AudioSegment.from_mp3(filename)
            
            # Adjust pitch/speed slightly for different speakers
            if speaker.lower() in ['sam', 'casey', 'jordan']:
                # Slightly faster for second/third speaker
                audio = audio.speedup(playback_speed=1.05)
            
            return audio
            
        except Exception as e:
            print(f"❌ Error generating voice for {speaker}: {e}")
            return None
    
    def generate_music(self, duration_ms=3000, music_type="intro"):
        """Generate simple intro/outro music"""
        
        if music_type == "intro":
            # Upbeat intro tones
            tone1 = Sine(523).to_audio_segment(duration=800)  # C
            tone2 = Sine(659).to_audio_segment(duration=800)  # E
            tone3 = Sine(784).to_audio_segment(duration=1400)  # G
            music = tone1 + tone2 + tone3
        else:
            # Outro tones
            tone1 = Sine(784).to_audio_segment(duration=800)  # G
            tone2 = Sine(659).to_audio_segment(duration=800)  # E
            tone3 = Sine(523).to_audio_segment(duration=1400)  # C
            music = tone1 + tone2 + tone3
        
        # Fade in/out
        music = music.fade_in(300).fade_out(300)
        return music - 15  # Reduce volume
    
    def create_podcast_audio(self, blog_content, title, podcast_type, audience="global"):
        """Create complete podcast audio file"""
        
        print("\n" + "="*80)
        print("🎙️ CREATING PODCAST AUDIO")
        print("="*80)
        
        # Step 1: Generate script
        script = self.generate_script(blog_content, title, podcast_type, audience)
        
        # Save script
        script_file = f"final_podcasts/{title.replace(' ', '_')}_script.txt"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"✅ Script saved: {script_file}")
        
        # Step 2: Parse segments
        segments = self.parse_script(script)
        
        if not segments:
            print("❌ No segments found in script!")
            return None
        
        # Step 3: Generate intro music
        print("\n⏳ Step 3: Creating intro music...")
        intro_music = self.generate_music(3000, "intro")
        print("✅ Intro music created")
        
        # Step 4: Generate voice for each segment
        print("\n⏳ Step 4: Converting text to speech...")
        
        final_audio = intro_music
        
        lang = 'hi' if audience == 'indian' else 'en'
        
        for i, segment in enumerate(segments):
            print(f"  Processing {i+1}/{len(segments)}: {segment['speaker']}")
            
            temp_file = f"audio_segments/segment_{i:03d}_{segment['speaker']}.mp3"
            audio = self.text_to_speech(
                segment['text'], 
                segment['speaker'], 
                temp_file,
                lang
            )
            
            if audio:
                # Add small pause between speakers
                pause = AudioSegment.silent(duration=500)
                final_audio = final_audio + pause + audio
        
        print("✅ All segments converted")
        
        # Step 5: Add outro music
        print("\n⏳ Step 5: Adding outro music...")
        outro_music = self.generate_music(3000, "outro")
        final_audio = final_audio + outro_music
        print("✅ Outro music added")
        
        # Step 6: Export final podcast
        output_file = f"final_podcasts/{title.replace(' ', '_')}_{podcast_type}_{audience}.mp3"
        print(f"\n⏳ Step 6: Exporting final podcast...")
        
        final_audio.export(output_file, format="mp3", bitrate="192k")
        
        print("\n" + "="*80)
        print("✅ PODCAST CREATED SUCCESSFULLY!")
        print("="*80)
        print(f"\n📁 Audio File: {output_file}")
        print(f"📝 Script File: {script_file}")
        print(f"⏱️  Duration: {len(final_audio)/1000:.1f} seconds")
        print(f"🎤 Segments: {len(segments)}")
        print("\n")
        
        return output_file


# Demo
if __name__ == "__main__":
    generator = PodcastVoiceGenerator()
    
    # Sample blog
    blog = """
    Artificial Intelligence is transforming education in India. 
    Students can now learn from AI tutors that adapt to their pace. 
    Online education is becoming more accessible to everyone. 
    The future of learning is digital and personalized.
    """
    
    # Generate podcast with voice
    audio_file = generator.create_podcast_audio(
        blog_content=blog,
        title="AI in Education",
        podcast_type="co-host",
        audience="indian"
    )
    
    if audio_file:
        print(f"🎉 Done! Play your podcast:")
        print(f"   {audio_file}")
