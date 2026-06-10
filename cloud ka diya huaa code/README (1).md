# 🎙️ Podcast Studio Pro — Ultimate Edition

> AI-powered blog-to-podcast converter with natural voices, Hinglish support, and emotion-aware audio.

---

## ✨ Features

| Feature | Details |
|---|---|
| **AI Script Generation** | OpenRouter (Gemini Flash) converts blogs → podcast scripts |
| **Natural Voices** | Microsoft EdgeTTS — FREE, unlimited, CPU-only |
| **Multi-language** | Hinglish, Hindi, Telugu, French, Spanish, English |
| **Smart Voice Assignment** | Each speaker gets a unique voice (alternating M/F) |
| **Emotion Detection** | Excited / Curious / Emphasis / Thoughtful / Neutral |
| **Parallel Generation** | Up to 8 threads — 5-10x faster than sequential |
| **1/2/3 Host Modes** | Solo, Co-Host, Panel |
| **Stream + Download** | Inline player + MP3 download |

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open in browser
http://localhost:8080
```

---

## 🔧 How It Works

```
Blog Content
    │
    ▼
[Step 1] Configure
    • Podcast type (Solo / Co-Host / Panel)
    • Language (Hinglish / Hindi / English / Telugu / French / Spanish)
    • Paste blog content
    │
    ▼
[Step 2] Script
    • AI generates natural dialogue via OpenRouter
    • OR write/paste your own script
    • Preview speaker → voice assignments
    │
    ▼
[Step 3] Generate
    • EdgeTTS converts each line to audio (parallel)
    • Emotion detected per line → voice speed/pitch adjusted
    • All segments merged into one MP3
    │
    ▼
[Step 4] Listen & Download
    • Inline audio player
    • One-click MP3 download
```

---

## 📝 Script Format

```
Host: Welcome to the show everyone!
Alex: Today we're diving into the world of AI.
Sam: Yaar, ye topic bahut interesting hai!
Alex: Bilkul! Let's start from the basics.
```

Each line: `SpeakerName: Dialogue text`

---

## 🎤 Available Voices

### Indian / Hinglish
- Prabhat — Indian Male (en-IN)
- Neerja — Indian Female (en-IN)
- Madhur — Hindi Male (hi-IN)
- Swara — Hindi Female (hi-IN)

### English (Global)
- Christopher, Guy — US Male
- Aria, Jenny — US Female

### Other Languages
- Telugu: Mohan (M), Shruti (F)
- French: Henri (M), Denise (F)
- Spanish: Alvaro (M), Elvira (F)

---

## ⚙️ Configuration

Edit `app.py` to change:
- `OPENROUTER_API_KEY` — your API key
- `OPENROUTER_MODEL` — AI model to use
- `VOICE_LIBRARY` — add/remove voices
- `OUTPUT_DIR` / `TEMP_DIR` — file paths

---

## 📁 Project Structure

```
podcast_studio/
├── app.py                  ← Flask backend (main file)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
├── templates/
│   └── index.html          ← Frontend UI
├── generated_podcasts/     ← Final MP3 files (auto-created)
└── temp_audio/             ← Temporary segments (auto-cleaned)
```
