# 🎙️ Quick Reference Card

## 🚀 Start Application (Easiest Way)

```bash
# Step 1: Setup (first time only)
setup_fullstack.bat

# Step 2: Start servers
start_servers.bat

# Step 3: Open browser
http://localhost:5173
```

## 📝 Script Format

```
Speaker: Dialogue text here

Example:
Alex: Acha toh dekho yaar, AI ke baare mein baat karte hain!
Sam: Wow! Bilkul sahi! AI bahut interesting hai.
```

## 🎤 Available Speakers

| Name | Voice | Gender | Style |
|------|-------|--------|-------|
| Alex | Adam | Male | Friendly |
| Sam | Bella | Female | Warm |
| Jordan | Josh | Male | Expert |
| Casey | Dorothy | Female | Curious |
| Host | Adam | Male | Professional |

## 🎯 Podcast Types

- **Single**: One host (Host)
- **Co-host**: Two hosts (Alex + Sam)
- **Multi**: Three hosts (Alex + Sam + Jordan)

## 🌍 Audiences

- **Global**: Pure English
- **India**: Hinglish (Hindi + English mix)

## 💡 Tips for Best Results

1. ✅ Use `!` for excitement → Excited voice
2. ✅ Use `?` for questions → Curious voice
3. ✅ Keep dialogues under 200 characters
4. ✅ One dialogue per line
5. ✅ Use proper speaker names

## 🎨 Example Scripts

### English
```
Alex: Welcome to our AI podcast!
Sam: Thanks! Let's discuss machine learning.
Alex: Great topic! AI is transforming industries.
Sam: Absolutely! The future looks exciting.
```

### Hinglish
```
Alex: Acha toh dekho yaar, AI ke baare mein baat karte hain!
Sam: Wow! Bilkul sahi! AI bahut interesting hai.
Alex: Dekho, AI ka matlab hai machines bhi soch sakti hain.
Sam: Really? Aur yeh technology ab har jagah use ho rahi hai?
```

## 🔧 Manual Commands

### Backend
```bash
cd ai-blog-podcast/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd ai-blog-podcast/frontend
npm install
npm run dev
```

## 🧪 Test Audio System

```bash
python test_audio_integration.py
```

Output: `ai-blog-podcast/backend/outputs/test_podcast.mp3`

## 📁 Output Location

Generated podcasts: `ai-blog-podcast/backend/outputs/podcast_*.mp3`

## 🐛 Quick Fixes

### Port already in use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Backend won't start
```bash
cd ai-blog-podcast/backend
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
cd ai-blog-podcast/frontend
rm -rf node_modules
npm install
```

## 📊 Audio Quality

- Format: MP3
- Bitrate: 192kbps
- Pause: 800ms between dialogues
- Effects: Normalization + Compression

## 🔑 API Key

Already configured in `.env`:
```
ELEVENLABS_API_KEY=sk_33c17748cbd7ba62cc21225bb2e995d33844a7671dd4f115
```

## 📞 URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 Full Documentation

- `FULLSTACK_AUDIO_GUIDE.md` - Complete guide
- `AUDIO_INTEGRATION_COMPLETE.md` - Technical details
- `HOW_TO_RUN.md` - Original instructions

---

**That's it! Start creating amazing podcasts! 🎉**
