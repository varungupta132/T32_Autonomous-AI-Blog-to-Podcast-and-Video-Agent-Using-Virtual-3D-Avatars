"""
================================================================================
🎙️ COMPLETE INTEGRATED PODCAST STUDIO
================================================================================
Features:
  1. FREE EdgeTTS - Natural voices, unlimited usage
  2. AI Podcast Generator - OpenRouter API for professional scripts
  3. Hinglish Support - Perfect for Indian audience
  4. Parallel Processing - 5-10x faster generation
  5. Emotion Detection - Natural voice modulation
  6. Professional UI - Beautiful web interface

================================================================================
"""

import re
import json
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import edge_tts
import asyncio
import sys

# Set appropriate event loop policy for Windows to prevent ThreadPoolExecutor issues
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIGURATION
# ============================================================================

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-openrouter-api-key-here")

# EdgeTTS voices - Natural Microsoft voices (FREE!)
VOICE_LIBRARY = {
    "indian": [
        {"voice": "en-IN-PrabhatNeural", "name": "Prabhat (Indian Male)"},
        {"voice": "en-IN-NeerjaNeural", "name": "Neerja (Indian Female)"},
        {"voice": "hi-IN-MadhurNeural", "name": "Madhur (Hindi Male)"},
        {"voice": "hi-IN-SwaraNeural", "name": "Swara (Hindi Female)"}
    ],
    "global": [
        {"voice": "en-US-ChristopherNeural", "name": "Christopher (US Male)"},
        {"voice": "en-US-AriaNeural", "name": "Aria (US Female)"},
        {"voice": "en-US-GuyNeural", "name": "Guy (US Male)"},
        {"voice": "en-US-JennyNeural", "name": "Jenny (US Female)"}
    ],
    "telugu": [
        {"voice": "te-IN-MohanNeural", "name": "Mohan (Telugu Male)"},
        {"voice": "te-IN-ShrutiNeural", "name": "Shruti (Telugu Female)"}
    ],
    "french": [
        {"voice": "fr-FR-HenriNeural", "name": "Henri (French Male)"},
        {"voice": "fr-FR-DeniseNeural", "name": "Denise (French Female)"}
    ],
    "spanish": [
        {"voice": "es-ES-AlvaroNeural", "name": "Alvaro (Spanish Male)"},
        {"voice": "es-ES-ElviraNeural", "name": "Elvira (Spanish Female)"}
    ]
}

OUTPUT_DIR = Path("generated_podcasts")
TEMP_DIR = Path("temp_audio")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================================
# FLASK APP
# ============================================================================

app = Flask(__name__)

# ============================================================================
# OPENROUTER AI FUNCTIONS
# ============================================================================

