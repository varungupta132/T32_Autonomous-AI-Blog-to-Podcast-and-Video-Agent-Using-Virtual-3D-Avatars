# 📦 Installation Guide

Complete step-by-step installation guide for the AI Blog-to-Podcast Generator.

---

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: 10GB free space
- **Python**: Version 3.8 or higher

### Check Python Version
```bash
python --version
# or
python3 --version
```

If Python is not installed, download from: https://www.python.org/downloads/

---

## Step 1: Install Ollama

Ollama is required for local AI processing.

### Windows
1. Download from: https://ollama.com/download
2. Run the installer
3. Follow installation wizard

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Verify Installation
```bash
ollama --version
```

---

## Step 2: Download AI Models

Choose one or more models based on your needs:

### Recommended: LLaMA 2 (3.8GB)
```bash
ollama pull llama2
```

### Alternative: Mistral (4.4GB) - Better Quality
```bash
ollama pull mistral
```

### Lightweight: Gemma 3 (815MB) - Faster
```bash
ollama pull gemma3:1b
```

### Verify Models
```bash
ollama list
```

---

## Step 3: Clone Repository

```bash
git clone https://github.com/varungupta132/T32_Autonomous-AI-Blog-to-Podcast-and-Video-Agent-Using-Virtual-3D-Avatars.git

cd T32_Autonomous-AI-Blog-to-Podcast-and-Video-Agent-Using-Virtual-3D-Avatars
```

---

## Step 4: Install Python Dependencies

### Option A: Using pip (Recommended)
```bash
pip install -r requirements.txt
```

### Option B: Using pip3
```bash
pip3 install -r requirements.txt
```

### Option C: Using virtual environment (Best Practice)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 5: Install FFmpeg (For Audio Processing)

FFmpeg is required for audio merging and processing.

### Windows
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit PATH variable
   - Add `C:\ffmpeg\bin`

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Verify Installation
```bash
ffmpeg -version
```

---

## Step 6: Verify Installation

### Test Ollama Connection
```bash
python -c "import ollama; print(ollama.list())"
```

### Test Flask
```bash
python -c "import flask; print(flask.__version__)"
```

### Test Audio Libraries
```bash
python -c "from gtts import gTTS; print('gTTS OK')"
python -c "from pydub import AudioSegment; print('pydub OK')"
```

---

## Step 7: Run the Application

### Web Interface (Recommended)
```bash
python web_podcast_ollama.py
```

Then open: http://localhost:5000

### Command Line Interface
```bash
python podcast_generator_ollama.py
```

### Audio Generator
```bash
python podcast_to_voice.py
```

---

## Troubleshooting

### Issue: "Ollama not found"
**Solution:**
1. Ensure Ollama is installed
2. Restart terminal/command prompt
3. Check PATH environment variable

### Issue: "Model not found"
**Solution:**
```bash
ollama list  # Check installed models
ollama pull llama2  # Download model
```

### Issue: "Module not found" errors
**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: "FFmpeg not found"
**Solution:**
1. Install FFmpeg (see Step 5)
2. Restart terminal
3. Verify: `ffmpeg -version`

### Issue: "Port 5000 already in use"
**Solution:**
Edit `web_podcast_ollama.py` and change port:
```python
app.run(debug=True, port=5001)  # Change to 5001
```

### Issue: Slow generation
**Solution:**
1. Use smaller model: `gemma3:1b`
2. Reduce content length
3. Close other applications
4. Check system resources

### Issue: Audio quality issues
**Solution:**
1. Install premium TTS (ElevenLabs)
2. Adjust audio bitrate in code
3. Use better quality models

---

## Optional: ElevenLabs Setup (Premium Voices)

For higher quality voices:

1. Sign up at: https://elevenlabs.io
2. Get API key from dashboard
3. Install library:
```bash
pip install elevenlabs
```
4. Set API key in `standalone_podcast_generator.py`

---

## Directory Structure After Installation

```
T32_Autonomous-AI-Blog-to-Podcast-and-Video-Agent-Using-Virtual-3D-Avatars/
├── web_podcast_ollama.py
├── podcast_generator_ollama.py
├── podcast_to_voice.py
├── standalone_podcast_generator.py
├── requirements.txt
├── README.md
├── PROGRESS.md
├── ARCHITECTURE.md
├── INSTALLATION.md
├── audio_segments/          # Created automatically
├── final_podcasts/          # Created automatically
└── venv/                    # If using virtual environment
```

---

## Next Steps

1. ✅ Read [README.md](README.md) for usage guide
2. ✅ Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. ✅ Run web interface: `python web_podcast_ollama.py`
4. ✅ Generate your first podcast!

---

## Quick Start Commands

```bash
# 1. Install Ollama
# Download from: https://ollama.com/download

# 2. Pull model
ollama pull llama2

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run web app
python web_podcast_ollama.py

# 5. Open browser
# http://localhost:5000
```

---

## Support

If you encounter issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Verify all prerequisites are installed
3. Check Ollama is running: `ollama list`
4. Ensure Python version is 3.8+

---

**Installation Time**: ~15-30 minutes (depending on model download speed)

**Last Updated**: March 2026
