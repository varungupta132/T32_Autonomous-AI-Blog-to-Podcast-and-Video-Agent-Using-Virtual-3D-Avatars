# 🎙️ Blog to Podcast Generator (Ollama)

Convert your blogs into engaging podcast scripts using local AI - No API limits!

## ✨ Features

- 🎤 **Single Host** - One person podcast
- 👥 **Co-Host** - Two people dialogue
- 🎭 **Multi-Host** - Three people panel
- 🌐 **Global** - English audience
- 🇮🇳 **Indian** - Hinglish audience
- ♾️ **Unlimited** - No API limits!

## 🚀 Quick Start

### 1. Install Ollama

Download from: https://ollama.com/download

### 2. Install Python Packages

```bash
pip install ollama flask
```

### 3. Test Installation

```bash
python test_ollama.py
```

### 4. Run Web App

```bash
python web_podcast_ollama.py
```

Open: http://localhost:5000

## 📁 Files

- **web_podcast_ollama.py** - Web interface (Recommended)
- **podcast_generator_ollama.py** - Command line interface
- **test_ollama.py** - Test Ollama installation
- **setup_ollama.bat** - Auto setup script

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

## 🔧 Troubleshooting

### Ollama not found?
Download: https://ollama.com/download

### Model not found?
```bash
ollama list
ollama pull llama2
```

## 🎉 That's It!

Generate unlimited podcast scripts with no limits!

---

Made with ❤️ using Ollama