def generate_ai_podcast(content, title, ptype, audience):
    """Generate podcast script using OpenRouter API"""
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENAI_API_KEY,
        )
        
        if audience == "indian":
            aud = """Indian Hinglish - Mix Hindi and English NATURALLY like Indians actually speak.

RULES FOR NATURAL HINGLISH:
1. Start sentences in Hindi, add English words naturally
2. Use simple Hindi grammar (avoid complex tenses)
3. Common pattern: "Dekho yaar, [topic] bahut interesting hai"
4. Hindi words to use: dekho, yaar, acha, toh, bahut, kya, matlab, bilkul, sahi, haan, nahi, bhai, theek
5. Keep it conversational and simple
6. Don't switch to full English mid-sentence or at end
7. End sentences in Hindi, not English

GOOD Examples:
✅ "Dekho yaar, AI bahut powerful hai"
✅ "Acha toh education mein bhi AI help karta hai"
✅ "Bilkul sahi! Healthcare mein bhi use ho raha hai"
✅ "Hum try karenge answer dene ka"

BAD Examples (Avoid):
❌ "AI is very powerful, taking convenience to a new level"
❌ "because every tech has both sides"
❌ "we will try to answer" (use "hum try karenge")
❌ "with improved quality of life" (use "better life mil sakti hai")"""
        elif audience == "telugu":
            aud = "Telugu - Conversational, fluent, and highly engaging Telugu suitable for an interesting podcast. MUST write in Telugu script (తెలుగు లిపి). Do NOT use English letters for Telugu words. VERY IMPORTANT: KEEP SPEAKER NAMES IN ENGLISH (e.g., Alex:, Sam:, Host:)."
        elif audience == "french":
            aud = "French - Native, fluent, and highly engaging conversational French suitable for an interesting podcast."
        elif audience == "spanish":
            aud = "Spanish - Native, fluent, and highly engaging conversational Spanish suitable for an interesting podcast."
        else:
            aud = "English - clear, professional, conversational, engaging."


        if ptype == "single":
            fmt = """SINGLE HOST ONLY - Use ONLY "Host:" label.
Host speaks directly to listeners warmly and engagingly."""
        elif ptype == "co-host":
            fmt = """TWO HOSTS - Alex and Sam in natural dialogue.
They discuss, ask questions, and build on each other's points."""
        else:
            fmt = """THREE HOSTS - Alex (moderator), Jordan (expert), Casey (curious).
Dynamic conversation with different perspectives."""

        prompt = f"""Convert the following blog into an engaging podcast script.

LANGUAGE: {aud}
FORMAT: {fmt}

STRUCTURE:
1. INTRO (2-3 lines): Warm welcome, introduce topic
2. MAIN DISCUSSION (12-16 lines): Cover key points naturally
3. OUTRO (2-3 lines): Thank listeners, closing

CRITICAL RULES:
1. NO emojis
2. NO stage directions (no *laughs*, [music])
3. ONLY speakable dialogue
4. Make it engaging and emotional
5. 18-22 exchanges, 500-600 words
6. Natural conversation flow
7. For Hinglish: Start sentences in Hindi, add English words naturally. NO full English sentences.
8. Each speaker on separate line
9. Keep grammar simple and correct

TOPIC: {title if title else "Untitled"}

BLOG CONTENT:
{content}

Write ONLY the dialogue. Start now:
"""

        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a professional podcast script writer. Create engaging, natural conversations. Follow format exactly. NO emojis, NO stage directions, ONLY dialogue.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        script = response.choices[0].message.content

        # Post-processing cleanup
        # Remove markdown stars for bold/italic which can mess up speaker names
        script = script.replace('*', '')
        # Remove parentheticals and square brackets which usually contain stage directions
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        script = script.replace('INTRO MUSIC', '').replace('OUTRO MUSIC', '')
        script = script.replace('MUSIC', '').replace('SOUND', '')

        if ptype == "single":
            script = re.sub(r'(Alex|Sam|Jordan|Casey):', 'Host:', script)
        elif ptype == "co-host":
            script = script.replace('Host 1:', 'Alex:')
            script = script.replace('Host 2:', 'Sam:')
            script = script.replace('Host1:', 'Alex:')
            script = script.replace('Host2:', 'Sam:')
            script = script.replace('Host:', 'Alex:')
            script = re.sub(r'(Jordan|Casey):', 'Sam:', script)
        else:
            script = script.replace('Host:', 'Alex:')
            script = script.replace('Host 1:', 'Alex:')
            script = script.replace('Host 2:', 'Jordan:')
            script = script.replace('Host 3:', 'Casey:')

        script = re.sub(r'[ \t]+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n\n+', '\n\n', script)

        lines = []
        for line in script.split('\n'):
            line = line.strip()
            # Relaxed length checks to allow for shorter words/sentences in Telugu
            if line and ':' in line and len(line) > 3:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 1:
                    lines.append(line)

        script = '\n\n'.join(lines)
        script = script.strip()

        return {'success': True, 'script': script}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================================
# EDGE TTS FUNCTIONS
# ============================================================================

def parse_script(script):
    """Parse script and extract speakers with dialogues"""
    dialogues = []
    lines = script.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if ':' in line and len(line) > 5:
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip()
                dialogue = parts[1].strip()
                if dialogue:
                    dialogues.append({"speaker": speaker, "text": dialogue})
    
    return dialogues

def detect_speakers(dialogues, language="global"):
    """Detect unique speakers and assign voices"""
    speakers = list(set([d["speaker"] for d in dialogues]))
    speakers.sort()
    
    voices = VOICE_LIBRARY.get(language, VOICE_LIBRARY["global"])
    speaker_voices = {}
    
    for i, speaker in enumerate(speakers):
        voice_info = voices[i % len(voices)]
        speaker_voices[speaker] = {
            "voice_key": voice_info["voice"],
            "voice_info": {**voice_info, "rate": "+0%", "pitch": "+0Hz"}
        }
    
    return speaker_voices

