"""
Web-based Podcast Generator using Ollama (Local AI)
No API limits, completely free!
"""

from flask import Flask, render_template_string, request, jsonify
import ollama
from utils import clean_script_text, normalize_speaker_labels, validate_script_lines
import config

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🦙 Ollama Podcast Generator</title>
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
            margin-top: 10px;
            font-size: 0.9em;
        }
        .content { padding: 40px; }
        .form-group { margin-bottom: 30px; }
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
            margin: 30px auto;
        }
        .btn:hover { transform: translateY(-3px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .loading { text-align: center; padding: 40px; display: none; }
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
        .result {
            display: none;
            margin-top: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        .result.active { display: block; }
        .result h2 { color: #667eea; margin-bottom: 20px; }
        .script-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            white-space: pre-wrap;
            line-height: 1.8;
            max-height: 600px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦙 Ollama Podcast Generator</h1>
            <p>Local AI - No API Limits - Completely Free!</p>
            <div class="badge">✅ Unlimited Podcasts</div>
        </div>
        
        <div class="content">
            <form id="podcastForm">
                <div class="form-group">
                    <label>📌 Blog Title (Optional)</label>
                    <input type="text" id="title" placeholder="Enter title...">
                </div>
                
                <div class="form-group">
                    <label>📝 Blog Content</label>
                    <textarea id="content" placeholder="Paste your blog..." required></textarea>
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
                
                <button type="submit" class="btn">✨ Generate Podcast</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <h3>Generating with Ollama...</h3>
                <p>This may take 30-90 seconds</p>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                    ⏳ AI is thinking... Please wait, don't refresh!
                </p>
            </div>
            
            <div class="result" id="result">
                <h2>🎉 Your Podcast Script</h2>
                <div class="script-content" id="scriptContent"></div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedType = 'single';
        let selectedAudience = 'global';
        
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
        
        document.getElementById('podcastForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const title = document.getElementById('title').value;
            const content = document.getElementById('content').value;
            
            if (!content.trim()) {
                alert('Please enter blog content!');
                return;
            }
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('result').classList.remove('active');
            
            try {
                // Create AbortController for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minutes
                
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title, content,
                        podcast_type: selectedType,
                        audience: selectedAudience
                    }),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('scriptContent').textContent = data.script;
                    document.getElementById('result').classList.add('active');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                if (error.name === 'AbortError') {
                    alert('Request timed out. The AI is taking too long. Please try with shorter content or try again.');
                } else {
                    alert('Error: ' + error.message);
                }
            } finally {
                document.getElementById('loading').classList.remove('active');
            }
        });
    </script>
</body>
</html>
"""

def generate_podcast(content, title, ptype, audience):
    """Generate podcast using Ollama with strict quality controls"""
    try:
        # Optimized audience instructions
        if audience == "indian":
            aud = "Indian Hinglish style - mix Hindi-English naturally. Use Indian examples. Professional tone."
        else:
            aud = "Global English - clear, professional. Universal examples. Conversational but polished."
        
        # Optimized type instructions
        if ptype == "single":
            fmt = """Single Host speaking to listeners.
Use "Host:" label only. Professional, warm, conversational.
Example: Host: Welcome everyone! Today we're exploring something fascinating..."""
        elif ptype == "co-host":
            fmt = """Two hosts (Alex and Sam) in dialogue.
Alternate every 2-3 lines. Natural questions and answers.
Example:
Alex: This topic is really interesting.
Sam: Absolutely! What caught your attention most?"""
        else:
            fmt = """Three hosts: Alex (moderator), Jordan (expert), Casey (curious).
All participate with different perspectives.
Example:
Alex: Let's explore this. Jordan, your thoughts?
Jordan: The key point is...
Casey: Can you explain that more?"""
        
        # STRICT prompt to prevent bad output
        prompt = f"""You are a professional podcast script writer. Create a clean, speakable podcast script.

FORMAT: {fmt}
AUDIENCE: {aud}

CRITICAL RULES - FOLLOW EXACTLY:
1. NO emojis - absolutely none (no 🤖 🚀 💡 etc)
2. NO stage directions - no *laughs*, *smiles*, (parentheses)
3. NO actions in brackets [like this]
4. ONLY dialogue that can be spoken out loud
5. Use proper speaker labels: "Host:", "Alex:", "Sam:"
6. Professional language - no "Yo", "fam", overly casual slang
7. Complete sentences - no cut-off endings
8. 8-12 exchanges, 300-400 words total
9. Natural conversation style
10. No repetition of ideas

TOPIC: {title if title else "Untitled"}
CONTENT: {content}

Write ONLY the dialogue. Start now:
"""
        
        response = ollama.chat(
            model='llama2',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a professional podcast script writer. Write only clean, speakable dialogue with no emojis, no stage directions, no actions. Just natural conversation.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 600
            }
        )
        
        script = response['message']['content']
        
        # Aggressive post-processing to remove bad elements
        import re
        
        # Remove emojis
        script = re.sub(r'[^\x00-\x7F]+', '', script)
        
        # Remove stage directions
        script = re.sub(r'\*[^*]+\*', '', script)
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        
        # Remove music/sound cues
        script = script.replace('[INTRO MUSIC', '').replace('[OUTRO MUSIC', '')
        script = script.replace('[MUSIC]', '').replace('[SOUND', '')
        
        # Fix speaker label inconsistencies
        script = script.replace('Host 1:', 'Alex:')
        script = script.replace('Host 2:', 'Sam:')
        script = script.replace('Host1:', 'Alex:')
        script = script.replace('Host2:', 'Sam:')
        script = script.replace('Host 1 :', 'Alex:')
        script = script.replace('Host 2 :', 'Sam:')
        
        # Clean up extra spaces
        script = re.sub(r'\s+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n+', '\n', script)
        
        # Remove lines that are just actions or empty
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line and ':' in line and len(line) > 10:
                # Check if line has actual content after speaker label
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 5:
                    lines.append(line)
        
        script = '\n\n'.join(lines)
        script = script.strip()
        
        return {
            'success': True,
            'script': script
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    result = generate_podcast(
        data['content'],
        data.get('title', ''),
        data['podcast_type'],
        data.get('audience', 'global')
    )
    return jsonify(result)

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🦙 OLLAMA PODCAST GENERATOR - WEB APP")
    print("="*80)
    print("\n✅ No API limits!")
    print("✅ Completely free!")
    print("✅ Runs locally!")
    print("\n🌐 Open: http://localhost:5000")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=True, port=5000)
