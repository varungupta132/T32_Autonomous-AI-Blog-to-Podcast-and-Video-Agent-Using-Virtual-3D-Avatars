# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python
python --version  # Need 3.11+

# Check Node
node --version    # Need 20+

# Check Ollama
ollama --version  # Need latest

# Check FFmpeg
ffmpeg -version   # Need latest
```

## Installation

### Step 1: Install Ollama Model
```bash
ollama pull llama3
```

### Step 2: Setup Backend
```bash
cd ai-blog-podcast/backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
copy ..\.env.example .env  # Windows
# cp ../.env.example .env  # macOS/Linux
```

### Step 3: Setup Frontend
```bash
cd ai-blog-podcast/frontend
npm install
```

## Run Application

### Terminal 1: Start Ollama
```bash
ollama serve
```

### Terminal 2: Start Backend
```bash
cd backend
# Activate venv first if not already active
uvicorn main:app --reload
```

### Terminal 3: Start Frontend
```bash
cd frontend
npm run dev
```

## Access Application

Open browser: **http://localhost:5173**

## First Podcast

1. Paste this sample blog:
```
Artificial Intelligence is transforming technology. Machine learning enables computers to learn from data. AI applications include healthcare, finance, and autonomous vehicles. The future of AI is exciting and full of possibilities.
```

2. Select:
   - Podcast Type: **Co-host**
   - Audience: **Global**
   - Language: **English**

3. Click **Generate Podcast**

4. Wait 15-20 seconds

5. Listen to your podcast!

## Docker Alternative

```bash
cd ai-blog-podcast

# Start Ollama on host
ollama serve

# Run containers
docker-compose up --build

# Access at http://localhost:3000
```

## Troubleshooting

### "Connection refused" error
```bash
# Make sure Ollama is running
ollama serve
```

### "Module not found" error
```bash
# Reinstall dependencies
pip install -r requirements.txt  # Backend
npm install                       # Frontend
```

### Port already in use
```bash
# Change port in .env
BACKEND_PORT=8001
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [EXAMPLES.md](EXAMPLES.md) for more use cases
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design

## Need Help?

- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Open an issue on GitHub

---

**Enjoy creating podcasts! 🎙️**