def analyze_emotion(text):
    """Detect emotion for voice modulation"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['wow', 'amazing', 'incredible', 'awesome', 'fantastic', 
                                             'zabardast', 'kya baat', '!!', 'bahut accha']):
        return "excited"
    elif '?' in text or any(word in text_lower for word in ['kya', 'really', 'sach', 'how', 'why']):
        return "curious"
    elif any(word in text_lower for word in ['important', 'must', 'critical', 'zaruri', 'bilkul']):
        return "emphasis"
    elif any(word in text_lower for word in ['think', 'believe', 'perhaps', 'maybe', 'shayad']):
        return "thoughtful"
    
    return "neutral"

def get_voice_params(emotion):
    """Get voice parameters based on emotion"""
    params = {
        "excited": {"rate": "+15%", "pitch": "+5Hz"},
        "curious": {"rate": "+5%", "pitch": "+3Hz"},
        "emphasis": {"rate": "+0%", "pitch": "+2Hz"},
        "thoughtful": {"rate": "-10%", "pitch": "-2Hz"},
        "neutral": {"rate": "+0%", "pitch": "+0Hz"}
    }
    return params.get(emotion, params["neutral"])

async def generate_audio_async(text, voice, rate, pitch, output_path):
    """Generate audio using EdgeTTS"""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(str(output_path))

def generate_audio_segment(speaker_voice, text, output_path):
    """Generate audio segment with emotion"""
    try:
        voice_info = speaker_voice["voice_info"]
        emotion = analyze_emotion(text)
        params = get_voice_params(emotion)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(generate_audio_async(
                text=text,
                voice=voice_info["voice"],
                rate=params["rate"],
                pitch=params["pitch"],
                output_path=output_path
            ))
        finally:
            loop.close()
        
        return output_path, emotion
    
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        raise

def merge_audio_files(audio_files, output_file):
    """Merge audio files"""
    with open(output_file, 'wb') as outfile:
        for mp3_file in audio_files:
            if os.path.exists(mp3_file):
                with open(mp3_file, 'rb') as infile:
                    outfile.write(infile.read())
    return output_file

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/ai-generate', methods=['POST'])
def ai_generate():
    """Generate podcast script using OpenRouter AI"""
    try:
        data = request.json
        content = data.get('content', '')
        title = data.get('title', '')
        ptype = data.get('podcast_type', 'single')
        audience = data.get('audience', 'global')
        
        if not content:
            return jsonify({"error": "No content provided"}), 400
        
        result = generate_ai_podcast(content, title, ptype, audience)
        
        if result['success']:
            return jsonify({
                "success": True,
                "script": result['script'],
                "type": ptype,
                "audience": audience
            })
        else:
            return jsonify({"error": result['error']}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_script():
    """Analyze script and detect speakers"""
    try:
        data = request.json
        script = data.get('script', '')
        language = data.get('language', 'global')
        
        if not script:
            return jsonify({"error": "No script provided"}), 400
        
        dialogues = parse_script(script)
        
        if not dialogues:
            return jsonify({"error": "No valid dialogues found. Format: Speaker: Dialogue"}), 400
        
        speaker_voices = detect_speakers(dialogues, language)
        
        return jsonify({
            "success": True,
            "total_dialogues": len(dialogues),
            "speakers": len(speaker_voices),
            "speaker_info": {
                speaker: {
                    "voice": info["voice_info"]["name"],
                    "engine": "Microsoft EdgeTTS (FREE)"
                }
                for speaker, info in speaker_voices.items()
            },
            "dialogues": dialogues
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_podcast():
    """Generate podcast with EdgeTTS - PARALLEL processing"""
    try:
        data = request.json
        script = data.get('script', '')
        language = data.get('language', 'global')
        podcast_name = data.get('name', f'podcast_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        podcast_name = re.sub(r'[^\w\-_]', '_', podcast_name)
        
        if not script:
            return jsonify({"error": "No script provided"}), 400
        
        print(f"\n{'='*60}")
        print(f"🎙️ EDGE TTS PODCAST GENERATION - FREE & NATURAL")
        print(f"{'='*60}\n")
        
        dialogues = parse_script(script)
        if not dialogues:
            return jsonify({"error": "No valid dialogues found"}), 400
            
        speaker_voices = detect_speakers(dialogues, language)
        
        print(f"📊 Total dialogues: {len(dialogues)}")
        print(f"🎤 Speakers: {len(speaker_voices)}")
        print(f"⚡ Using parallel generation\n")
        
        tasks = []
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue["speaker"]
            text = dialogue["text"]
            output_path = TEMP_DIR / f"{podcast_name}_seg_{i:03d}_{speaker}.mp3"
            
            tasks.append({
                "index": i,
                "speaker": speaker,
                "text": text,
                "output_path": output_path,
                "voice": speaker_voices[speaker]
            })
        
        audio_files = [None] * len(tasks)
        progress_data = []
        import time
        start_time = time.time()
        
        def generate_segment(task):
            """Worker function"""
            try:
                idx = task["index"]
                speaker = task["speaker"]
                text = task["text"]
                output_path = task["output_path"]
                voice = task["voice"]
                
                print(f"[{idx+1}/{len(tasks)}] 🎵 {speaker}: {text[:40]}...")
                
                _, emotion = generate_audio_segment(voice, text, output_path)
                
                if output_path.exists():
                    print(f"[{idx+1}/{len(tasks)}] ✓ Done ({emotion})")
                    return {
                        "success": True,
                        "index": idx,
                        "path": output_path,
                        "speaker": speaker,
                        "emotion": emotion,
                        "text": text
                    }
                else:
                    return {"success": False, "index": idx, "error": "File not created"}
                    
            except Exception as e:
                print(f"[{idx+1}/{len(tasks)}] ✗ Error: {str(e)}")
                return {"success": False, "index": idx, "error": str(e)}
        
        max_workers = min(len(tasks), 8)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(generate_segment, task): task for task in tasks}
            
            for future in as_completed(future_to_task):
                result = future.result()
                
                if result["success"]:
                    idx = result["index"]
                    audio_files[idx] = result["path"]
                    progress_data.append({
                        "index": idx + 1,
                        "speaker": result["speaker"],
                        "emotion": result["emotion"],
                        "text": result["text"][:60] + "..." if len(result["text"]) > 60 else result["text"]
                    })
                else:
                    return jsonify({"error": f"Failed segment {result['index']+1}"}), 500
        
        audio_files = [f for f in audio_files if f is not None]
        
        if not audio_files:
            return jsonify({"error": "No audio files generated"}), 500
        
        print(f"\n🎧 Merging {len(audio_files)} segments...")
        
        output_file = OUTPUT_DIR / f"{podcast_name}.mp3"
        merge_audio_files(audio_files, output_file)
        
        if not output_file.exists():
            return jsonify({"error": "Failed to create final file"}), 500
        
        for file in audio_files:
            try:
                if file.exists():
                    file.unlink()
            except:
                pass
        
        file_size = output_file.stat().st_size / 1024 / 1024
        
        print(f"\n{'='*60}")
        print(f"✓ SUCCESS! {output_file.name}")
        print(f"  Size: {file_size:.2f} MB")
        print(f"  Segments: {len(audio_files)}")
        print(f"{'='*60}\n")
        
        progress_data.sort(key=lambda x: x["index"])
        
        return jsonify({
            "success": True,
            "filename": output_file.name,
            "file_size": f"{file_size:.2f} MB",
            "total_segments": len(audio_files),
            "speakers": len(speaker_voices),
            "progress": progress_data
        })
    
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream/<filename>')
def stream_podcast(filename):
    """Stream audio for inline playback"""
    try:
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            return send_file(file_path, mimetype='audio/mpeg')
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>')
def download_podcast(filename):
    """Download generated podcast"""
    try:
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voices')
def get_voices():
    """Get available voices"""
    return jsonify({
        "voices": VOICE_LIBRARY
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎙️  COMPLETE INTEGRATED PODCAST STUDIO")
    print("="*60)
    print("\n🚀 Starting server...")
    print("📱 Open: http://localhost:8080")
    print("\n✨ Features:")
    print("   • FREE EdgeTTS - Natural voices, unlimited!")
    print("   • AI Script Generator - OpenRouter API")
    print("   • Hinglish support - Perfect for India!")
    print("   • Emotion-based voice modulation")
    print("   • ⚡ Fast parallel generation")
    print("\n💡 Two modes:")
    print("   1. AI Generate - Get professional scripts")
    print("   2. TTS Generate - Convert scripts to audio")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
