# 🎙️ AI Blog-to-Podcast Agent with Virtual 3D Avatar Integration

A full-stack application that converts blog posts into professional podcast audio with support for multiple speakers and avatar-ready output format.

---

## ✨ Features

- 🎤 **Single Host** - One person podcast
- 👥 **Co-Host** - Two people dialogue
- 🎭 **Multi-Host** - Three people panel
- 🌐 **Global** - English audience
- 🇮🇳 **Indian** - Hinglish audience
- ♾️ **Unlimited** - No API limits!
- 🎵 **Audio Generation** - Convert scripts to audio
- 🎥 **3D Avatar** - Video podcast integration (In Progress)

## 🚀 Quick Start

### 1. Install Ollama

Download from: https://ollama.com/download

### 2. Install Python Packages

```bash
pip install ollama flask gtts pydub
```

### 3. Run Web App

```bash
python web_podcast_ollama.py
```

Open: http://localhost:5000

## 📁 Files

- **web_podcast_ollama.py** - Web interface (Recommended)
- **podcast_generator_ollama.py** - Command line interface
- **podcast_to_voice.py** - Audio converter
- **PROGRESS.md** - Project progress report

## 💡 Usage

### Web Interface (Easy)

1. Run: `python web_podcast_ollama.py`
2. Open: http://localhost:5000
3. Paste your blog
4. Choose type & audience
5. Generate!

### Command Line

```bash
python podcast_generator_ollama.py
```

### Audio Generation

```bash
python podcast_to_voice.py
```

## 🦙 Available Models

Your system has:
- **llama2** (3.8GB) - Good quality ⭐
- **mistral** (4.4GB) - Better quality
- **gemma3:1b** (815MB) - Fast

## 📊 Example Output

### Global:
```
Alex: Welcome to the show!
Sam: Today we're discussing AI in education.
```

### Indian (Hinglish):
```
Ishaan: Yaar, aaj ka topic bahut interesting hai!
Sameera: Haan! AI education ko transform kar raha hai.
```

## ✅ Benefits

- ✅ Unlimited podcasts
- ✅ No API costs
- ✅ Works offline
- ✅ Private & secure
- ✅ No repetition
- ✅ Natural dialogue
- ✅ Audio generation
- ✅ 3D avatar integration (In Progress)

## 🔧 Troubleshooting

### Ollama not found?
Download: https://ollama.com/download

### Model not found?
```bash
ollama list
ollama pull llama2
```

### Audio generation issues?
Ensure ffmpeg is installed:
- Windows: Download from https://ffmpeg.org/download.html
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

### Port already in use?
Change the port in `config.py` or run:
```bash
python web_podcast_ollama.py --port 5001
```

## 🎯 Current Status

✅ **Working:**
- Web interface
- AI script generation
- Audio conversion

🔄 **In Progress:**
- Realistic audio merging
- 3D avatar integration

## 🎉 That's It!

Generate unlimited podcast scripts with no limits!

---

Made with ❤️ using Ollama & Flask
