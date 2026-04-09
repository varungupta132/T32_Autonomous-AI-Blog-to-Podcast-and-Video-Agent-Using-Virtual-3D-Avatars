import os
import asyncio
import sys
from pathlib import Path
import urllib.request
import edge_tts

BGM_DIR = Path("bgm")
BGM_DIR.mkdir(exist_ok=True)
BGM_TRACKS = {
    "intro": "https://cdn.pixabay.com/download/audio/2022/10/25/audio_2e2a3c74eb.mp3",
    "soft": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
    "news": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_bb630cc098.mp3"
}

VOICE_LIBRARY = {
    "indian": [
        {"voice": "en-IN-PrabhatNeural", "name": "Prabhat (Indian Male)"},
        {"voice": "en-IN-NeerjaNeural", "name": "Neerja (Indian Female)"},
        {"voice": "hi-IN-MadhurNeural", "name": "Madhur (Hindi Male)"},
        {"voice": "hi-IN-SwaraNeural", "name": "Swara (Hindi Female)"}
    ],
    "global": [
        {"voice": "en-US-ChristopherNeural", "name": "Christopher (US Male)"},
        {"voice": "en-US-AriaNeural", "name": "Aria (US Female)"},
        {"voice": "en-US-GuyNeural", "name": "Guy (US Male)"},
        {"voice": "en-US-JennyNeural", "name": "Jenny (US Female)"}
    ],
    "telugu": [
        {"voice": "te-IN-MohanNeural", "name": "Mohan (Telugu Male)"},
        {"voice": "te-IN-ShrutiNeural", "name": "Shruti (Telugu Female)"}
    ],
    "french": [
        {"voice": "fr-FR-HenriNeural", "name": "Henri (French Male)"},
        {"voice": "fr-FR-DeniseNeural", "name": "Denise (French Female)"}
    ],
    "spanish": [
        {"voice": "es-ES-AlvaroNeural", "name": "Alvaro (Spanish Male)"},
        {"voice": "es-ES-ElviraNeural", "name": "Elvira (Spanish Female)"}
    ]
}

def ensure_bgm_exists():
    for name, url in BGM_TRACKS.items():
        file_path = BGM_DIR / f"{name}.mp3"
        if not file_path.exists():
            try:
                print(f"Downloading stock BGM track: {name}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
            except Exception as e:
                print(f"Failed to download {name} BGM: {e}")

ensure_bgm_exists()

def parse_script(script):
    dialogues = []
    lines = script.strip().split('\n')
    for line in lines:
        line = line.strip()
        if ':' in line and len(line) > 5:
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip()
                dialogue = parts[1].strip()
                if dialogue:
                    dialogues.append({"speaker": speaker, "text": dialogue})
    return dialogues

def detect_speakers(dialogues, language="global"):
    speakers = list(set([d["speaker"] for d in dialogues]))
    speakers.sort()
    voices = VOICE_LIBRARY.get(language, VOICE_LIBRARY["global"])
    speaker_voices = {}
    for i, speaker in enumerate(speakers):
        voice_info = voices[i % len(voices)]
        speaker_voices[speaker] = {
            "voice_key": voice_info["voice"],
            "voice_info": {**voice_info, "rate": "+0%", "pitch": "+0Hz"}
        }
    return speaker_voices

def analyze_emotion(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ['wow', 'amazing', 'incredible', 'awesome', 'fantastic', 'zabardast', 'kya baat']):
        return "excited"
    elif '?' in text or any(word in text_lower for word in ['kya', 'really', 'sach', 'how', 'why']):
        return "curious"
    elif any(word in text_lower for word in ['important', 'must', 'critical', 'zaruri', 'bilkul']):
        return "emphasis"
    elif any(word in text_lower for word in ['think', 'believe', 'perhaps', 'maybe', 'shayad']):
        return "thoughtful"
    return "neutral"

def get_voice_params(emotion):
    params = {
        "excited": {"rate": "+15%", "pitch": "+5Hz"},
        "curious": {"rate": "+5%", "pitch": "+3Hz"},
        "emphasis": {"rate": "+0%", "pitch": "+2Hz"},
        "thoughtful": {"rate": "-10%", "pitch": "-2Hz"},
        "calm": {"rate": "-5%", "pitch": "-5Hz"},
        "serious": {"rate": "-10%", "pitch": "-5Hz"},
        "neutral": {"rate": "+0%", "pitch": "+0Hz"}
    }
    return params.get(emotion, params["neutral"])

async def generate_audio_async(text, voice, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(str(output_path))

def generate_audio_segment(speaker_voice, text, output_path, emotion_override="auto"):
    try:
        voice_info = speaker_voice["voice_info"]
        if emotion_override and emotion_override != "auto":
            emotion = emotion_override
        else:
            emotion = analyze_emotion(text)
        params = get_voice_params(emotion)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(generate_audio_async(text=text, voice=voice_info["voice"], rate=params["rate"], pitch=params["pitch"], output_path=output_path))
        finally:
            loop.close()
        return output_path, emotion
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        raise

def merge_audio_files(audio_files, output_file, bg_music=None):
    try:
        from pydub import AudioSegment
        import imageio_ffmpeg
        AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()
        
        combined_speech = AudioSegment.empty()
        for mp3_file in audio_files:
            if os.path.exists(mp3_file):
                segment = AudioSegment.from_mp3(mp3_file)
                combined_speech += segment
                
        if bg_music and bg_music in BGM_TRACKS:
            bgm_path = BGM_DIR / f"{bg_music}.mp3"
            if bgm_path.exists():
                print(f"🎧 Mixing background music: {bg_music}...")
                bgm = AudioSegment.from_mp3(bgm_path)
                while len(bgm) < len(combined_speech):
                    bgm += bgm
                bgm = bgm[:len(combined_speech)]
                bgm = bgm - 18 
                combined_speech = combined_speech.overlay(bgm)
                
        combined_speech.export(output_file, format="mp3")
        return output_file
        
    except Exception as e:
        print(f"✗ Pydub mixing failed: {e}. Falling back to byte concatenation.")
        with open(output_file, 'wb') as outfile:
            for mp3_file in audio_files:
                if os.path.exists(mp3_file):
                    with open(mp3_file, 'rb') as infile:
                        outfile.write(infile.read())
        return output_file
