import requests
import json
from config import settings

class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
    
    def generate_script(self, blog: str, podcast_type: str, audience: str, language_style: str) -> str:
        """Generate podcast script using Ollama with post-processing"""
        
        system_prompt = self._build_system_prompt(podcast_type, audience, language_style)
        user_prompt = f"Convert this blog into a podcast script:\n\n{blog}"
        
        # Combine into single strong prompt
        full_prompt = f"""{system_prompt}

BLOG CONTENT TO CONVERT:
{blog}

NOW WRITE THE PODCAST SCRIPT (remember: {podcast_type} format, {audience} audience, {language_style} style):
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 600,
                        "repeat_penalty": 1.2  # Prevent repetition
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            script = result.get("response", "").strip()
            
            # Post-process to clean up the script
            script = self._clean_script(script, podcast_type)
            
            return script
        
        except requests.exceptions.Timeout:
            raise Exception("LLM request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM service error: {str(e)}")
    
    def _clean_script(self, script: str, podcast_type: str) -> str:
        """Aggressive post-processing to remove bad elements and enforce format"""
        import re
        
        # Remove emojis (non-ASCII characters)
        script = re.sub(r'[^\x00-\x7F]+', '', script)
        
        # Remove stage directions
        script = re.sub(r'\*[^*]+\*', '', script)
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        
        # Remove music/sound cues
        script = script.replace('[INTRO MUSIC', '').replace('[OUTRO MUSIC', '')
        script = script.replace('[MUSIC]', '').replace('[SOUND', '')
        
        # Normalize speaker labels based on podcast type
        if podcast_type == "single":
            # Force single host only
            script = re.sub(r'(Host\s*\d*|Co-?host|Cohost|Guest|Expert)\s*:', 'HOST:', script, flags=re.IGNORECASE)
        elif podcast_type == "cohost":
            # Force two hosts only
            script = re.sub(r'Host\s*1\s*:', 'HOST:', script, flags=re.IGNORECASE)
            script = re.sub(r'Host\s*2\s*:', 'COHOST:', script, flags=re.IGNORECASE)
            script = re.sub(r'Co-?host\s*:', 'COHOST:', script, flags=re.IGNORECASE)
            # Remove any third speaker
            script = re.sub(r'(Guest|Expert|Host\s*3)\s*:.*?(?=\n|$)', '', script, flags=re.IGNORECASE)
        else:  # multi
            script = re.sub(r'Host\s*1\s*:', 'HOST:', script, flags=re.IGNORECASE)
            script = re.sub(r'Host\s*2\s*:', 'COHOST:', script, flags=re.IGNORECASE)
            script = re.sub(r'Host\s*3\s*:', 'EXPERT:', script, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        script = re.sub(r'\s+', ' ', script)
        script = re.sub(r' +\n', '\n', script)
        script = re.sub(r'\n+', '\n', script)
        
        # Remove lines that are just actions or empty
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line and ':' in line and len(line) > 10:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 5:
                    lines.append(line)
        
        script = '\n\n'.join(lines)
        script = script.strip()
        
        return script
    
    def _build_system_prompt(self, podcast_type: str, audience: str, language_style: str) -> str:
        """Build dynamic system prompt with strict quality controls"""
        
        # Base system instruction
        base_prompt = """You are a professional podcast script writer. Create a clean, speakable podcast script.

CRITICAL RULES - FOLLOW EXACTLY:
1. NO emojis - absolutely none (no 🤖 🚀 💡 etc)
2. NO stage directions - no *laughs*, *smiles*, (parentheses)
3. NO actions in brackets [like this]
4. ONLY dialogue that can be spoken out loud
5. Use proper speaker labels followed by colon
6. Professional language - no "Yo", "fam", overly casual slang
7. Complete sentences - no cut-off endings
8. 8-12 exchanges, 300-400 words total
9. Natural conversation style
10. No repetition of ideas

OUTPUT FORMAT:
Each line must be: SPEAKER: dialogue
Example:
HOST: Welcome to today's episode!
COHOST: Thanks for having me. This topic is fascinating.
"""
        
        # Podcast type instructions
        if podcast_type == "single":
            base_prompt += """\nPODCAST TYPE: Single Host
- ONE HOST only, speaking to listeners
- Use "HOST:" label only
- Professional, warm, conversational tone
- Direct address to audience
- Example:
HOST: Welcome everyone! Today we're exploring something fascinating.
HOST: Let me break this down for you.
HOST: The key point here is really important.
"""
        elif podcast_type == "cohost":
            base_prompt += """\nPODCAST TYPE: Co-Host Dialogue
- TWO hosts: HOST and COHOST
- Alternate every 2-3 lines
- Natural questions and answers
- Build on each other's points
- Example:
HOST: This topic is really interesting.
COHOST: Absolutely! What caught your attention most?
HOST: Well, the main thing is...
COHOST: That makes sense. Can you explain more?
"""
        else:  # multi
            base_prompt += """\nPODCAST TYPE: Multi-Host Panel
- THREE hosts: HOST (moderator), COHOST (expert), EXPERT (analyst)
- All participate with different perspectives
- HOST guides the conversation
- Example:
HOST: Let's explore this. COHOST, your thoughts?
COHOST: The key point is...
EXPERT: I'd add that...
HOST: Interesting perspectives from both of you.
"""
        
        # Audience instructions
        if audience == "india":
            base_prompt += """\nAUDIENCE: Indian
- Tone: Relatable to Indian audience
- Use examples relevant to India
- Cultural context matters
"""
            if language_style == "hinglish":
                base_prompt += """- Language: Hinglish - mix Hindi-English naturally
- Example: "Yeh technology bahut interesting hai"
- Use common Hindi words naturally integrated
"""
            else:
                base_prompt += "- Language: Clear English with Indian context\n"
        else:
            base_prompt += """\nAUDIENCE: Global
- Tone: Universal appeal, professional
- Use internationally relevant examples
- Clear, accessible language
- Language: Professional English
"""
        
        base_prompt += """\n
STRUCTURE:
1. Start with engaging hook (1-2 exchanges)
2. Main content discussion (natural flow, 6-8 exchanges)
3. Short outro (1-2 exchanges)

Remember: Write ONLY speakable dialogue. No emojis, no actions, no stage directions.
Start the podcast script now:
"""
        
        return base_prompt
