# Troubleshooting Guide

## Common Issues and Solutions

### 1. Ollama Not Found

**Error:** `Ollama not found` or `Connection refused`

**Solutions:**
- Download and install Ollama from https://ollama.com/download
- Ensure Ollama service is running
- Check if Ollama is in your system PATH

**Verify Installation:**
```bash
ollama --version
ollama list
```

### 2. Model Not Available

**Error:** `Model 'llama2' not found`

**Solutions:**
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama2

# Or use alternative models
ollama pull mistral
ollama pull gemma3:1b
```

### 3. Python Dependencies Issues

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solutions:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install flask ollama gtts pydub
```

### 4. Audio Generation Fails

**Error:** `ffmpeg not found` or `Audio generation failed`

**Solutions:**

**Windows:**
1. Download ffmpeg from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Restart terminal

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 5. Port Already in Use

**Error:** `Address already in use: Port 5000`

**Solutions:**

**Option 1: Kill the process**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

**Option 2: Use different port**
```python
# Edit web_podcast_ollama.py
app.run(debug=True, port=5001)
```

### 6. Script Generation Takes Too Long

**Issue:** Generation exceeds 3 minutes

**Solutions:**
- Use a faster model: `gemma3:1b`
- Reduce blog content length
- Check system resources (CPU/RAM)
- Ensure no other heavy processes running

**Example:**
```python
generator = PodcastGeneratorOllama(model="gemma3:1b")
```

### 7. Generated Script Has Emojis/Formatting

**Issue:** Script contains unwanted characters

**Solutions:**
- The system automatically cleans scripts
- If issues persist, check `utils.py` cleaning functions
- Update post-processing rules

### 8. Audio Quality Issues

**Issue:** Poor audio quality or robotic voice

**Solutions:**
- Increase audio bitrate in `config.py`:
```python
AUDIO_BITRATE = "256k"  # Higher quality
```
- Consider using ElevenLabs for premium voices
- Adjust TTS speed multiplier

### 9. Memory Issues

**Error:** `Out of memory` or system slowdown

**Solutions:**
- Use smaller model: `gemma3:1b`
- Close other applications
- Increase system swap space
- Process shorter content

### 10. Import Errors

**Error:** `ImportError: cannot import name 'X'`

**Solutions:**
```bash
# Ensure you're in the correct directory
cd T32_WORKING_COPY

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version (3.8+ required)
python --version
```

## Platform-Specific Issues

### Windows

**Issue:** Scripts don't run
```bash
# Use python instead of python3
python web_podcast_ollama.py
```

**Issue:** Path issues
```bash
# Use backslashes or raw strings
path = r"C:\Users\...\podcasts"
```

### Linux/Mac

**Issue:** Permission denied
```bash
# Make scripts executable
chmod +x scripts/setup.sh

# Run with proper permissions
sudo python3 web_podcast_ollama.py
```

## Performance Optimization

### Slow Generation

1. **Use faster model:**
```python
generator = PodcastGeneratorOllama(model="gemma3:1b")
```

2. **Reduce temperature:**
```python
options={'temperature': 0.5}  # More deterministic, faster
```

3. **Limit output length:**
```python
options={'num_predict': 400}  # Shorter scripts
```

### High Memory Usage

1. **Monitor Ollama:**
```bash
# Check Ollama memory usage
ollama ps
```

2. **Restart Ollama:**
```bash
# Stop and restart
ollama stop
ollama serve
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Ollama Logs

```bash
# View Ollama logs
ollama logs
```

### Test Components Individually

```python
# Test Ollama connection
import ollama
response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': 'Hello'}])
print(response)

# Test TTS
from gtts import gTTS
tts = gTTS('Test', lang='en')
tts.save('test.mp3')
```

## Getting Help

If issues persist:

1. Check GitHub Issues: [Repository Issues](https://github.com/varungupta132/T32_Autonomous-AI-Blog-to-Podcast-and-Video-Agent-Using-Virtual-3D-Avatars/issues)
2. Review documentation in `/docs` folder
3. Check Ollama documentation: https://ollama.com/docs
4. Create a new issue with:
   - Error message
   - System information
   - Steps to reproduce
   - Expected vs actual behavior

## System Requirements

**Minimum:**
- Python 3.8+
- 8GB RAM
- 5GB free disk space
- Internet (for initial setup)

**Recommended:**
- Python 3.10+
- 16GB RAM
- 10GB free disk space
- SSD storage
- Multi-core CPU
