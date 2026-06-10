"""
Web-based Podcast Generator using Ollama (Local AI) - FIXED VERSION
No API limits, completely free!
FIXES: No unanswered questions, better Hinglish grammar, natural mixing
"""

from flask import Flask, render_template_string, request, jsonify
import ollama
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🦙 Ollama Podcast Generator (Fixed)</title>
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
            <p>Local AI - Fixed Version - No API Limits!</p>
            <div class="badge">✅ Improved Quality</div>
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
            </div>
            
            <div class="result" id="result">
                <h2>🎉 Your Podcast Script</h2>
                <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                    <strong>🎙️ Type:</strong> <span id="resultType">Single</span> | 
                    <strong>🌍 Audience:</strong> <span id="resultAudience">Global</span>
                </div>
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
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 180000);
                
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
                    document.getElementById('resultType').textContent = selectedType.charAt(0).toUpperCase() + selectedType.slice(1);
                    document.getElementById('resultAudience').textContent = selectedAudience.charAt(0).toUpperCase() + selectedAudience.slice(1);
                    document.getElementById('result').classList.add('active');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                if (error.name === 'AbortError') {
                    alert('Request timed out. Please try again.');
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
    """Generate podcast using Ollama with FIXED prompts"""
    try:
        # Step 1: Extract key points
        extraction_prompt = f"""Extract the main points from this blog in a simple list:

{content}

List only key points, one per line."""

        extraction_response = ollama.chat(
            model='llama2',
            messages=[{'role': 'user', 'content': extraction_prompt}],
            options={'temperature': 0.3, 'num_predict': 300}
        )
        
        key_points = extraction_response['message']['content']
        
        # Step 2: Language instructions - FIXED for better Hinglish
        if audience == "indian":
            aud = """Hinglish - Mix Hindi and English NATURALLY in EVERY sentence.
Hindi words to use: acha, toh, dekho, yaar, bahut, kya, matlab, bilkul, sahi, haan, nahi, bhai.
Example: "Acha toh dekho yaar, AI ka matlab hai machines bhi soch sakti hain."
Mix throughout sentence, not just at start or end. Keep grammar simple."""
        else:
            aud = "English - clear, conversational, engaging."
        
        # Step 3: Format instructions - FIXED to prevent unanswered questions
        if ptype == "single":
            fmt = """SINGLE HOST - Use ONLY "Host:" label.
CRITICAL FIX: Host speaks TO listeners, NOT asking them questions!
Use rhetorical questions that host answers immediately.

WRONG: "What do you think?" (listener can't answer)
RIGHT: "You might wonder what this means. Let me explain..."

Example:
Host: Welcome! Today we explore AI.
Host: What is AI? It's technology that makes machines smart.
Host: Why does this matter? Because it changes our daily lives."""
        elif ptype == "co-host":
            fmt = """TWO HOSTS - Alex and Sam discuss together.
They ask EACH OTHER questions.
Example:
Alex: This is interesting!
Sam: What caught your attention?
Alex: The impact on education."""
        else:
            fmt = """THREE HOSTS - Alex, Jordan, Casey discuss together.
They ask EACH OTHER questions.
Example:
Alex: Jordan, your thoughts?
Jordan: The key is AI learns from data.
Casey: Can you explain more?"""
        
        # Step 4: Create podcast - STRICT RULES
        podcast_prompt = f"""Create an engaging podcast script.

KEY POINTS:
{key_points}

FORMAT: {fmt}
LANGUAGE: {aud}

STRUCTURE:
1. INTRO (2-3 lines): Welcome, introduce topic
2. DISCUSSION (10-14 lines): Explain key points
3. OUTRO (2-3 lines): Thank listeners

CRITICAL RULES:
1. NO emojis
2. NO stage directions
3. ONLY dialogue
4. Single host: Use rhetorical questions you answer immediately. DO NOT ask listeners questions!
5. Hinglish: Mix Hindi and English in EVERY sentence naturally
6. Keep grammar simple
7. 15-18 exchanges, 450-550 words
8. Natural and engaging

TOPIC: {title if title else "Untitled"}

Write dialogue only:
"""
        
        # Step 5: Generate with better system prompt
        if ptype == "single":
            sys_msg = 'Podcast writer. Single host explains to listeners. Use rhetorical questions host answers. NO questions to listeners.'
        else:
            sys_msg = 'Podcast writer. Hosts discuss with each other, asking each other questions.'
        
        response = ollama.chat(
            model='llama2',
            messages=[
                {'role': 'system', 'content': sys_msg},
                {'role': 'user', 'content': podcast_prompt}
            ],
            options={'temperature': 0.75, 'top_p': 0.9, 'num_predict': 700}
        )
        
        script = response['message']['content']
        
        # Post-processing
        script = re.sub(r'[^\x00-\x7F]+', '', script)
        script = re.sub(r'\*[^*]+\*', '', script)
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        script = script.replace('[INTRO MUSIC', '').replace('[OUTRO MUSIC', '')
        script = script.replace('[MUSIC]', '').replace('[SOUND', '')
        
        # Fix speaker labels
        if ptype == "single":
            script = re.sub(r'(Alex|Sam|Jordan|Casey):', 'Host:', script)
        elif ptype == "co-host":
            script = script.replace('Host 1:', 'Alex:')
            script = script.replace('Host 2:', 'Sam:')
            script = script.replace('Host:', 'Alex:')
            script = re.sub(r'(Jordan|Casey):', 'Sam:', script)
        else:
            script = script.replace('Host:', 'Alex:')
            script = script.replace('Host 1:', 'Alex:')
            script = script.replace('Host 2:', 'Jordan:')
            script = script.replace('Host 3:', 'Casey:')
        
        # Clean spacing
        script = re.sub(r'\s+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n+', '\n', script)
        
        # Extract dialogue lines
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
    print("🦙 OLLAMA PODCAST GENERATOR - FIXED VERSION")
    print("="*80)
    print("\n✅ Fixed: No unanswered questions!")
    print("✅ Fixed: Better Hinglish grammar!")
    print("✅ Fixed: Natural language mixing!")
    print("\n🌐 Open: http://localhost:5000")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=True, port=5000)
