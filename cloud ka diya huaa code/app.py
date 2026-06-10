"""
================================================================================
🎙️ PODCAST STUDIO PRO - ULTIMATE COMBINED VERSION
================================================================================
Best of both worlds:
  ✅ AI Script Generation (OpenRouter / Gemini)
  ✅ EdgeTTS - Free, Natural Microsoft Voices
  ✅ Multi-language: Hinglish, Hindi, Telugu, French, Spanish, English
  ✅ Emotion Detection + Voice Modulation
  ✅ Parallel Audio Generation (5-10x faster)
  ✅ 1/2/3 Host Support with smart voice assignment
  ✅ Stream + Download support
================================================================================
"""

import re
import json
import os
import sys
import time
import asyncio
import traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, render_template, request, jsonify, send_file, Response
import edge_tts

# Fix Windows event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL   = "google/gemini-2.0-flash-lite-preview-02-05:free"

# Voice library — indexed by language key
# Each language has alternating Male/Female so speakers get different voices
VOICE_LIBRARY = {
    "indian": [
        {"voice": "en-IN-PrabhatNeural",   "name": "Prabhat",   "gender": "Male",   "lang": "Indian English"},
        {"voice": "en-IN-NeerjaNeural",    "name": "Neerja",    "gender": "Female", "lang": "Indian English"},
        {"voice": "hi-IN-MadhurNeural",    "name": "Madhur",    "gender": "Male",   "lang": "Hindi"},
        {"voice": "hi-IN-SwaraNeural",     "name": "Swara",     "gender": "Female", "lang": "Hindi"},
    ],
    "hindi": [
        {"voice": "hi-IN-MadhurNeural",    "name": "Madhur",    "gender": "Male",   "lang": "Hindi"},
        {"voice": "hi-IN-SwaraNeural",     "name": "Swara",     "gender": "Female", "lang": "Hindi"},
        {"voice": "en-IN-PrabhatNeural",   "name": "Prabhat",   "gender": "Male",   "lang": "Indian English"},
        {"voice": "en-IN-NeerjaNeural",    "name": "Neerja",    "gender": "Female", "lang": "Indian English"},
    ],
    "global": [
        {"voice": "en-US-ChristopherNeural","name": "Christopher","gender": "Male",  "lang": "US English"},
        {"voice": "en-US-AriaNeural",       "name": "Aria",      "gender": "Female", "lang": "US English"},
        {"voice": "en-US-GuyNeural",        "name": "Guy",       "gender": "Male",   "lang": "US English"},
        {"voice": "en-US-JennyNeural",      "name": "Jenny",     "gender": "Female", "lang": "US English"},
    ],
    "telugu": [
        {"voice": "te-IN-MohanNeural",     "name": "Mohan",     "gender": "Male",   "lang": "Telugu"},
        {"voice": "te-IN-ShrutiNeural",    "name": "Shruti",    "gender": "Female", "lang": "Telugu"},
    ],
    "french": [
        {"voice": "fr-FR-HenriNeural",     "name": "Henri",     "gender": "Male",   "lang": "French"},
        {"voice": "fr-FR-DeniseNeural",    "name": "Denise",    "gender": "Female", "lang": "French"},
    ],
    "spanish": [
        {"voice": "es-ES-AlvaroNeural",    "name": "Alvaro",    "gender": "Male",   "lang": "Spanish"},
        {"voice": "es-ES-ElviraNeural",    "name": "Elvira",    "gender": "Female", "lang": "Spanish"},
    ],
}

# Emotion → voice params
EMOTION_PARAMS = {
    "excited":    {"rate": "+18%", "pitch": "+6Hz"},
    "curious":    {"rate": "+8%",  "pitch": "+4Hz"},
    "emphasis":   {"rate": "+2%",  "pitch": "+3Hz"},
    "thoughtful": {"rate": "-10%", "pitch": "-2Hz"},
    "neutral":    {"rate": "+0%",  "pitch": "+0Hz"},
}

EMOTION_KEYWORDS = {
    "excited":    ["wow", "amazing", "incredible", "awesome", "fantastic",
                   "zabardast", "kya baat", "bahut accha", "outstanding", "brilliant"],
    "curious":    ["really", "sach", "interesting", "i wonder", "tell me more"],
    "emphasis":   ["important", "must", "critical", "zaruri", "bilkul", "definitely",
                   "absolutely", "never", "always"],
    "thoughtful": ["think", "believe", "perhaps", "maybe", "shayad", "consider", "reflect"],
}

