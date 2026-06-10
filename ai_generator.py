import re
from openai import OpenAI

OPENAI_API_KEY = ""

def generate_ai_podcast(content, title, ptype, audience, api_key=None):
    """Generate podcast script using OpenRouter API"""
    try:
        current_api_key = api_key if api_key else OPENAI_API_KEY
        if not current_api_key:
            return {'success': False, 'error': "No OpenRouter API key provided."}
            
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=current_api_key,
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
            fmt = """SINGLE SPEAKER ONLY (1 person). Focus on direct engaging narration to the listeners."""
        else:
            fmt = """DYNAMIC CONVERSATION. You MUST accurately reflect the people mentioned in the blog content. Use their EXACT NAMES and include ALL of them in the dialogue. If no specific names are mentioned, default to a two-person natural dialogue."""

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
10. EXTREMELY IMPORTANT: Extract the EXACT names of the people provided in the BLOG CONTENT and use them as the speakers. Do NOT invent alternative names or drop anyone.
11. Do NOT use generic labels like 'Host 1' or 'Speaker A'.

TOPIC: {title if title else "Untitled"}

BLOG CONTENT:
{content}

Write ONLY the dialogue. Start now:
"""

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
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
        script = script.replace('*', '')
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        script = script.replace('INTRO MUSIC', '').replace('OUTRO MUSIC', '')
        script = script.replace('MUSIC', '').replace('SOUND', '')

        # Basic cleanup of fallback generic names to ensure presentation is clean
        script = script.replace('Host 1:', 'Speaker 1:')
        script = script.replace('Host 2:', 'Speaker 2:')
        script = script.replace('Host 3:', 'Speaker 3:')

        script = re.sub(r'[ \t]+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n\n+', '\n\n', script)

        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line and ':' in line and len(line) > 3:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 1:
                    lines.append(line)

        script = '\n\n'.join(lines)
        script = script.strip()

        return {'success': True, 'script': script}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
