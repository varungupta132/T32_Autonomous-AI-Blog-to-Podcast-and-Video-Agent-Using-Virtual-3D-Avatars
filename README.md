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

### Prerequisites
- Python 3.8 or higher
- Ollama installed on your system

### 1. Install Ollama

Download from: https://ollama.com/download

### 2. Install Python Packages

```bash
pip install -r requirements.txt
```

### 3. Pull AI Model

```bash
ollama pull llama2
```

### 4. Run Web App

```bash
python web_podcast_ollama.py
```

Open: http://localhost:5000

## 📁 Files

- **web_podcast_ollama.py** - Web interface (Recommended)
- **podcast_generator_ollama.py** - Command line interface
- **podcast_to_voice.py** - Audio converter
- **config.py** - Configuration settings
- **utils.py** - Utility functions
- **error_handler.py** - Error handling and logging
- **PROGRESS.md** - Project progress report
- **ARCHITECTURE.md** - System architecture documentation
- **INSTALLATION.md** - Detailed installation guide
- **CONTRIBUTING.md** - Contribution guidelines
- **CHANGELOG.md** - Version history
- **LICENSE** - MIT License

### Documentation
- **docs/API.md** - API documentation
- **docs/USAGE_EXAMPLES.md** - Usage examples
- **docs/TROUBLESHOOTING.md** - Troubleshooting guide

### Examples
- **examples/sample_blog.txt** - Sample blog content
- **examples/batch_process.py** - Batch processing script

### Scripts
- **scripts/setup.sh** - Linux/Mac setup script
- **scripts/setup.bat** - Windows setup script

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

- ✅ Unlimited podcasts - no API costs
- ✅ Works offline - complete privacy
- ✅ No repetition - natural dialogue
- ✅ Audio generation with TTS
- ✅ Multiple podcast formats
- ✅ Bilingual support (English/Hinglish)
- ✅ Open source and customizable
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
- Web interface with beautiful UI
- AI script generation with multiple models
- Audio conversion with TTS
- Batch processing support
- Comprehensive documentation
- Unit tests and CI/CD
- Error handling and logging

🔄 **In Progress:**
- Realistic audio merging improvements
- 3D avatar video integration
- Additional language support

## 🎉 That's It!

Generate unlimited podcast scripts with no limits!

## 📚 Documentation

- [Installation Guide](INSTALLATION.md)
- [Architecture](ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Usage Examples](docs/USAGE_EXAMPLES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Performance Guide](docs/PERFORMANCE.md)
- [FAQ](docs/FAQ.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Show Your Support

If you find this project helpful, please give it a star on GitHub!