OUTPUT_DIR = Path("generated_podcasts")
TEMP_DIR   = Path("temp_audio")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================================
# FLASK APP
# ============================================================================

app = Flask(__name__)

# ============================================================================
# AI SCRIPT GENERATION
# ============================================================================

AUDIENCE_PROMPTS = {
    "indian": """LANGUAGE: Hinglish — mix Hindi and English naturally like Indians talk.
RULES:
- Start sentences in Hindi, sprinkle English nouns naturally
- Use: dekho, yaar, acha, toh, bahut, kya, matlab, bilkul, sahi, haan, bhai, theek, samjhe
- Pattern: "Dekho yaar, AI bahut powerful hai"
- NEVER write full English sentences
- Keep grammar conversational and simple""",

    "hindi": """LANGUAGE: Pure Hindi — formal conversational Hindi, Devanagari script only.
- Use clean, clear Hindi
- Avoid English words unless absolutely necessary (like "AI", "Internet")
- Natural, warm tone""",

    "global": """LANGUAGE: English — clear, professional, engaging American English.""",

    "telugu": """LANGUAGE: Telugu — write ONLY in Telugu script (తెలుగు లిపి). 
Keep SPEAKER NAMES in English (Alex:, Sam:, Host:).""",

    "french": """LANGUAGE: French — native, fluent conversational French.""",

    "spanish": """LANGUAGE: Spanish — native, fluent conversational Spanish.""",
}

FORMAT_PROMPTS = {
    "single": """FORMAT: SINGLE HOST
- Use ONLY "Host:" label
- Speaks warmly and directly to listeners
- No dialogue — monologue style""",

    "co-host": """FORMAT: TWO HOSTS (Alex and Sam)
- Natural back-and-forth dialogue
- They ask questions and build on each other's points
- Balanced speaking time""",

    "panel": """FORMAT: THREE HOSTS (Alex = moderator, Jordan = expert, Casey = curious listener)
- Dynamic 3-way conversation
- Alex guides, Jordan explains, Casey asks questions
- Varied perspectives""",
}

def generate_ai_script(content: str, title: str, podcast_type: str, audience: str) -> dict:
    """Generate podcast script using OpenRouter API"""
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        audience_instruction = AUDIENCE_PROMPTS.get(audience, AUDIENCE_PROMPTS["global"])
        format_instruction   = FORMAT_PROMPTS.get(podcast_type, FORMAT_PROMPTS["co-host"])

        prompt = f"""Convert this blog/content into an engaging podcast script.

{audience_instruction}

{format_instruction}

SCRIPT STRUCTURE:
1. INTRO (2-3 exchanges): Warm welcome + introduce topic
2. MAIN DISCUSSION (12-16 exchanges): Deep dive into key points naturally  
3. OUTRO (2-3 exchanges): Summary + closing

STRICT RULES:
- NO emojis
- NO stage directions (*laughs*, [music], (pause))
- ONLY speakable dialogue — no markdown
- 18-22 total exchanges
- Each speaker on its own line
- Natural, conversational flow
- Interesting — keep listeners hooked!

TOPIC TITLE: {title or "Untitled"}

CONTENT:
{content}

Write ONLY the dialogue script now. Start immediately:
"""

        resp = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert podcast script writer. "
                        "Produce engaging, natural-sounding dialogue. "
                        "Follow every formatting rule exactly. "
                        "NO emojis, NO stage directions, ONLY spoken dialogue."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        script = resp.choices[0].message.content

        # ── Post-processing cleanup ──────────────────────────────────────────
        script = script.replace("*", "")
        script = re.sub(r'\([^)]*\)', '', script)           # remove parenthetical directions
        script = re.sub(r'\[[^\]]*\]', '', script)           # remove bracket directions
        for word in ["INTRO MUSIC", "OUTRO MUSIC", "MUSIC", "SOUND", "---", "==="]:
            script = script.replace(word, "")

        # Normalise speaker labels
        if podcast_type == "single":
            script = re.sub(r'\b(Alex|Sam|Jordan|Casey)\s*:', 'Host:', script)
        elif podcast_type == "co-host":
            script = re.sub(r'Host\s*1\s*:', 'Alex:', script)
            script = re.sub(r'Host\s*2\s*:', 'Sam:', script)
            script = re.sub(r'Host\s*:\s*', 'Alex:', script)
            script = re.sub(r'\b(Jordan|Casey)\s*:', 'Sam:', script)
        else:  # panel
            script = re.sub(r'Host\s*:\s*', 'Alex:', script)
            script = re.sub(r'Host\s*1\s*:', 'Alex:', script)
            script = re.sub(r'Host\s*2\s*:', 'Jordan:', script)
            script = re.sub(r'Host\s*3\s*:', 'Casey:', script)

        # Clean whitespace
        script = re.sub(r'[ \t]+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n{3,}', '\n\n', script)

        # Keep only valid dialogue lines
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if ':' in line and len(line) > 5:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 2:
                    lines.append(line)

        script = '\n\n'.join(lines).strip()
        return {"success": True, "script": script}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# AUDIO FUNCTIONS
