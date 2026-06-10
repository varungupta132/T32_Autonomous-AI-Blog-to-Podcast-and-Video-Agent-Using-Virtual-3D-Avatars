"""
Interactive Podcast Studio - EdgeTTS + OpenRouter AI
Multilingual Edition
"""

import re
import os
import asyncio
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, render_template, request, jsonify, send_file, Response
import edge_tts
from openai import OpenAI

# Video generation requires local GPU (Wav2Lip + FFmpeg).
# Set VIDEO_ENABLED=true env var only when running locally with GPU.
VIDEO_ENABLED = os.environ.get("VIDEO_ENABLED", "false").lower() == "true"
if VIDEO_ENABLED:
    try:
        from video_engine import generate_podcast_video
    except ImportError:
        VIDEO_ENABLED = False
        print("[video] video_engine import failed — video disabled")

# Content extraction helpers
try:
    import requests
    from bs4 import BeautifulSoup
    URL_SUPPORT = True
except ImportError:
    URL_SUPPORT = False

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

FREE_MODELS = [
    "nvidia/nemotron-3-nano-30b-a3b:free",
]

# ============================================================================
# MULTILINGUAL VOICE LIBRARY
# Each language gets male + female EdgeTTS voices
# ============================================================================

LANG_VOICES = {
    "english":    [{"voice": "en-IN-PrabhatNeural",  "name": "Prabhat (EN Male)"},
                   {"voice": "en-IN-NeerjaNeural",   "name": "Neerja (EN Female)"}],
    "hinglish":   [{"voice": "en-IN-PrabhatNeural",  "name": "Prabhat (Hinglish Male)"},
                   {"voice": "en-IN-NeerjaNeural",   "name": "Neerja (Hinglish Female)"}],
    "hindi":      [{"voice": "hi-IN-MadhurNeural",   "name": "Madhur (HI Male)"},
                   {"voice": "hi-IN-SwaraNeural",    "name": "Swara (HI Female)"}],
    "urdu":       [{"voice": "ur-PK-AsadNeural",     "name": "Asad (UR Male)"},
                   {"voice": "ur-PK-UzmaNeural",     "name": "Uzma (UR Female)"}],
    "arabic":     [{"voice": "ar-SA-HamedNeural",    "name": "Hamed (AR Male)"},
                   {"voice": "ar-SA-ZariyahNeural",  "name": "Zariyah (AR Female)"}],
    "spanish":    [{"voice": "es-ES-AlvaroNeural",   "name": "Alvaro (ES Male)"},
                   {"voice": "es-ES-ElviraNeural",   "name": "Elvira (ES Female)"}],
    "french":     [{"voice": "fr-FR-HenriNeural",    "name": "Henri (FR Male)"},
                   {"voice": "fr-FR-DeniseNeural",   "name": "Denise (FR Female)"}],
    "german":     [{"voice": "de-DE-ConradNeural",   "name": "Conrad (DE Male)"},
                   {"voice": "de-DE-KatjaNeural",    "name": "Katja (DE Female)"}],
    "portuguese": [{"voice": "pt-BR-AntonioNeural",  "name": "Antonio (PT Male)"},
                   {"voice": "pt-BR-FranciscaNeural","name": "Francisca (PT Female)"}],
    "russian":    [{"voice": "ru-RU-DmitryNeural",   "name": "Dmitry (RU Male)"},
                   {"voice": "ru-RU-SvetlanaNeural", "name": "Svetlana (RU Female)"}],
    "chinese":    [{"voice": "zh-CN-YunxiNeural",    "name": "Yunxi (ZH Male)"},
                   {"voice": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao (ZH Female)"}],
    "japanese":   [{"voice": "ja-JP-KeitaNeural",    "name": "Keita (JA Male)"},
                   {"voice": "ja-JP-NanamiNeural",   "name": "Nanami (JA Female)"}],
    "korean":     [{"voice": "ko-KR-InJoonNeural",   "name": "InJoon (KO Male)"},
                   {"voice": "ko-KR-SunHiNeural",    "name": "SunHi (KO Female)"}],
    "italian":    [{"voice": "it-IT-DiegoNeural",    "name": "Diego (IT Male)"},
                   {"voice": "it-IT-ElsaNeural",     "name": "Elsa (IT Female)"}],
    "turkish":    [{"voice": "tr-TR-AhmetNeural",    "name": "Ahmet (TR Male)"},
                   {"voice": "tr-TR-EmelNeural",     "name": "Emel (TR Female)"}],
    "dutch":      [{"voice": "nl-NL-MaartenNeural",  "name": "Maarten (NL Male)"},
                   {"voice": "nl-NL-ColetteNeural",  "name": "Colette (NL Female)"}],
    "polish":     [{"voice": "pl-PL-MarekNeural",    "name": "Marek (PL Male)"},
                   {"voice": "pl-PL-ZofiaNeural",    "name": "Zofia (PL Female)"}],
    "swedish":    [{"voice": "sv-SE-MattiasNeural",  "name": "Mattias (SV Male)"},
                   {"voice": "sv-SE-SofieNeural",    "name": "Sofie (SV Female)"}],
    "indonesian": [{"voice": "id-ID-ArdiNeural",     "name": "Ardi (ID Male)"},
                   {"voice": "id-ID-GadisNeural",    "name": "Gadis (ID Female)"}],
    "bengali":    [{"voice": "bn-IN-BashkarNeural",  "name": "Bashkar (BN Male)"},
                   {"voice": "bn-IN-TanishaaNeural", "name": "Tanishaa (BN Female)"}],
    "tamil":      [{"voice": "ta-IN-ValluvarNeural", "name": "Valluvar (TA Male)"},
                   {"voice": "ta-IN-PallaviNeural",  "name": "Pallavi (TA Female)"}],
    "telugu":     [{"voice": "te-IN-MohanNeural",    "name": "Mohan (TE Male)"},
                   {"voice": "te-IN-ShrutiNeural",   "name": "Shruti (TE Female)"}],
    "vietnamese": [{"voice": "vi-VN-NamMinhNeural",  "name": "NamMinh (VI Male)"},
                   {"voice": "vi-VN-HoaiMyNeural",   "name": "HoaiMy (VI Female)"}],
    "thai":       [{"voice": "th-TH-NiwatNeural",    "name": "Niwat (TH Male)"},
                   {"voice": "th-TH-PremwadeeNeural","name": "Premwadee (TH Female)"}],
    "greek":      [{"voice": "el-GR-NestorasNeural", "name": "Nestoras (EL Male)"},
                   {"voice": "el-GR-AthinaNeural",   "name": "Athina (EL Female)"}],
    "czech":      [{"voice": "cs-CZ-AntoninNeural",  "name": "Antonin (CS Male)"},
                   {"voice": "cs-CZ-VlastaNeural",   "name": "Vlasta (CS Female)"}],
    "romanian":   [{"voice": "ro-RO-EmilNeural",     "name": "Emil (RO Male)"},
                   {"voice": "ro-RO-AlinaNeural",    "name": "Alina (RO Female)"}],
    "hungarian":  [{"voice": "hu-HU-TamasNeural",    "name": "Tamas (HU Male)"},
                   {"voice": "hu-HU-NoemiNeural",    "name": "Noemi (HU Female)"}],
    "danish":     [{"voice": "da-DK-JeppeNeural",    "name": "Jeppe (DA Male)"},
                   {"voice": "da-DK-ChristelNeural", "name": "Christel (DA Female)"}],
    "finnish":    [{"voice": "fi-FI-HarriNeural",    "name": "Harri (FI Male)"},
                   {"voice": "fi-FI-NooraNeural",    "name": "Noora (FI Female)"}],
    "norwegian":  [{"voice": "nb-NO-FinnNeural",     "name": "Finn (NO Male)"},
                   {"voice": "nb-NO-PernilleNeural", "name": "Pernille (NO Female)"}],
    "ukrainian":  [{"voice": "uk-UA-OstapNeural",    "name": "Ostap (UK Male)"},
                   {"voice": "uk-UA-PolinaNeural",   "name": "Polina (UK Female)"}],
    "malay":      [{"voice": "ms-MY-OsmanNeural",    "name": "Osman (MS Male)"},
                   {"voice": "ms-MY-YasminNeural",   "name": "Yasmin (MS Female)"}],
    "filipino":   [{"voice": "fil-PH-AngeloNeural",  "name": "Angelo (FIL Male)"},
                   {"voice": "fil-PH-BlessicaNeural","name": "Blessica (FIL Female)"}],
    "swahili":    [{"voice": "sw-KE-RafikiNeural",   "name": "Rafiki (SW Male)"},
                   {"voice": "sw-KE-ZuriNeural",     "name": "Zuri (SW Female)"}],
    "afrikaans":  [{"voice": "af-ZA-WillemNeural",   "name": "Willem (AF Male)"},
                   {"voice": "af-ZA-AdriNeural",     "name": "Adri (AF Female)"}],
    "catalan":    [{"voice": "ca-ES-EnricNeural",    "name": "Enric (CA Male)"},
                   {"voice": "ca-ES-JoanaNeural",    "name": "Joana (CA Female)"}],
    "croatian":   [{"voice": "hr-HR-SreckoNeural",   "name": "Srecko (HR Male)"},
                   {"voice": "hr-HR-GabrijelaNeural","name": "Gabrijela (HR Female)"}],
    "slovak":     [{"voice": "sk-SK-LukasNeural",    "name": "Lukas (SK Male)"},
                   {"voice": "sk-SK-ViktoriaNeural", "name": "Viktoria (SK Female)"}],
    "bulgarian":  [{"voice": "bg-BG-BorislavNeural", "name": "Borislav (BG Male)"},
                   {"voice": "bg-BG-KalinaNeural",   "name": "Kalina (BG Female)"}],
    "lithuanian": [{"voice": "lt-LT-LeonasNeural",   "name": "Leonas (LT Male)"},
                   {"voice": "lt-LT-OnaNeural",      "name": "Ona (LT Female)"}],
    "latvian":    [{"voice": "lv-LV-NilsNeural",     "name": "Nils (LV Male)"},
                   {"voice": "lv-LV-EveritaNeural",  "name": "Everita (LV Female)"}],
    "estonian":   [{"voice": "et-EE-KertNeural",     "name": "Kert (ET Male)"},
                   {"voice": "et-EE-AnuNeural",      "name": "Anu (ET Female)"}],
    "slovenian":  [{"voice": "sl-SI-RokNeural",      "name": "Rok (SL Male)"},
                   {"voice": "sl-SI-PetraNeural",    "name": "Petra (SL Female)"}],
    "albanian":   [{"voice": "sq-AL-IlirNeural",     "name": "Ilir (SQ Male)"},
                   {"voice": "sq-AL-AnilaNeural",    "name": "Anila (SQ Female)"}],
    "macedonian": [{"voice": "mk-MK-AleksandarNeural","name": "Aleksandar (MK Male)"},
                   {"voice": "mk-MK-MarijaNeural",   "name": "Marija (MK Female)"}],
    "georgian":   [{"voice": "ka-GE-GiorgiNeural",   "name": "Giorgi (KA Male)"},
                   {"voice": "ka-GE-EkaNeural",      "name": "Eka (KA Female)"}],
    "armenian":   [{"voice": "hy-AM-HaykNeural",     "name": "Hayk (HY Male)"},
                   {"voice": "hy-AM-AnahitNeural",   "name": "Anahit (HY Female)"}],
    "azerbaijani":[{"voice": "az-AZ-BabekNeural",    "name": "Babek (AZ Male)"},
                   {"voice": "az-AZ-BanuNeural",     "name": "Banu (AZ Female)"}],
    "kazakh":     [{"voice": "kk-KZ-DauletNeural",   "name": "Daulet (KK Male)"},
                   {"voice": "kk-KZ-AigulNeural",    "name": "Aigul (KK Female)"}],
    "uzbek":      [{"voice": "uz-UZ-SardorNeural",   "name": "Sardor (UZ Male)"},
                   {"voice": "uz-UZ-MadinaNeural",   "name": "Madina (UZ Female)"}],
    "mongolian":  [{"voice": "mn-MN-BataaNeural",    "name": "Bataa (MN Male)"},
                   {"voice": "mn-MN-YesuiNeural",    "name": "Yesui (MN Female)"}],
    "nepali":     [{"voice": "ne-NP-SagarNeural",    "name": "Sagar (NE Male)"},
                   {"voice": "ne-NP-HemkalaNeural",  "name": "Hemkala (NE Female)"}],
    "sinhala":    [{"voice": "si-LK-SameeraNeural",  "name": "Sameera (SI Male)"},
                   {"voice": "si-LK-ThiliniNeural",  "name": "Thilini (SI Female)"}],
    "khmer":      [{"voice": "km-KH-PisethNeural",   "name": "Piseth (KM Male)"},
                   {"voice": "km-KH-SreymomNeural",  "name": "Sreymom (KM Female)"}],
    "lao":        [{"voice": "lo-LA-ChanthavongNeural","name": "Chanthavong (LO Male)"},
                   {"voice": "lo-LA-KeomanyNeural",  "name": "Keomany (LO Female)"}],
    "burmese":    [{"voice": "my-MM-ThihaNeural",    "name": "Thiha (MY Male)"},
                   {"voice": "my-MM-NilarNeural",    "name": "Nilar (MY Female)"}],
    "amharic":    [{"voice": "am-ET-AmehaNeural",    "name": "Ameha (AM Male)"},
                   {"voice": "am-ET-MekdesNeural",   "name": "Mekdes (AM Female)"}],
    "persian":    [{"voice": "fa-IR-FaridNeural",    "name": "Farid (FA Male)"},
                   {"voice": "fa-IR-DilaraNeural",   "name": "Dilara (FA Female)"}],
    "hebrew":     [{"voice": "he-IL-AvriNeural",     "name": "Avri (HE Male)"},
                   {"voice": "he-IL-HilaNeural",     "name": "Hila (HE Female)"}],
    "marathi":    [{"voice": "mr-IN-ManoharNeural",  "name": "Manohar (MR Male)"},
                   {"voice": "mr-IN-AarohiNeural",   "name": "Aarohi (MR Female)"}],
    "gujarati":   [{"voice": "gu-IN-NiranjanNeural", "name": "Niranjan (GU Male)"},
                   {"voice": "gu-IN-DhwaniNeural",   "name": "Dhwani (GU Female)"}],
    "kannada":    [{"voice": "kn-IN-GaganNeural",    "name": "Gagan (KN Male)"},
                   {"voice": "kn-IN-SapnaNeural",    "name": "Sapna (KN Female)"}],
    "malayalam":  [{"voice": "ml-IN-MidhunNeural",   "name": "Midhun (ML Male)"},
                   {"voice": "ml-IN-SobhanaNeural",  "name": "Sobhana (ML Female)"}],
    "punjabi":    [{"voice": "pa-IN-OjasNeural",     "name": "Ojas (PA Male)"},
                   {"voice": "pa-IN-VaaniNeural",    "name": "Vaani (PA Female)"}],
}

# Fallback to English if language not found
DEFAULT_VOICES = LANG_VOICES["english"]

def get_voices_for_language(language: str):
    """Return voice list for a given language key, fallback to English."""
    return LANG_VOICES.get(language.lower(), DEFAULT_VOICES)

# Always resolve paths relative to this script's location
BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated_podcasts"
TEMP_DIR   = BASE_DIR / "temp_audio"
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

app = Flask(__name__, template_folder=str(BASE_DIR / 'templates'))

# ============================================================================
# SCRIPT GENERATION (OpenRouter AI)
# ============================================================================

def generate_podcast_script(content, title, ptype, audience, language="english"):
    """Generate podcast script using OpenRouter with model fallback."""
    try:
        LANG_INSTRUCTIONS = {
            "english":    "English — clear, professional, conversational.",
            "hinglish":   "Indian Hinglish — mix Hindi and English NATURALLY. Use: dekho, yaar, acha, toh, bilkul, haan, bhai. Start sentences in Hindi, add English words naturally.",
            "hindi":      "Pure Hindi — write entirely in Hindi (Devanagari script).",
            "urdu":       "Urdu — write in natural conversational Urdu.",
            "arabic":     "Arabic — Modern Standard Arabic, clear and engaging.",
            "spanish":    "Spanish — natural conversational Latin American Spanish.",
            "french":     "French — natural conversational French.",
            "german":     "German — professional yet conversational German.",
            "portuguese": "Brazilian Portuguese — warm, conversational.",
            "russian":    "Russian — clear, engaging Russian.",
            "chinese":    "Mandarin Chinese — clear, engaging Simplified Chinese.",
            "japanese":   "Japanese — polite, natural conversational Japanese.",
            "korean":     "Korean — natural, conversational Korean.",
            "italian":    "Italian — warm, expressive Italian.",
            "turkish":    "Turkish — natural, conversational Turkish.",
            "dutch":      "Dutch — clear, conversational Dutch.",
            "polish":     "Polish — natural, engaging Polish.",
            "swedish":    "Swedish — clear, conversational Swedish.",
            "indonesian": "Indonesian — natural Bahasa Indonesia.",
            "bengali":    "Bengali — natural, conversational Bengali.",
            "tamil":      "Tamil — natural, conversational Tamil.",
            "telugu":     "Telugu — natural, conversational Telugu.",
            "marathi":    "Marathi — natural, conversational Marathi.",
            "gujarati":   "Gujarati — natural, conversational Gujarati.",
            "kannada":    "Kannada — natural, conversational Kannada.",
            "malayalam":  "Malayalam — natural, conversational Malayalam.",
            "punjabi":    "Punjabi — natural, conversational Punjabi.",
            "vietnamese": "Vietnamese — natural, conversational Vietnamese.",
            "thai":       "Thai — natural, conversational Thai.",
            "swahili":    "Swahili — natural, conversational Swahili.",
            "persian":    "Persian (Farsi) — natural, conversational Persian.",
            "hebrew":     "Hebrew — natural, conversational Hebrew.",
            "greek":      "Greek — natural, conversational Greek.",
            "czech":      "Czech — natural, conversational Czech.",
            "romanian":   "Romanian — natural, conversational Romanian.",
            "hungarian":  "Hungarian — natural, conversational Hungarian.",
            "danish":     "Danish — natural, conversational Danish.",
            "finnish":    "Finnish — natural, conversational Finnish.",
            "norwegian":  "Norwegian — natural, conversational Norwegian.",
            "ukrainian":  "Ukrainian — natural, conversational Ukrainian.",
            "malay":      "Malay — natural, conversational Bahasa Melayu.",
            "filipino":   "Filipino/Tagalog — natural, conversational Filipino.",
            "afrikaans":  "Afrikaans — natural, conversational Afrikaans.",
            "catalan":    "Catalan — natural, conversational Catalan.",
            "croatian":   "Croatian — natural, conversational Croatian.",
            "slovak":     "Slovak — natural, conversational Slovak.",
            "bulgarian":  "Bulgarian — natural, conversational Bulgarian.",
            "lithuanian": "Lithuanian — natural, conversational Lithuanian.",
            "latvian":    "Latvian — natural, conversational Latvian.",
            "estonian":   "Estonian — natural, conversational Estonian.",
            "slovenian":  "Slovenian — natural, conversational Slovenian.",
            "albanian":   "Albanian — natural, conversational Albanian.",
            "macedonian": "Macedonian — natural, conversational Macedonian.",
            "georgian":   "Georgian — natural, conversational Georgian.",
            "armenian":   "Armenian — natural, conversational Armenian.",
            "azerbaijani":"Azerbaijani — natural, conversational Azerbaijani.",
            "kazakh":     "Kazakh — natural, conversational Kazakh.",
            "uzbek":      "Uzbek — natural, conversational Uzbek.",
            "mongolian":  "Mongolian — natural, conversational Mongolian.",
            "nepali":     "Nepali — natural, conversational Nepali.",
            "sinhala":    "Sinhala — natural, conversational Sinhala.",
            "khmer":      "Khmer — natural, conversational Khmer.",
            "lao":        "Lao — natural, conversational Lao.",
            "burmese":    "Burmese — natural, conversational Burmese.",
            "amharic":    "Amharic — natural, conversational Amharic.",
        }

        # Legacy audience override
        if audience == "indian" and language == "english":
            language = "hinglish"

        aud = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["english"])

        if ptype == "single":
            fmt = 'SINGLE HOST ONLY - Use ONLY "Host:" label.'
        elif ptype == "co-host":
            fmt = "TWO HOSTS - Alex and Sam in natural dialogue."
        else:
            fmt = "THREE HOSTS - Alex (moderator), Jordan (expert), Casey (curious)."

        prompt = (
            "Convert the following blog into an engaging podcast script.\n\n"
            f"LANGUAGE: {aud}\n"
            f"FORMAT: {fmt}\n\n"
            "STRUCTURE:\n"
            "1. INTRO (2-3 lines): Warm welcome, introduce topic\n"
            "2. MAIN DISCUSSION (12-16 lines): Cover key points naturally\n"
            "3. OUTRO (2-3 lines): Thank listeners, closing\n\n"
            "RULES:\n"
            "- NO stage directions, NO [music], NO *laughs*\n"
            "- ONLY speakable dialogue\n"
            "- 18-22 exchanges, 500-600 words\n"
            "- Each speaker on its own line as 'Speaker: text'\n\n"
            f"TOPIC: {title or 'Untitled'}\n\n"
            f"BLOG CONTENT:\n{content}\n\n"
            "Write ONLY the dialogue. Start now:"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional podcast script writer. "
                    "Create engaging, natural conversations. "
                    "NO stage directions, ONLY dialogue."
                )
            },
            {"role": "user", "content": prompt}
        ]

        response = None
        last_error = None
        used_model = None

        for model_id in FREE_MODELS:
            try:
                print(f"Trying model: {model_id}")
                response = openrouter_client.chat.completions.create(
                    model=model_id,
                    messages=messages
                )
                used_model = model_id
                print(f"Success with: {model_id}")
                break
            except Exception as e:
                last_error = e
                print(f"Model {model_id} failed: {e}")
                continue

        if response is None:
            return {"success": False, "error": f"All models failed. Last error: {last_error}"}

        script = response.choices[0].message.content

        # For non-English: keep Unicode, only strip stage directions
        is_english_based = language in ("english", "hinglish")
        if is_english_based:
            script = re.sub(r'[^\x00-\x7F]+', '', script)

        script = re.sub(r'\*[^*]+\*', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        script = script.replace('INTRO MUSIC', '').replace('OUTRO MUSIC', '')

        # Normalize speaker labels
        if ptype == "single":
            script = re.sub(r'(Alex|Sam|Jordan|Casey):', 'Host:', script)
        elif ptype == "co-host":
            script = script.replace('Host 1:', 'Alex:').replace('Host1:', 'Alex:')
            script = script.replace('Host 2:', 'Sam:').replace('Host2:', 'Sam:')
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

        # Keep only valid dialogue lines
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line and ':' in line and len(line) > 5:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 3:
                    lines.append(line)

        script = '\n\n'.join(lines).strip()
        return {"success": True, "script": script, "model": used_model}

    except Exception as e:
        return {"success": False, "error": str(e)}
        return {"success": False, "error": str(e)}

# ============================================================================
# AUDIO GENERATION (EdgeTTS)
# ============================================================================

def parse_script(script):
    """Parse script lines into list of {speaker, text} dicts."""
    dialogues = []
    for line in script.strip().split('\n'):
        line = line.strip()
        if ':' in line and len(line) > 5:
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip()
                dialogue = parts[1].strip()
                if dialogue:
                    dialogues.append({"speaker": speaker, "text": dialogue})
    return dialogues


def detect_speakers(dialogues, language="english"):
    """Assign a language-appropriate voice to each unique speaker."""
    speakers = sorted(set(d["speaker"] for d in dialogues))
    voices = get_voices_for_language(language)
    return {
        speaker: {
            "voice_info": voices[i % len(voices)]
        }
        for i, speaker in enumerate(speakers)
    }


def analyze_emotion(text):
    t = text.lower()
    if any(w in t for w in ['wow', 'amazing', 'incredible', 'awesome', 'zabardast', '!!']):
        return "excited"
    elif '?' in text or any(w in t for w in ['kya', 'really', 'how', 'why']):
        return "curious"
    elif any(w in t for w in ['important', 'must', 'critical', 'bilkul']):
        return "emphasis"
    elif any(w in t for w in ['think', 'believe', 'perhaps', 'maybe', 'shayad']):
        return "thoughtful"
    return "neutral"


def get_voice_params(emotion):
    return {
        "excited":    {"rate": "+15%", "pitch": "+5Hz"},
        "curious":    {"rate": "+5%",  "pitch": "+3Hz"},
        "emphasis":   {"rate": "+0%",  "pitch": "+2Hz"},
        "thoughtful": {"rate": "-10%", "pitch": "-2Hz"},
        "neutral":    {"rate": "+0%",  "pitch": "+0Hz"},
    }.get(emotion, {"rate": "+0%", "pitch": "+0Hz"})


async def _tts_async(text, voice, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(str(output_path))


def generate_audio_segment(speaker_voice, text, output_path):
    """Generate one audio segment using EdgeTTS."""
    voice_info = speaker_voice["voice_info"]
    emotion = analyze_emotion(text)
    params = get_voice_params(emotion)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_tts_async(
            text=text,
            voice=voice_info["voice"],
            rate=params["rate"],
            pitch=params["pitch"],
            output_path=output_path
        ))
    finally:
        loop.close()

    return output_path, emotion


def merge_audio_files(audio_files, output_file):
    """
    Professional merge:
      INTRO  → clip 2s–17s, normalize, fade-out last 3s
      SPEECH → all segments clean
      OUTRO  → clip 2:30–2:38, fade-in first 2s, normalize
    Falls back to simple concat if anything fails.
    """
    MUSIC_FILE = BASE_DIR / "nastelbom-podcast-intro-490161.mp3"

    try:
        from pydub import AudioSegment

        music = AudioSegment.from_mp3(str(MUSIC_FILE))

        # ── INTRO: 2s → 17s (15 seconds) ──
        intro = music[2000:17000]
        intro = intro.normalize() - 4          # normalize then pull down 4 dB
        intro = intro.fade_out(3000)           # fade out last 3 seconds

        # ── SPEECH: load and join all segments ──
        speech = AudioSegment.empty()
        for f in audio_files:
            if os.path.exists(f):
                speech += AudioSegment.from_mp3(str(f))

        if len(speech) == 0:
            raise ValueError("No speech segments")

        # ── OUTRO: 2:30 → 2:38 (8 seconds) ──
        outro = music[150000:158000]
        outro = outro.normalize() - 4          # match intro volume
        outro = outro.fade_in(2000)            # fade in over first 2 seconds
        outro = outro.fade_out(2000)           # fade out over last 2 seconds

        # ── ASSEMBLE ──
        # intro → 300ms silence → speech → 500ms silence → outro
        gap_start = AudioSegment.silent(duration=300)
        gap_end   = AudioSegment.silent(duration=500)

        final = intro + gap_start + speech + gap_end + outro

        final.export(str(output_file), format="mp3", bitrate="128k")
        print(f"[merge] intro({len(intro)/1000:.1f}s) + speech({len(speech)/1000:.1f}s) + outro({len(outro)/1000:.1f}s) = {len(final)/1000:.1f}s total")

    except Exception as e:
        print(f"[merge] pydub failed ({e}), simple concat fallback")
        with open(output_file, 'wb') as out:
            for f in audio_files:
                if os.path.exists(f):
                    with open(f, 'rb') as inp:
                        out.write(inp.read())

    return output_file

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ai-generate', methods=['POST'])
def ai_generate():
    """Generate podcast script via OpenRouter AI."""
    try:
        data = request.json
        content = data.get('content', '').strip()
        if not content:
            return jsonify({"success": False, "error": "No content provided"}), 400

        result = generate_podcast_script(
            content=content,
            title=data.get('title', ''),
            ptype=data.get('podcast_type', 'single'),
            audience=data.get('audience', 'global'),
            language=data.get('language', 'english')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_script():
    """Analyze script and return speaker/dialogue info."""
    try:
        data = request.json
        script = data.get('script', '')
        if not script:
            return jsonify({"error": "No script provided"}), 400

        dialogues = parse_script(script)
        if not dialogues:
            return jsonify({"error": "No valid dialogues found. Format: Speaker: Dialogue"}), 400

        speaker_voices = detect_speakers(dialogues)
        return jsonify({
            "success": True,
            "total_dialogues": len(dialogues),
            "speakers": len(speaker_voices),
            "speaker_info": {
                s: {"voice": info["voice_info"]["name"], "engine": "Microsoft EdgeTTS (FREE)"}
                for s, info in speaker_voices.items()
            },
            "dialogues": dialogues
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_podcast():
    """Generate podcast audio with EdgeTTS (parallel)."""
    try:
        data = request.json
        script = data.get('script', '')
        language = data.get('language', 'english')
        podcast_name = re.sub(
            r'[^\w\-_]', '_',
            data.get('name', f'podcast_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        )

        if not script:
            return jsonify({"error": "No script provided"}), 400

        dialogues = parse_script(script)
        if not dialogues:
            return jsonify({"error": "No valid dialogues found"}), 400

        speaker_voices = detect_speakers(dialogues, language)
        print(f"\nGenerating {len(dialogues)} segments, {len(speaker_voices)} speakers, language={language}...")

        tasks = [
            {
                "index": i,
                "speaker": d["speaker"],
                "text": d["text"],
                "output_path": TEMP_DIR / f"{podcast_name}_seg_{i:03d}_{d['speaker']}.mp3",
                "voice": speaker_voices[d["speaker"]]
            }
            for i, d in enumerate(dialogues)
        ]

        audio_files = [None] * len(tasks)
        progress_data = []

        def generate_segment(task):
            try:
                _, emotion = generate_audio_segment(task["voice"], task["text"], task["output_path"])
                if task["output_path"].exists():
                    return {
                        "success": True,
                        "index": task["index"],
                        "path": task["output_path"],
                        "speaker": task["speaker"],
                        "emotion": emotion,
                        "text": task["text"]
                    }
                return {"success": False, "index": task["index"], "error": "File not created"}
            except Exception as e:
                return {"success": False, "index": task["index"], "error": str(e)}

        with ThreadPoolExecutor(max_workers=min(len(tasks), 8)) as executor:
            futures = {executor.submit(generate_segment, t): t for t in tasks}
            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    idx = result["index"]
                    audio_files[idx] = result["path"]
                    text = result["text"]
                    progress_data.append({
                        "index": idx + 1,
                        "speaker": result["speaker"],
                        "emotion": result["emotion"],
                        "text": text[:60] + "..." if len(text) > 60 else text
                    })
                else:
                    return jsonify({
                        "error": f"Segment {result['index']+1} failed: {result.get('error','')}"
                    }), 500

        audio_files = [f for f in audio_files if f is not None]
        if not audio_files:
            return jsonify({"error": "No audio files generated"}), 500

        output_file = OUTPUT_DIR / f"{podcast_name}.mp3"
        merge_audio_files(audio_files, output_file)

        if not output_file.exists():
            return jsonify({"error": "Failed to create final file"}), 500

        # Cleanup temp segments
        for f in audio_files:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass

        file_size = output_file.stat().st_size / 1024 / 1024
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
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/stream/<filename>')
def stream_podcast(filename):
    """Stream audio with HTTP range support for browser seek."""
    try:
        file_path = OUTPUT_DIR / filename
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        file_size = file_path.stat().st_size
        range_header = request.headers.get('Range')

        if range_header:
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            byte_start = int(match.group(1)) if match else 0
            byte_end = int(match.group(2)) if match and match.group(2) else file_size - 1
            length = byte_end - byte_start + 1

            def stream_chunk():
                with open(file_path, 'rb') as f:
                    f.seek(byte_start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(8192, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            return Response(
                stream_chunk(), status=206, mimetype='audio/mpeg',
                headers={
                    'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(length),
                }
            )

        return send_file(file_path, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>')
def download_podcast(filename):
    """Download generated podcast as attachment."""
    try:
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/voices')
def get_voices():
    return jsonify({
        "voices": [
            {"key": k, "name": v["name"], "voice_id": v["voice"]}
            for k, v in VOICE_LIBRARY.items()
        ]
    })


@app.route('/api/fetch-url', methods=['POST'])
def fetch_url():
    """Scrape text content from a URL."""
    if not URL_SUPPORT:
        return jsonify({"success": False, "error": "requests/beautifulsoup4 not installed"}), 500
    try:
        url = request.json.get('url', '').strip()
        if not url:
            return jsonify({"success": False, "error": "No URL provided"}), 400
        if not url.startswith('http'):
            url = 'https://' + url

        headers = {"User-Agent": "Mozilla/5.0 (compatible; PodcastBot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove scripts, styles, nav, footer
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            tag.decompose()

        # Try to get article/main content first
        main = soup.find('article') or soup.find('main') or soup.find(id='content') or soup.find(class_='content') or soup.body
        text = main.get_text(separator='\n') if main else soup.get_text(separator='\n')

        # Clean up whitespace
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 40]
        content = '\n'.join(lines[:200])  # cap at ~200 lines

        title = soup.title.string.strip() if soup.title else ''

        if not content:
            return jsonify({"success": False, "error": "Could not extract text from this URL"}), 400

        return jsonify({"success": True, "content": content, "title": title})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Extract text from uploaded PDF."""
    if not PDF_SUPPORT:
        return jsonify({"success": False, "error": "PyPDF2 not installed"}), 500
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": "Only PDF files are supported"}), 400

        reader = PyPDF2.PdfReader(f)
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t.strip())

        content = '\n\n'.join(pages_text)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()

        if not content:
            return jsonify({"success": False, "error": "Could not extract text from PDF"}), 400

        title = f.filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        return jsonify({"success": True, "content": content[:8000], "title": title})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """Return list of generated podcasts."""
    try:
        files = sorted(OUTPUT_DIR.glob('*.mp3'), key=lambda f: f.stat().st_mtime, reverse=True)
        history = []
        for f in files:
            stat = f.stat()
            history.append({
                "filename": f.name,
                "size": f"{stat.st_size / 1024 / 1024:.2f} MB",
                "created": datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y, %I:%M %p")
            })
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# VIDEO ROUTES
# ============================================================================

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """Generate avatar podcast video using Wav2Lip + FFmpeg (local GPU only)."""
    if not VIDEO_ENABLED:
        return jsonify({
            "error": "Video generation requires a local GPU setup. Run the app locally with VIDEO_ENABLED=true to use this feature."
        }), 503

    try:
        data = request.json
        script = data.get('script', '')
        language = data.get('language', 'english')
        podcast_name = re.sub(
            r'[^\w\-_]', '_',
            data.get('name', f'podcast_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        )

        if not script:
            return jsonify({"error": "No script provided"}), 400

        dialogues = parse_script(script)
        if not dialogues:
            return jsonify({"error": "No valid dialogues found"}), 400

        speaker_voices = detect_speakers(dialogues, language)

        # Step 1: Generate all audio segments
        tasks = [
            {
                "index": i,
                "speaker": d["speaker"],
                "text": d["text"],
                "output_path": TEMP_DIR / f"vid_{podcast_name}_seg_{i:03d}_{d['speaker']}.mp3",
                "voice": speaker_voices[d["speaker"]]
            }
            for i, d in enumerate(dialogues)
        ]

        audio_files = [None] * len(tasks)

        def gen_seg(task):
            try:
                _, emotion = generate_audio_segment(task["voice"], task["text"], task["output_path"])
                if task["output_path"].exists():
                    return {"success": True, "index": task["index"], "path": task["output_path"],
                            "speaker": task["speaker"], "text": task["text"]}
                return {"success": False, "index": task["index"]}
            except Exception as e:
                return {"success": False, "index": task["index"], "error": str(e)}

        with ThreadPoolExecutor(max_workers=min(len(tasks), 6)) as executor:
            from concurrent.futures import as_completed
            futures = {executor.submit(gen_seg, t): t for t in tasks}
            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    audio_files[result["index"]] = result

        # Build dialogue list with audio paths for video engine
        video_dialogues = []
        for item in audio_files:
            if item and item.get("success"):
                video_dialogues.append({
                    "speaker": item["speaker"],
                    "text": item["text"],
                    "audio_path": str(item["path"])
                })

        if not video_dialogues:
            return jsonify({"error": "Audio generation failed for all segments"}), 500

        # Step 2: Generate video
        result = generate_podcast_video(
            dialogues=video_dialogues,
            podcast_name=podcast_name
        )

        # Cleanup audio segments
        for item in audio_files:
            if item and item.get("path"):
                try:
                    Path(item["path"]).unlink(missing_ok=True)
                except Exception:
                    pass

        if not result["success"]:
            return jsonify({"error": result.get("error", "Video generation failed")}), 500

        return jsonify({
            "success": True,
            "filename": result["filename"],
            "file_size": result["file_size"],
            "total_segments": len(video_dialogues),
            "speakers": len(speaker_voices)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/stream-video/<filename>')
def stream_video(filename):
    """Stream generated video with range support (local only)."""
    if not VIDEO_ENABLED:
        return jsonify({"error": "Video feature not available on this deployment"}), 503
    try:
        from pathlib import Path as P
        VIDEO_DIR = BASE_DIR / "generated_videos"
        file_path = VIDEO_DIR / filename
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        file_size = file_path.stat().st_size
        range_header = request.headers.get('Range')

        if range_header:
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            byte_start = int(match.group(1)) if match else 0
            byte_end = int(match.group(2)) if match and match.group(2) else file_size - 1
            length = byte_end - byte_start + 1

            def stream_chunk():
                with open(file_path, 'rb') as f:
                    f.seek(byte_start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(8192, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            return Response(stream_chunk(), status=206, mimetype='video/mp4',
                            headers={
                                'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                                'Accept-Ranges': 'bytes',
                                'Content-Length': str(length),
                            })

        return send_file(file_path, mimetype='video/mp4')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/download-video/<filename>')
def download_video(filename):
    """Download generated video (local only)."""
    if not VIDEO_ENABLED:
        return jsonify({"error": "Video feature not available on this deployment"}), 503
    try:
        VIDEO_DIR = BASE_DIR / "generated_videos"
        file_path = VIDEO_DIR / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/video-history')
def get_video_history():
    """Return list of generated videos (local only)."""
    if not VIDEO_ENABLED:
        return jsonify({"success": True, "history": []})
    try:
        VIDEO_DIR = BASE_DIR / "generated_videos"
        files = sorted(VIDEO_DIR.glob('*.mp4'), key=lambda f: f.stat().st_mtime, reverse=True)
        history = []
        for f in files:
            stat = f.stat()
            history.append({
                "filename": f.name,
                "size": f"{stat.st_size / 1024 / 1024:.1f} MB",
                "created": datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y, %I:%M %p")
            })
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print("\n" + "="*60)
    print("  INTERACTIVE PODCAST STUDIO")
    print("="*60)
    print(f"  Open: http://localhost:{port}")
    print("  AI Script : OpenRouter (free models, auto-fallback)")
    print("  Audio     : Microsoft EdgeTTS (free, unlimited)")
    print(f"  Video     : {'Enabled (local GPU)' if VIDEO_ENABLED else 'Disabled (cloud mode)'}")
    print("="*60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)