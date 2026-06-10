import re, os, json, time, asyncio, queue, threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, jsonify, send_file, Response
import edge_tts
from openai import OpenAI

try:
    import fitz
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import docx as docxlib
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import wikipedia
    WIKI_SUPPORT = True
except ImportError:
    WIKI_SUPPORT = False

OPENROUTER_API_KEY = chr(34)+KEY+chr(34)
openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
FREE_MODELS = ["nvidia/nemotron-3-nano-30b-a3b:free"]
LANGUAGE_VOICES = {
    "english": [
        {"voice": "en-US-GuyNeural",   "name": "Guy (US Male)"},
        {"voice": "en-US-JennyNeural", "name": "Jenny (US Female)"},
        {"voice": "en-GB-RyanNeural",  "name": "Ryan (UK Male)"},
        {"voice": "en-GB-SoniaNeural", "name": "Sonia (UK Female)"},
    ],
    "hinglish": [
        {"voice": "en-IN-PrabhatNeural", "name": "Prabhat (Indian Male)"},
        {"voice": "en-IN-NeerjaNeural",  "name": "Neerja (Indian Female)"},
        {"voice": "hi-IN-MadhurNeural",  "name": "Madhur (Hindi Male)"},
        {"voice": "hi-IN-SwaraNeural",   "name": "Swara (Hindi Female)"},
    ],
    "hindi": [
        {"voice": "hi-IN-MadhurNeural", "name": "Madhur (Hindi Male)"},
        {"voice": "hi-IN-SwaraNeural",  "name": "Swara (Hindi Female)"},
        {"voice": "hi-IN-MadhurNeural", "name": "Madhur (Hindi Male)"},
        {"voice": "hi-IN-SwaraNeural",  "name": "Swara (Hindi Female)"},
    ],
    "spanish": [{"voice": "es-ES-AlvaroNeural","name": "Alvaro (Spain Male)"},{"voice": "es-ES-ElviraNeural","name": "Elvira (Spain Female)"},{"voice": "es-MX-JorgeNeural","name": "Jorge (Mexico Male)"},{"voice": "es-MX-DaliaNeural","name": "Dalia (Mexico Female)"}],
    "french":  [{"voice": "fr-FR-HenriNeural","name": "Henri (France Male)"},{"voice": "fr-FR-DeniseNeural","name": "Denise (France Female)"},{"voice": "fr-CA-ThierryNeural","name": "Thierry (Canada Male)"},{"voice": "fr-CA-SylvieNeural","name": "Sylvie (Canada Female)"}],
    "german":  [{"voice": "de-DE-FlorianMultilingualNeural","name": "Florian (Germany Male)"},{"voice": "de-DE-SeraphinaMultilingualNeural","name": "Seraphina (Germany Female)"},{"voice": "de-AT-JonasNeural","name": "Jonas (Austria Male)"},{"voice": "de-AT-IngridNeural","name": "Ingrid (Austria Female)"}],
    "japanese":[{"voice": "ja-JP-KeitaNeural","name": "Keita (Japan Male)"},{"voice": "ja-JP-NanamiNeural","name": "Nanami (Japan Female)"},{"voice": "ja-JP-KeitaNeural","name": "Keita (Japan Male)"},{"voice": "ja-JP-NanamiNeural","name": "Nanami (Japan Female)"}],
    "arabic":  [{"voice": "ar-SA-HamedNeural","name": "Hamed (Saudi Male)"},{"voice": "ar-SA-ZariyahNeural","name": "Zariyah (Saudi Female)"},{"voice": "ar-EG-ShakirNeural","name": "Shakir (Egypt Male)"},{"voice": "ar-EG-SalmaNeural","name": "Salma (Egypt Female)"}],
    "chinese": [{"voice": "zh-CN-YunjianNeural","name": "Yunjian (China Male)"},{"voice": "zh-CN-XiaoxiaoNeural","name": "Xiaoxiao (China Female)"},{"voice": "zh-TW-YunJheNeural","name": "YunJhe (Taiwan Male)"},{"voice": "zh-TW-HsiaoChenNeural","name": "HsiaoChen (Taiwan Female)"}],
    "portuguese":[{"voice": "pt-BR-AntonioNeural","name": "Antonio (Brazil Male)"},{"voice": "pt-BR-ThalitaMultilingualNeural","name": "Thalita (Brazil Female)"},{"voice": "pt-PT-DuarteNeural","name": "Duarte (Portugal Male)"},{"voice": "pt-PT-RaquelNeural","name": "Raquel (Portugal Female)"}],
    "russian": [{"voice": "ru-RU-DmitryNeural","name": "Dmitry (Russia Male)"},{"voice": "ru-RU-SvetlanaNeural","name": "Svetlana (Russia Female)"},{"voice": "ru-RU-DmitryNeural","name": "Dmitry (Russia Male)"},{"voice": "ru-RU-SvetlanaNeural","name": "Svetlana (Russia Female)"}],
    "korean":  [{"voice": "ko-KR-InJoonNeural","name": "InJoon (Korea Male)"},{"voice": "ko-KR-SunHiNeural","name": "SunHi (Korea Female)"},{"voice": "ko-KR-HyunsuMultilingualNeural","name": "Hyunsu (Korea Male)"},{"voice": "ko-KR-SunHiNeural","name": "SunHi (Korea Female)"}],
    "italian": [{"voice": "it-IT-GiuseppeMultilingualNeural","name": "Giuseppe (Italy Male)"},{"voice": "it-IT-ElsaNeural","name": "Elsa (Italy Female)"},{"voice": "it-IT-DiegoNeural","name": "Diego (Italy Male)"},{"voice": "it-IT-IsabellaNeural","name": "Isabella (Italy Female)"}],
    "turkish": [{"voice": "tr-TR-AhmetNeural","name": "Ahmet (Turkey Male)"},{"voice": "tr-TR-EmelNeural","name": "Emel (Turkey Female)"},{"voice": "tr-TR-AhmetNeural","name": "Ahmet (Turkey Male)"},{"voice": "tr-TR-EmelNeural","name": "Emel (Turkey Female)"}],
    "dutch":   [{"voice": "nl-NL-MaartenNeural","name": "Maarten (Netherlands Male)"},{"voice": "nl-NL-ColetteNeural","name": "Colette (Netherlands Female)"},{"voice": "nl-BE-ArnaudNeural","name": "Arnaud (Belgium Male)"},{"voice": "nl-BE-DenaNeural","name": "Dena (Belgium Female)"}],
    "polish":  [{"voice": "pl-PL-MarekNeural","name": "Marek (Poland Male)"},{"voice": "pl-PL-ZofiaNeural","name": "Zofia (Poland Female)"},{"voice": "pl-PL-MarekNeural","name": "Marek (Poland Male)"},{"voice": "pl-PL-ZofiaNeural","name": "Zofia (Poland Female)"}],
    "swedish": [{"voice": "sv-SE-MattiasNeural","name": "Mattias (Sweden Male)"},{"voice": "sv-SE-SofieNeural","name": "Sofie (Sweden Female)"},{"voice": "sv-SE-MattiasNeural","name": "Mattias (Sweden Male)"},{"voice": "sv-SE-SofieNeural","name": "Sofie (Sweden Female)"}],
    "indonesian":[{"voice": "id-ID-ArdiNeural","name": "Ardi (Indonesia Male)"},{"voice": "id-ID-GadisNeural","name": "Gadis (Indonesia Female)"},{"voice": "id-ID-ArdiNeural","name": "Ardi (Indonesia Male)"},{"voice": "id-ID-GadisNeural","name": "Gadis (Indonesia Female)"}],
    "tamil":   [{"voice": "ta-IN-ValluvarNeural","name": "Valluvar (Tamil Male)"},{"voice": "ta-IN-PallaviNeural","name": "Pallavi (Tamil Female)"},{"voice": "ta-MY-SuryaNeural","name": "Surya (Malaysia Male)"},{"voice": "ta-MY-KaniNeural","name": "Kani (Malaysia Female)"}],
    "bengali": [{"voice": "bn-IN-BashkarNeural","name": "Bashkar (India Male)"},{"voice": "bn-IN-TanishaaNeural","name": "Tanishaa (India Female)"},{"voice": "bn-BD-PradeepNeural","name": "Pradeep (Bangladesh Male)"},{"voice": "bn-BD-NabanitaNeural","name": "Nabanita (Bangladesh Female)"}],
    "urdu":    [{"voice": "ur-PK-AsadNeural","name": "Asad (Pakistan Male)"},{"voice": "ur-PK-UzmaNeural","name": "Uzma (Pakistan Female)"},{"voice": "ur-IN-SalmanNeural","name": "Salman (India Male)"},{"voice": "ur-IN-GulNeural","name": "Gul (India Female)"}],
    "telugu":  [{"voice": "te-IN-MohanNeural","name": "Mohan (Telugu Male)"},{"voice": "te-IN-ShrutiNeural","name": "Shruti (Telugu Female)"},{"voice": "te-IN-MohanNeural","name": "Mohan (Telugu Male)"},{"voice": "te-IN-ShrutiNeural","name": "Shruti (Telugu Female)"}],
    "marathi": [{"voice": "mr-IN-ManoharNeural","name": "Manohar (Marathi Male)"},{"voice": "mr-IN-AarohiNeural","name": "Aarohi (Marathi Female)"},{"voice": "mr-IN-ManoharNeural","name": "Manohar (Marathi Male)"},{"voice": "mr-IN-AarohiNeural","name": "Aarohi (Marathi Female)"}],
    "gujarati":[{"voice": "gu-IN-NiranjanNeural","name": "Niranjan (Gujarati Male)"},{"voice": "gu-IN-DhwaniNeural","name": "Dhwani (Gujarati Female)"},{"voice": "gu-IN-NiranjanNeural","name": "Niranjan (Gujarati Male)"},{"voice": "gu-IN-DhwaniNeural","name": "Dhwani (Gujarati Female)"}],
    "kannada": [{"voice": "kn-IN-GaganNeural","name": "Gagan (Kannada Male)"},{"voice": "kn-IN-SapnaNeural","name": "Sapna (Kannada Female)"},{"voice": "kn-IN-GaganNeural","name": "Gagan (Kannada Male)"},{"voice": "kn-IN-SapnaNeural","name": "Sapna (Kannada Female)"}],
    "malayalam":[{"voice": "ml-IN-MidhunNeural","name": "Midhun (Malayalam Male)"},{"voice": "ml-IN-SobhanaNeural","name": "Sobhana (Malayalam Female)"},{"voice": "ml-IN-MidhunNeural","name": "Midhun (Malayalam Male)"},{"voice": "ml-IN-SobhanaNeural","name": "Sobhana (Malayalam Female)"}],
    "nepali":  [{"voice": "ne-NP-SagarNeural","name": "Sagar (Nepali Male)"},{"voice": "ne-NP-HemkalaNeural","name": "Hemkala (Nepali Female)"},{"voice": "ne-NP-SagarNeural","name": "Sagar (Nepali Male)"},{"voice": "ne-NP-HemkalaNeural","name": "Hemkala (Nepali Female)"}],
    "sinhala": [{"voice": "si-LK-SameeraNeural","name": "Sameera (Sinhala Male)"},{"voice": "si-LK-ThiliniNeural","name": "Thilini (Sinhala Female)"},{"voice": "si-LK-SameeraNeural","name": "Sameera (Sinhala Male)"},{"voice": "si-LK-ThiliniNeural","name": "Thilini (Sinhala Female)"}],
    "malay":   [{"voice": "ms-MY-OsmanNeural","name": "Osman (Malay Male)"},{"voice": "ms-MY-YasminNeural","name": "Yasmin (Malay Female)"},{"voice": "ms-MY-OsmanNeural","name": "Osman (Malay Male)"},{"voice": "ms-MY-YasminNeural","name": "Yasmin (Malay Female)"}],
    "vietnamese":[{"voice": "vi-VN-NamMinhNeural","name": "NamMinh (Vietnamese Male)"},{"voice": "vi-VN-HoaiMyNeural","name": "HoaiMy (Vietnamese Female)"},{"voice": "vi-VN-NamMinhNeural","name": "NamMinh (Vietnamese Male)"},{"voice": "vi-VN-HoaiMyNeural","name": "HoaiMy (Vietnamese Female)"}],
    "thai":    [{"voice": "th-TH-NiwatNeural","name": "Niwat (Thai Male)"},{"voice": "th-TH-PremwadeeNeural","name": "Premwadee (Thai Female)"},{"voice": "th-TH-NiwatNeural","name": "Niwat (Thai Male)"},{"voice": "th-TH-PremwadeeNeural","name": "Premwadee (Thai Female)"}],
    "filipino":[{"voice": "fil-PH-AngeloNeural","name": "Angelo (Filipino Male)"},{"voice": "fil-PH-BlessicaNeural","name": "Blessica (Filipino Female)"},{"voice": "fil-PH-AngeloNeural","name": "Angelo (Filipino Male)"},{"voice": "fil-PH-BlessicaNeural","name": "Blessica (Filipino Female)"}],
    "greek":   [{"voice": "el-GR-NestorasNeural","name": "Nestoras (Greek Male)"},{"voice": "el-GR-AthinaNeural","name": "Athina (Greek Female)"},{"voice": "el-GR-NestorasNeural","name": "Nestoras (Greek Male)"},{"voice": "el-GR-AthinaNeural","name": "Athina (Greek Female)"}],
    "czech":   [{"voice": "cs-CZ-AntoninNeural","name": "Antonin (Czech Male)"},{"voice": "cs-CZ-VlastaNeural","name": "Vlasta (Czech Female)"},{"voice": "cs-CZ-AntoninNeural","name": "Antonin (Czech Male)"},{"voice": "cs-CZ-VlastaNeural","name": "Vlasta (Czech Female)"}],
    "romanian":[{"voice": "ro-RO-EmilNeural","name": "Emil (Romanian Male)"},{"voice": "ro-RO-AlinaNeural","name": "Alina (Romanian Female)"},{"voice": "ro-RO-EmilNeural","name": "Emil (Romanian Male)"},{"voice": "ro-RO-AlinaNeural","name": "Alina (Romanian Female)"}],
    "hungarian":[{"voice": "hu-HU-TamasNeural","name": "Tamas (Hungarian Male)"},{"voice": "hu-HU-NoemiNeural","name": "Noemi (Hungarian Female)"},{"voice": "hu-HU-TamasNeural","name": "Tamas (Hungarian Male)"},{"voice": "hu-HU-NoemiNeural","name": "Noemi (Hungarian Female)"}],
    "danish":  [{"voice": "da-DK-JeppeNeural","name": "Jeppe (Danish Male)"},{"voice": "da-DK-ChristelNeural","name": "Christel (Danish Female)"},{"voice": "da-DK-JeppeNeural","name": "Jeppe (Danish Male)"},{"voice": "da-DK-ChristelNeural","name": "Christel (Danish Female)"}],
    "finnish": [{"voice": "fi-FI-HarriNeural","name": "Harri (Finnish Male)"},{"voice": "fi-FI-NooraNeural","name": "Noora (Finnish Female)"},{"voice": "fi-FI-HarriNeural","name": "Harri (Finnish Male)"},{"voice": "fi-FI-NooraNeural","name": "Noora (Finnish Female)"}],
    "norwegian":[{"voice": "nb-NO-FinnNeural","name": "Finn (Norwegian Male)"},{"voice": "nb-NO-PernilleNeural","name": "Pernille (Norwegian Female)"},{"voice": "nb-NO-FinnNeural","name": "Finn (Norwegian Male)"},{"voice": "nb-NO-PernilleNeural","name": "Pernille (Norwegian Female)"}],
    "ukrainian":[{"voice": "uk-UA-OstapNeural","name": "Ostap (Ukrainian Male)"},{"voice": "uk-UA-PolinaNeural","name": "Polina (Ukrainian Female)"},{"voice": "uk-UA-OstapNeural","name": "Ostap (Ukrainian Male)"},{"voice": "uk-UA-PolinaNeural","name": "Polina (Ukrainian Female)"}],
    "persian": [{"voice": "fa-IR-FaridNeural","name": "Farid (Persian Male)"},{"voice": "fa-IR-DilaraNeural","name": "Dilara (Persian Female)"},{"voice": "fa-IR-FaridNeural","name": "Farid (Persian Male)"},{"voice": "fa-IR-DilaraNeural","name": "Dilara (Persian Female)"}],
    "hebrew":  [{"voice": "he-IL-AvriNeural","name": "Avri (Hebrew Male)"},{"voice": "he-IL-HilaNeural","name": "Hila (Hebrew Female)"},{"voice": "he-IL-AvriNeural","name": "Avri (Hebrew Male)"},{"voice": "he-IL-HilaNeural","name": "Hila (Hebrew Female)"}],
    "swahili": [{"voice": "sw-KE-RafikiNeural","name": "Rafiki (Swahili Male)"},{"voice": "sw-KE-ZuriNeural","name": "Zuri (Swahili Female)"},{"voice": "sw-KE-RafikiNeural","name": "Rafiki (Swahili Male)"},{"voice": "sw-KE-ZuriNeural","name": "Zuri (Swahili Female)"}],
    "amharic": [{"voice": "am-ET-AmehaNeural","name": "Ameha (Amharic Male)"},{"voice": "am-ET-MekdesNeural","name": "Mekdes (Amharic Female)"},{"voice": "am-ET-AmehaNeural","name": "Ameha (Amharic Male)"},{"voice": "am-ET-MekdesNeural","name": "Mekdes (Amharic Female)"}],
    "zulu":    [{"voice": "zu-ZA-ThembaNeural","name": "Themba (Zulu Male)"},{"voice": "zu-ZA-ThandoNeural","name": "Thando (Zulu Female)"},{"voice": "zu-ZA-ThembaNeural","name": "Themba (Zulu Male)"},{"voice": "zu-ZA-ThandoNeural","name": "Thando (Zulu Female)"}],
    "afrikaans":[{"voice": "af-ZA-WillemNeural","name": "Willem (Afrikaans Male)"},{"voice": "af-ZA-AdriNeural","name": "Adri (Afrikaans Female)"},{"voice": "af-ZA-WillemNeural","name": "Willem (Afrikaans Male)"},{"voice": "af-ZA-AdriNeural","name": "Adri (Afrikaans Female)"}],
    "azerbaijani":[{"voice": "az-AZ-BabekNeural","name": "Babek (Azerbaijani Male)"},{"voice": "az-AZ-BanuNeural","name": "Banu (Azerbaijani Female)"},{"voice": "az-AZ-BabekNeural","name": "Babek (Azerbaijani Male)"},{"voice": "az-AZ-BanuNeural","name": "Banu (Azerbaijani Female)"}],
    "kazakh":  [{"voice": "kk-KZ-DauletNeural","name": "Daulet (Kazakh Male)"},{"voice": "kk-KZ-AigulNeural","name": "Aigul (Kazakh Female)"},{"voice": "kk-KZ-DauletNeural","name": "Daulet (Kazakh Male)"},{"voice": "kk-KZ-AigulNeural","name": "Aigul (Kazakh Female)"}],
    "uzbek":   [{"voice": "uz-UZ-SardorNeural","name": "Sardor (Uzbek Male)"},{"voice": "uz-UZ-MadinaNeural","name": "Madina (Uzbek Female)"},{"voice": "uz-UZ-SardorNeural","name": "Sardor (Uzbek Male)"},{"voice": "uz-UZ-MadinaNeural","name": "Madina (Uzbek Female)"}],
    "mongolian":[{"voice": "mn-MN-BataaNeural","name": "Bataa (Mongolian Male)"},{"voice": "mn-MN-YesuiNeural","name": "Yesui (Mongolian Female)"},{"voice": "mn-MN-BataaNeural","name": "Bataa (Mongolian Male)"},{"voice": "mn-MN-YesuiNeural","name": "Yesui (Mongolian Female)"}],
    "burmese": [{"voice": "my-MM-ThihaNeural","name": "Thiha (Burmese Male)"},{"voice": "my-MM-NilarNeural","name": "Nilar (Burmese Female)"},{"voice": "my-MM-ThihaNeural","name": "Thiha (Burmese Male)"},{"voice": "my-MM-NilarNeural","name": "Nilar (Burmese Female)"}],
    "khmer":   [{"voice": "km-KH-PisethNeural","name": "Piseth (Khmer Male)"},{"voice": "km-KH-SreymomNeural","name": "Sreymom (Khmer Female)"},{"voice": "km-KH-PisethNeural","name": "Piseth (Khmer Male)"},{"voice": "km-KH-SreymomNeural","name": "Sreymom (Khmer Female)"}],
    "lao":     [{"voice": "lo-LA-ChanthavongNeural","name": "Chanthavong (Lao Male)"},{"voice": "lo-LA-KeomanyNeural","name": "Keomany (Lao Female)"},{"voice": "lo-LA-ChanthavongNeural","name": "Chanthavong (Lao Male)"},{"voice": "lo-LA-KeomanyNeural","name": "Keomany (Lao Female)"}],
    "catalan": [{"voice": "ca-ES-EnricNeural","name": "Enric (Catalan Male)"},{"voice": "ca-ES-JoanaNeural","name": "Joana (Catalan Female)"},{"voice": "ca-ES-EnricNeural","name": "Enric (Catalan Male)"},{"voice": "ca-ES-JoanaNeural","name": "Joana (Catalan Female)"}],
    "slovak":  [{"voice": "sk-SK-LukasNeural","name": "Lukas (Slovak Male)"},{"voice": "sk-SK-ViktoriaNeural","name": "Viktoria (Slovak Female)"},{"voice": "sk-SK-LukasNeural","name": "Lukas (Slovak Male)"},{"voice": "sk-SK-ViktoriaNeural","name": "Viktoria (Slovak Female)"}],
    "croatian":[{"voice": "hr-HR-SreckoNeural","name": "Srecko (Croatian Male)"},{"voice": "hr-HR-GabrijelaNeural","name": "Gabrijela (Croatian Female)"},{"voice": "hr-HR-SreckoNeural","name": "Srecko (Croatian Male)"},{"voice": "hr-HR-GabrijelaNeural","name": "Gabrijela (Croatian Female)"}],
    "bulgarian":[{"voice": "bg-BG-BorislavNeural","name": "Borislav (Bulgarian Male)"},{"voice": "bg-BG-KalinaNeural","name": "Kalina (Bulgarian Female)"},{"voice": "bg-BG-BorislavNeural","name": "Borislav (Bulgarian Male)"},{"voice": "bg-BG-KalinaNeural","name": "Kalina (Bulgarian Female)"}],
    "somali":  [{"voice": "so-SO-MuuseNeural","name": "Muuse (Somali Male)"},{"voice": "so-SO-UbaxNeural","name": "Ubax (Somali Female)"},{"voice": "so-SO-MuuseNeural","name": "Muuse (Somali Male)"},{"voice": "so-SO-UbaxNeural","name": "Ubax (Somali Female)"}],
    "galician":[{"voice": "gl-ES-RoiNeural","name": "Roi (Galician Male)"},{"voice": "gl-ES-SabelaNeural","name": "Sabela (Galician Female)"},{"voice": "gl-ES-RoiNeural","name": "Roi (Galician Male)"},{"voice": "gl-ES-SabelaNeural","name": "Sabela (Galician Female)"}],
    "welsh":   [{"voice": "cy-GB-AledNeural","name": "Aled (Welsh Male)"},{"voice": "cy-GB-NiaNeural","name": "Nia (Welsh Female)"},{"voice": "cy-GB-AledNeural","name": "Aled (Welsh Male)"},{"voice": "cy-GB-NiaNeural","name": "Nia (Welsh Female)"}],
    "irish":   [{"voice": "ga-IE-ColmNeural","name": "Colm (Irish Male)"},{"voice": "ga-IE-OrlaNeural","name": "Orla (Irish Female)"},{"voice": "ga-IE-ColmNeural","name": "Colm (Irish Male)"},{"voice": "ga-IE-OrlaNeural","name": "Orla (Irish Female)"}],
    "javanese":[{"voice": "jv-ID-DimasNeural","name": "Dimas (Javanese Male)"},{"voice": "jv-ID-SitiNeural","name": "Siti (Javanese Female)"},{"voice": "jv-ID-DimasNeural","name": "Dimas (Javanese Male)"},{"voice": "jv-ID-SitiNeural","name": "Siti (Javanese Female)"}],
}

NON_LATIN = {
    "hindi","japanese","arabic","chinese","russian","korean","tamil","bengali","urdu",
    "telugu","marathi","gujarati","kannada","malayalam","nepali","sinhala","thai",
    "amharic","persian","hebrew","burmese","khmer","lao","mongolian","ukrainian","bulgarian",
}

OUTPUT_DIR = Path("generated_podcasts")
TEMP_DIR   = Path("temp_audio")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
HISTORY_FILE = OUTPUT_DIR / "history.json"

app = Flask(__name__)
progress_queues = {}