# ============================================================================

def parse_script(script: str) -> list:
    """Parse 'Speaker: dialogue' formatted script"""
    dialogues = []
    for line in script.strip().split('\n'):
        line = line.strip()
        if ':' in line and len(line) > 5:
            parts = line.split(':', 1)
            speaker  = parts[0].strip()
            dialogue = parts[1].strip()
            if speaker and dialogue:
                dialogues.append({"speaker": speaker, "text": dialogue})
    return dialogues

def assign_voices(dialogues: list, language: str = "global") -> dict:
    """Assign a unique voice to each speaker, alternating M/F"""
    speakers = sorted(set(d["speaker"] for d in dialogues))
    voices   = VOICE_LIBRARY.get(language, VOICE_LIBRARY["global"])

    speaker_voices = {}
    for i, speaker in enumerate(speakers):
        info = voices[i % len(voices)]
        speaker_voices[speaker] = {
            "voice":  info["voice"],
            "name":   info["name"],
            "gender": info["gender"],
            "lang":   info["lang"],
        }
    return speaker_voices

def detect_emotion(text: str) -> str:
    text_lower = text.lower()
    if '!!' in text or text.count('!') >= 2:
        return "excited"
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return emotion
    if '?' in text:
        return "curious"
    return "neutral"

async def _tts_async(text: str, voice: str, rate: str, pitch: str, path: Path):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(str(path))

def generate_segment(task: dict) -> dict:
    """Generate one audio segment (runs in thread)"""
    try:
        idx      = task["index"]
        text     = task["text"]
        voice    = task["voice"]["voice"]
        out_path = task["output_path"]

        emotion = detect_emotion(text)
        params  = EMOTION_PARAMS[emotion]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_tts_async(text, voice, params["rate"], params["pitch"], out_path))
        finally:
            loop.close()

        if out_path.exists():
            return {"success": True, "index": idx, "path": out_path,
                    "speaker": task["speaker"], "emotion": emotion, "text": text}
        return {"success": False, "index": idx, "error": "File not created"}

    except Exception as e:
        return {"success": False, "index": task["index"], "error": str(e)}

def merge_audio(files: list, output: Path) -> Path:
    """Concatenate mp3 binary blobs"""
    with open(output, 'wb') as out:
        for f in files:
            f_path = Path(f)
            if f_path.exists():
                out.write(f_path.read_bytes())
    return output

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

# ── AI Script Generation ────────────────────────────────────────────────────

@app.route('/api/ai-generate', methods=['POST'])
def api_ai_generate():
    data     = request.json or {}
    content  = data.get('content', '').strip()
    title    = data.get('title', '').strip()
    ptype    = data.get('podcast_type', 'co-host')
    audience = data.get('audience', 'global')

    if not content:
        return jsonify({"error": "No content provided"}), 400

    result = generate_ai_script(content, title, ptype, audience)
    if result['success']:
        return jsonify({"success": True, "script": result['script'],
                        "type": ptype, "audience": audience})
    return jsonify({"error": result['error']}), 500

