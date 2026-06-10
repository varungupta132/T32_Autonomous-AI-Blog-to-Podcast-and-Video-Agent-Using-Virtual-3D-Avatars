"""
Web-based Podcast Generator using OpenRouter API
High-quality podcast generation with advanced AI models
"""

from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
import re

app = Flask(__name__)

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

HTML_TEMPLATE = """
<!DOCTYPE html> 
<html>
<head>
    <title>🎙️ AI Podcast Generator</title>
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
            white-space: pre-line;
            line-height: 2.2;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 15px;
        }
        .script-content::before {
            content: "📜 Podcast Script";
            display: block;
            font-weight: bold;
            margin-bottom: 15px;
            color: #667eea;
            font-family: 'Segoe UI', sans-serif;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎙️ AI Podcast Generator</h1>
            <p>Powered by OpenRouter AI - High Quality Scripts</p>
            <div class="badge">✨ Professional Quality</div>
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
                <h3>Generating with AI...</h3>
                <p>Creating your professional podcast script...</p>
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
                const timeoutId = setTimeout(() => controller.abort(), 120000);
                
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
    """Generate podcast using OpenRouter API - OPTIMIZED to 1 API call only"""
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

        # Single optimized prompt - NO extraction step
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

        # Single API call - OPTIMIZED
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free",
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
        script = script.replace('INTRO MUSIC', '').replace('OUTRO MUSIC', '')

        # Fix speaker labels based on type
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

        # Clean up spacing - PRESERVE newlines between speakers
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

        # Join with double newlines for clear separation
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
    print("🎙️ AI PODCAST GENERATOR - OPENROUTER API")
    print("="*80)
    print("\n✨ High-quality AI models!")
    print("✨ Professional podcast scripts!")
    print("✨ Fast generation!")
    print("\n🌐 Open: http://localhost:5000")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=False, port=5000)
