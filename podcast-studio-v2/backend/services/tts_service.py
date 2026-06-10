import asyncio
import concurrent.futures
import edge_tts
from config import VOICE_LIBRARY

EMOTION_PARAMS = {
    "excited":    {"rate": "+15%", "pitch": "+5Hz"},
    "curious":    {"rate": "+5%",  "pitch": "+3Hz"},
    "emphasis":   {"rate": "+0%",  "pitch": "+2Hz"},
    "thoughtful": {"rate": "-10%", "pitch": "-2Hz"},
    "neutral":    {"rate": "+0%",  "pitch": "+0Hz"},
}


def parse_script(script: str) -> list:
    dialogues = []
    for line in script.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            parts = line.split(':', 1)
            speaker, text = parts[0].strip(), parts[1].strip()
            if speaker and text and len(speaker) <= 20:
                dialogues.append({"speaker": speaker, "text": text})
    return dialogues


def detect_speakers(dialogues: list) -> dict:
    speakers = sorted(set(d["speaker"] for d in dialogues))
    keys = list(VOICE_LIBRARY.keys())
    return {
        spk: {
            "voice_key": keys[i % len(keys)],
            "voice_info": VOICE_LIBRARY[keys[i % len(keys)]]
        }
        for i, spk in enumerate(speakers)
    }


def _detect_emotion(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['wow', 'amazing', 'incredible', 'awesome', 'zabardast', 'kya baat', '!!']):
        return "excited"
    if '?' in t or any(w in t for w in ['kya', 'really', 'sach', 'how', 'why']):
        return "curious"
    if any(w in t for w in ['important', 'must', 'critical', 'zaruri', 'bilkul']):
        return "emphasis"
    if any(w in t for w in ['think', 'believe', 'perhaps', 'maybe', 'shayad']):
        return "thoughtful"
    return "neutral"


def _tts_worker(text, voice, rate, pitch, output_path):
    """Runs in a dedicated thread with its own fresh event loop."""
    async def _do():
        c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await c.save(str(output_path))
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_do())
    finally:
        loop.close()


def generate_segment(voice_info: dict, text: str, output_path) -> str:
    """
    Generate one audio segment. Thread-safe: each call spawns its own
    dedicated thread with a fresh event loop, avoiding aiohttp conflicts
    when called from Flask's ThreadPoolExecutor workers.
    """
    emotion = _detect_emotion(text)
    params = EMOTION_PARAMS[emotion]
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        f = pool.submit(_tts_worker, text, voice_info["voice"], params["rate"], params["pitch"], output_path)
        f.result()
    return emotion