# ── Script Analysis ─────────────────────────────────────────────────────────

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data     = request.json or {}
    script   = data.get('script', '').strip()
    language = data.get('language', 'global')

    if not script:
        return jsonify({"error": "No script provided"}), 400

    dialogues      = parse_script(script)
    if not dialogues:
        return jsonify({"error": "No valid dialogues found. Format: Speaker: Dialogue"}), 400

    speaker_voices = assign_voices(dialogues, language)

    return jsonify({
        "success":        True,
        "total_dialogues": len(dialogues),
        "speakers":       len(speaker_voices),
        "speaker_info": {
            spk: {"voice": v["name"], "gender": v["gender"], "lang": v["lang"]}
            for spk, v in speaker_voices.items()
        },
        "dialogues": dialogues,
    })

# ── Podcast Generation ──────────────────────────────────────────────────────

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data     = request.json or {}
    script   = data.get('script', '').strip()
    language = data.get('language', 'global')
    name     = data.get('name', f'podcast_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    name     = re.sub(r'[^\w\-_]', '_', name)

    if not script:
        return jsonify({"error": "No script provided"}), 400

    dialogues = parse_script(script)
    if not dialogues:
        return jsonify({"error": "No valid dialogues found"}), 400

    speaker_voices = assign_voices(dialogues, language)

    # Build tasks
    tasks = [
        {
            "index":       i,
            "speaker":     d["speaker"],
            "text":        d["text"],
            "output_path": TEMP_DIR / f"{name}_seg_{i:03d}.mp3",
            "voice":       speaker_voices[d["speaker"]],
        }
        for i, d in enumerate(dialogues)
    ]

    audio_files  = [None] * len(tasks)
    progress     = []
    errors       = []

    max_workers = min(len(tasks), 8)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generate_segment, t): t for t in tasks}
        for future in as_completed(futures):
            res = future.result()
            if res["success"]:
                audio_files[res["index"]] = res["path"]
                progress.append({
                    "index":   res["index"] + 1,
                    "speaker": res["speaker"],
                    "emotion": res["emotion"],
                    "text":    res["text"][:70] + ("…" if len(res["text"]) > 70 else ""),
                })
            else:
                errors.append(res)

    if errors:
        return jsonify({"error": f"Segment generation failed: {errors[0]['error']}"}), 500

    valid_files = [f for f in audio_files if f]
    if not valid_files:
        return jsonify({"error": "No audio files generated"}), 500

    output_path = OUTPUT_DIR / f"{name}.mp3"
    merge_audio(valid_files, output_path)

    # Cleanup temp
    for f in valid_files:
        try:
            Path(f).unlink()
        except Exception:
            pass

    if not output_path.exists():
        return jsonify({"error": "Failed to create final podcast file"}), 500

    size_mb = output_path.stat().st_size / 1024 / 1024
    progress.sort(key=lambda x: x["index"])

    return jsonify({
        "success":        True,
        "filename":       output_path.name,
        "file_size":      f"{size_mb:.2f} MB",
        "total_segments": len(valid_files),
        "speakers":       len(speaker_voices),
        "speaker_voices": {
            spk: {"name": v["name"], "gender": v["gender"]}
            for spk, v in speaker_voices.items()
        },
        "progress": progress,
    })

# ── Playback & Download ─────────────────────────────────────────────────────

@app.route('/api/stream/<filename>')
def api_stream(filename):
    path = OUTPUT_DIR / filename
    if path.exists():
        return send_file(path, mimetype='audio/mpeg')
    return jsonify({"error": "File not found"}), 404

@app.route('/api/download/<filename>')
def api_download(filename):
    path = OUTPUT_DIR / filename
    if path.exists():
        return send_file(path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

# ── Voices Info ─────────────────────────────────────────────────────────────

@app.route('/api/voices')
def api_voices():
    return jsonify({"voices": VOICE_LIBRARY})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🎙️  PODCAST STUDIO PRO — ULTIMATE EDITION")
    print("="*60)
    print("  🚀  http://localhost:8080")
    print("  ✅  AI Script Generation (OpenRouter)")
    print("  ✅  EdgeTTS — Free, Natural Voices")
    print("  ✅  Hinglish / Hindi / Telugu / French / Spanish")
    print("  ✅  Emotion-aware voice modulation")
    print("  ✅  Parallel audio generation")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8080)
