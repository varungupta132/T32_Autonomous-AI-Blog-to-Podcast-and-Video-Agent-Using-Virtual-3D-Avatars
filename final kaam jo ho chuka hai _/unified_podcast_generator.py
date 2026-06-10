"""
🎙️ UNIFIED AI PODCAST GENERATOR
Complete system: Script Generation (OpenRouter) + Audio Generation (ElevenLabs)
Beautiful Web Interface with Flask

Features:
- Generate podcast scripts using OpenRouter API (FREE model)
- Review and edit scripts before audio generation
- Generate audio using ElevenLabs with multiple voices
- Threading for progress tracking
- Beautiful responsive UI

Author: AI Assistant
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from openai import OpenAI
import re
from pathlib import Path
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import threading
import time
import json

app = Flask(__name__)

# ============================================================================
# API CONFIGURATION
# ============================================================================

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"

# ElevenLabs API Configuration
ELEVENLABS_API_KEY = "sk_33c17748cbd7ba62cc21225bb2e995d33844a7671dd4f115"

# Voice mapping for different speakers
VOICE_MAP = {
    "Host": {"id": "pNInz6obpgDQGcFmaJgB", "type": "male"},
    "Alex": {"id": "pNInz6obpgDQGcFmaJgB", "type": "male"},
    "Sam": {"id": "EXAVITQu4vr4xnSDxMaL", "type": "female"},
    "Jordan": {"id": "TxGEqnHWrfWFTfGW9XjX", "type": "male"},
    "Casey": {"id": "ThT5KcBeYPX3keUQqHPh", "type": "female"}
}

# Output directories
OUTPUT_DIR = Path("generated_podcasts")
TEMP_DIR = Path("temp_audio")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Global progress tracking
audio_progress = {
    "status": "idle",
    "current": 0,
    "total": 0,
    "message": "",
    "file_path": None
}

# ============================================================================
# OPENROUTER SCRIPT GENERATION
# ============================================================================

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def generate_podcast_script(content, title, ptype, audience):
    """Generate podcast script using OpenRouter API"""
    try:
        # Language/Audience instructions
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
✅ "Hum try karenge answer dene ka" (NOT "we will try to answer")

BAD Examples (Avoid):
❌ "AI is very powerful, taking convenience to a new level"
❌ "because every tech has both sides"
❌ "we will try to answer" (use "hum try karenge")
❌ "with improved quality of life" (use "better life mil sakti hai")

Keep grammar SIMPLE. Mix naturally. Sound like real Indian conversation."""
        else:
            aud = "English - clear, professional, conversational, engaging."

        # Format instructions
        if ptype == "single":
            fmt = """SINGLE HOST ONLY - Use ONLY "Host:" label.
Host speaks directly to listeners warmly and engagingly."""
        elif ptype == "co-host":
            fmt = """TWO HOSTS - Alex and Sam in natural dialogue.
They discuss, ask questions, and build on each other's points."""
        else:
            fmt = """THREE HOSTS - Alex (moderator), Jordan (expert), Casey (curious).
Dynamic conversation with different perspectives."""

        # Single optimized prompt
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

        # API call with FREE model (using Qwen)
        response = openrouter_client.chat.completions.create(
            model="qwen/qwen-2-7b-instruct:free",
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
        script = re.sub(r'[^\x00-\x7F]+', '', script)
        script = re.sub(r'\*[^*]+\*', '', script)
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        script = script.replace('[INTRO MUSIC', '').replace('[OUTRO MUSIC', '')
        script = script.replace('[MUSIC]', '').replace('[SOUND', '')
        script = script.replace('INTRO MUSIC', '').replace('OUTRO MUSIC', '')

        # Fix speaker labels
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

        # Clean up spacing
        script = re.sub(r'[ \t]+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n\n+', '\n\n', script)

        # Extract clean dialogue lines
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line and ':' in line and len(line) > 10:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 5:
                    lines.append(line)

        script = '\n\n'.join(lines)
        script = script.strip()

        return {'success': True, 'script': script}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================================
# ELEVENLABS AUDIO GENERATION
# ============================================================================

elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

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

def detect_emotion(text):
    """Detect emotion from text for better voice modulation"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['wow', '!', 'amazing', 'incredible', 'kya baat', 'zabardast']):
        return "excited"
    elif any(word in text_lower for word in ['?', 'kya', 'really', 'sach', 'how', 'why']):
        return "curious"
    else:
        return "neutral"

def generate_audio_segment(speaker, text, output_path):
    """Generate audio for a single dialogue using ElevenLabs"""
    voice_info = VOICE_MAP.get(speaker, VOICE_MAP["Host"])
    voice_id = voice_info["id"]
    
    emotion = detect_emotion(text)
    
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
    else:
        settings = VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.5,
            use_speaker_boost=True
        )
    
    audio_generator = elevenlabs_client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=settings
    )
    
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)
    
    return output_path

def merge_audio_files(audio_files, output_file):
    """Simple MP3 concatenation"""
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

def generate_podcast_audio_threaded(script, output_name="podcast"):
    """Generate podcast audio in a separate thread with progress tracking"""
    global audio_progress
    
    audio_progress["status"] = "processing"
    audio_progress["current"] = 0
    audio_progress["message"] = "Parsing script..."
    audio_progress["file_path"] = None
    
    try:
        # Parse script
        dialogues = parse_script(script)
        audio_progress["total"] = len(dialogues)
        
        if not dialogues:
            audio_progress["status"] = "error"
            audio_progress["message"] = "No valid dialogues found in script"
            return
        
        audio_progress["message"] = f"Found {len(dialogues)} dialogues. Generating audio..."
        
        # Generate audio segments
        audio_files = []
        for i, (speaker, dialogue) in enumerate(dialogues):
            audio_progress["current"] = i + 1
            audio_progress["message"] = f"Generating segment {i+1}/{len(dialogues)}: {speaker}"
            
            output_path = TEMP_DIR / f"{output_name}_segment_{i}_{speaker}.mp3"
            
            try:
                generate_audio_segment(speaker, dialogue, output_path)
                audio_files.append(output_path)
            except Exception as e:
                print(f"Error generating segment {i}: {e}")
                continue
        
        if not audio_files:
            audio_progress["status"] = "error"
            audio_progress["message"] = "No audio segments were generated"
            return
        
        # Merge audio
        audio_progress["message"] = "Merging audio segments..."
        output_file = OUTPUT_DIR / f"{output_name}.mp3"
        merge_audio_files(audio_files, output_file)
        
        # Cleanup
        audio_progress["message"] = "Cleaning up temporary files..."
        cleanup_temp_files(audio_files)
        
        # Success
        file_size = output_file.stat().st_size / 1024 / 1024
        audio_progress["status"] = "complete"
        audio_progress["message"] = f"Podcast generated successfully! ({file_size:.2f} MB)"
        audio_progress["file_path"] = str(output_file)
        
    except Exception as e:
        audio_progress["status"] = "error"
        audio_progress["message"] = f"Error: {str(e)}"

# ============================================================================
# FLASK WEB INTERFACE
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎙️ Unified AI Podcast Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            font-size: 0.9em;
        }
        .content { padding: 40px; }
        .step {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }
        .step h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .form-group { margin-bottom: 25px; }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
            font-size: 1.1em;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
        }
        textarea { min-height: 200px; resize: vertical; }
        .options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .option {
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        .option:hover {
            border-color: #667eea;
            transform: translateY(-5px);
        }
        .option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        }
        .option h3 { font-size: 1.3em; margin-bottom: 8px; color: #667eea; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 50px;
            font-size: 1.2em;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            display: block;
            margin: 20px auto;
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn-secondary {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        .loading.active { display: block; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .script-editor {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .script-editor textarea {
            font-family: 'Courier New', monospace;
            font-size: 15px;
            line-height: 2;
            min-height: 400px;
        }
        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .audio-player {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-top: 20px;
        }
        .audio-player audio {
            width: 100%;
            max-width: 600px;
            margin: 20px 0;
        }
        .hidden { display: none !important; }
        .alert {
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎙️ Unified AI Podcast Generator</h1>
            <p>Complete Solution: Script + Audio Generation</p>
            <div class="badge">✨ OpenRouter AI</div>
            <div class="badge">🎤 ElevenLabs TTS</div>
            <div class="badge">🚀 FREE Model</div>
        </div>
        
        <div class="content">
            <!-- Step 1: Generate Script -->
            <div class="step" id="step1">
                <h2>📝 Step 1: Generate Podcast Script</h2>
                
                <form id="scriptForm">
                    <div class="form-group">
                        <label>📌 Blog Title (Optional)</label>
                        <input type="text" id="title" placeholder="Enter title...">
                    </div>
                    
                    <div class="form-group">
                        <label>📝 Blog Content</label>
                        <textarea id="content" placeholder="Paste your blog content here..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>🎙️ Podcast Type</label>
                        <div class="options">
                            <div class="option selected" data-type="single">
                                <h3>🎤 Single</h3>
                                <p>One host</p>
                            </div>
                            <div class="option" data-type="co-host">
                                <h3>👥 Co-Host</h3>
                                <p>Two hosts</p>
                            </div>
                            <div class="option" data-type="multi-host">
                                <h3>🎭 Multi</h3>
                                <p>Three hosts</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>🌍 Audience</label>
                        <div class="options">
                            <div class="option selected" data-audience="global">
                                <h3>🌐 Global</h3>
                                <p>English</p>
                            </div>
                            <div class="option" data-audience="indian">
                                <h3>🇮🇳 Indian</h3>
                                <p>Hinglish</p>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">✨ Generate Script</button>
                </form>
                
                <div class="loading" id="scriptLoading">
                    <div class="spinner"></div>
                    <h3>Generating script with AI...</h3>
                    <p>Using OpenRouter FREE model...</p>
                </div>
            </div>
            
            <!-- Step 2: Review & Edit Script -->
            <div class="step hidden" id="step2">
                <h2>✏️ Step 2: Review & Edit Script</h2>
                <p style="margin-bottom: 20px; color: #666;">Review the generated script below. You can edit it before generating audio.</p>
                
                <div class="script-editor">
                    <label>📜 Podcast Script</label>
                    <textarea id="scriptContent"></textarea>
                </div>
                
                <button class="btn btn-secondary" onclick="generateAudio()">🎤 Generate Audio</button>
                <button class="btn" onclick="resetForm()" style="background: #6c757d;">🔄 Start Over</button>
            </div>
            
            <!-- Step 3: Generate Audio -->
            <div class="step hidden" id="step3">
                <h2>🎵 Step 3: Generating Audio</h2>
                
                <div id="audioProgress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%">0%</div>
                    </div>
                    <p id="progressMessage" style="text-align: center; color: #666; margin-top: 10px;">
                        Initializing...
                    </p>
                </div>
                
                <div class="audio-player hidden" id="audioPlayer">
                    <h3 style="color: #28a745; margin-bottom: 20px;">🎉 Podcast Generated Successfully!</h3>
                    <audio controls id="audioElement">
                        <source id="audioSource" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                    <br>
                    <a id="downloadLink" class="btn btn-secondary" download>📥 Download Podcast</a>
                    <button class="btn" onclick="resetForm()" style="background: #6c757d;">🔄 Create Another</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedType = 'single';
        let selectedAudience = 'global';
        let generatedScript = '';
        let progressInterval = null;
        
        // Option selection handlers
        document.querySelectorAll('[data-type]').forEach(el => {
            el.addEventListener('click', function() {
                document.querySelectorAll('[data-type]').forEach(e => e.classList.remove('selected'));
                this.classList.add('selected');
                selectedType = this.dataset.type;
            });
        });
        
        document.querySelectorAll('[data-audience]').forEach(el => {
            el.addEventListener('click', function() {
                document.querySelectorAll('[data-audience]').forEach(e => e.classList.remove('selected'));
                this.classList.add('selected');
                selectedAudience = this.dataset.audience;
            });
        });
        
        // Script generation form
        document.getElementById('scriptForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const title = document.getElementById('title').value;
            const content = document.getElementById('content').value;
            
            if (!content.trim()) {
                alert('Please enter blog content!');
                return;
            }
            
            document.getElementById('scriptLoading').classList.add('active');
            
            try {
                const response = await fetch('/generate-script', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title, content,
                        podcast_type: selectedType,
                        audience: selectedAudience
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    generatedScript = data.script;
                    document.getElementById('scriptContent').value = generatedScript;
                    document.getElementById('step1').classList.add('hidden');
                    document.getElementById('step2').classList.remove('hidden');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('scriptLoading').classList.remove('active');
            }
        });
        
        // Generate audio function
        async function generateAudio() {
            const script = document.getElementById('scriptContent').value;
            
            if (!script.trim()) {
                alert('Script is empty!');
                return;
            }
            
            // Show step 3
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step3').classList.remove('hidden');
            
            // Start audio generation
            try {
                const response = await fetch('/generate-audio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ script: script })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Start polling for progress
                    startProgressPolling();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        // Progress polling
        function startProgressPolling() {
            progressInterval = setInterval(async () => {
                try {
                    const response = await fetch('/audio-progress');
                    const data = await response.json();
                    
                    // Update progress bar
                    const percentage = data.total > 0 ? Math.round((data.current / data.total) * 100) : 0;
                    document.getElementById('progressFill').style.width = percentage + '%';
                    document.getElementById('progressFill').textContent = percentage + '%';
                    document.getElementById('progressMessage').textContent = data.message;
                    
                    // Check if complete
                    if (data.status === 'complete') {
                        clearInterval(progressInterval);
                        showAudioPlayer(data.file_path);
                    } else if (data.status === 'error') {
                        clearInterval(progressInterval);
                        alert('Error: ' + data.message);
                    }
                } catch (error) {
                    console.error('Progress polling error:', error);
                }
            }, 1000);
        }
        
        // Show audio player
        function showAudioPlayer(filePath) {
            const fileName = filePath.split('/').pop();
            const audioUrl = '/download/' + fileName;
            
            document.getElementById('audioSource').src = audioUrl;
            document.getElementById('audioElement').load();
            document.getElementById('downloadLink').href = audioUrl;
            document.getElementById('audioPlayer').classList.remove('hidden');
        }
        
        // Reset form
        function resetForm() {
            document.getElementById('step1').classList.remove('hidden');
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step3').classList.add('hidden');
            document.getElementById('audioPlayer').classList.add('hidden');
            document.getElementById('scriptForm').reset();
            document.getElementById('scriptContent').value = '';
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressFill').textContent = '0%';
            if (progressInterval) {
                clearInterval(progressInterval);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-script', methods=['POST'])
def generate_script():
    """Generate podcast script using OpenRouter"""
    data = request.json
    result = generate_podcast_script(
        data['content'],
        data.get('title', ''),
        data['podcast_type'],
        data.get('audience', 'global')
    )
    return jsonify(result)

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    """Start audio generation in background thread"""
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'success': False, 'error': 'No script provided'})
    
    # Generate unique output name
    timestamp = int(time.time())
    output_name = f"podcast_{timestamp}"
    
    # Start generation in thread
    thread = threading.Thread(
        target=generate_podcast_audio_threaded,
        args=(script, output_name)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Audio generation started'})

@app.route('/audio-progress')
def get_audio_progress():
    """Get current audio generation progress"""
    return jsonify(audio_progress)

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated podcast file"""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=False)
    else:
        return "File not found", 404

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🎙️ UNIFIED AI PODCAST GENERATOR")
    print("="*80)
    print("\n✨ Features:")
    print("   • Script Generation: OpenRouter API (FREE model)")
    print("   • Audio Generation: ElevenLabs TTS")
    print("   • Beautiful Web Interface")
    print("   • Progress Tracking")
    print("   • Review & Edit Scripts")
    print("\n🌐 Open: http://localhost:5000")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=False, port=5000, threaded=True)
