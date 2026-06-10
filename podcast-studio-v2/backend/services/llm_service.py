import re
import requests
from config import OPENROUTER_API_KEY

# Free models to try in order — first one that works wins
FREE_MODELS = [
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-3-1b-it:free",
]


def generate_ai_podcast(content: str, title: str, ptype: str, audience: str) -> dict:
    """Generate podcast script via OpenRouter. Returns {success, script} or {success, error}."""
    if not OPENROUTER_API_KEY:
        return {"success": False, "error": "OPENROUTER_API_KEY not set in .env"}

    prompt = _build_prompt(content, title, ptype, audience)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "Podcast Studio v2",
    }

    last_error = "All models failed."
    for model in FREE_MODELS:
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional podcast script writer. Follow format exactly. NO emojis, NO stage directions, ONLY dialogue.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1200,
                    "temperature": 0.8,
                },
                timeout=60,
            )

            if resp.status_code == 200:
                data = resp.json()
                script = data["choices"][0]["message"]["content"]
                script = _clean_script(script, ptype)
                if len(script) > 100:
                    return {"success": True, "script": script, "model": model}
                last_error = f"Model {model} returned empty script."

            elif resp.status_code == 401:
                return {
                    "success": False,
                    "error": (
                        "OpenRouter API key is invalid or has no credits. "
                        "Get a free key at https://openrouter.ai — it's free to sign up. "
                        "Then update OPENROUTER_API_KEY in backend/.env"
                    ),
                }
            else:
                last_error = f"Model {model}: HTTP {resp.status_code} — {resp.text[:200]}"

        except requests.Timeout:
            last_error = f"Model {model} timed out."
        except Exception as e:
            last_error = f"Model {model} error: {str(e)}"

    return {"success": False, "error": last_error}


def _build_prompt(content: str, title: str, ptype: str, audience: str) -> str:
    if audience == "indian":
        lang = (
            "Indian Hinglish — mix Hindi and English naturally like Indians speak. "
            "Use: dekho, yaar, acha, toh, bahut, kya, matlab, bilkul, sahi, haan, bhai. "
            "Start sentences in Hindi, add English words naturally."
        )
    else:
        lang = "English — clear, professional, conversational, engaging."

    if ptype == "single":
        fmt = 'SINGLE HOST ONLY — use label "Host:" for every line.'
    elif ptype == "co-host":
        fmt = "TWO HOSTS — Alex and Sam in natural back-and-forth dialogue."
    else:
        fmt = "THREE HOSTS — Alex (moderator), Jordan (expert), Casey (curious learner)."

    return (
        f"Convert the blog below into an engaging podcast script.\n\n"
        f"LANGUAGE: {lang}\n"
        f"FORMAT: {fmt}\n\n"
        f"RULES:\n"
        f"- NO emojis, NO stage directions, NO asterisks, NO brackets\n"
        f"- ONLY speakable dialogue\n"
        f"- 18-22 exchanges, ~500 words\n"
        f"- Each speaker on its own line: SpeakerName: dialogue\n\n"
        f"TOPIC: {title or 'Untitled'}\n\n"
        f"BLOG:\n{content[:8000]}\n\nWrite ONLY the dialogue:"
    )


def _clean_script(script: str, ptype: str) -> str:
    script = re.sub(r'\*[^*]+\*', '', script)
    script = re.sub(r'\([^)]+\)', '', script)
    script = re.sub(r'\[[^\]]+\]', '', script)
    script = re.sub(r'[ \t]+', ' ', script)

    if ptype == "single":
        script = re.sub(r'(Alex|Sam|Jordan|Casey|Host\s*\d*):', 'Host:', script)
    elif ptype == "co-host":
        script = re.sub(r'Host\s*1:', 'Alex:', script)
        script = re.sub(r'Host\s*2:', 'Sam:', script)
        script = re.sub(r'(Jordan|Casey):', 'Sam:', script)
        script = re.sub(r'^Host:', 'Alex:', script, flags=re.MULTILINE)
    else:
        script = re.sub(r'Host\s*1:', 'Alex:', script)
        script = re.sub(r'Host\s*2:', 'Jordan:', script)
        script = re.sub(r'Host\s*3:', 'Casey:', script)
        script = re.sub(r'^Host:', 'Alex:', script, flags=re.MULTILINE)

    lines = []
    for line in script.split('\n'):
        line = line.strip()
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2 and len(parts[0].strip()) <= 20 and len(parts[1].strip()) > 5:
                lines.append(line)

    return '\n\n'.join(lines).strip()
