# 🎙️ AI Blog-to-Podcast Agent

A full-stack application that converts blog posts into professional podcast audio with support for multiple speakers.

---

## ✨ Features

- **Blog to Podcast**: Convert any blog content into podcast audio
- **Multiple Formats**: Single host, Co-host, Multi-host podcast types
- **Language Support**: English and Hinglish (Indian English)
- **Local AI**: Uses Ollama (llama2 model) - completely free, no API limits
- **Audio Generation**: Converts script to speech using Google TTS
- **Beautiful UI**: Modern gradient design with React
- **History Tracking**: Saves generated podcasts to database
- **Privacy-Focused**: All processing on local machine

---

## 🛠️ Tech Stack

### Frontend
- React 18
- Vite
- TailwindCSS
- Axios

### Backend
- Python 3.11+
- FastAPI
- Ollama (llama2)
- Google TTS
- SQLAlchemy
- Pydub

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Ollama installed

### Setup

1. **Install Ollama and pull the model**:
   ```bash
   ollama pull llama2
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Setup Frontend**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Start Ollama** (in separate terminal):
   ```bash
   ollama serve
   ```

5. **Start Backend**:
   ```bash
   cd ../backend
   venv\Scripts\activate
   python run.py
   ```

6. **Start Frontend**:
   ```bash
   cd ../frontend
   npm run dev
   ```

7. **Open**: http://localhost:5173

---

## 📖 How to Use

1. Open http://localhost:5173
2. Enter your blog content
3. Select podcast type (Single/Co-host/Multi)
4. Choose audience (Global/Indian)
5. Click "Generate Podcast"
6. Wait 30-60 seconds
7. Listen to your podcast!

---

## 📊 Current Status

**Working:**
- ✅ Backend (FastAPI)
- ✅ Frontend (React)
- ✅ Ollama integration
- ✅ Script generation
- ✅ Audio generation
- ✅ UI/UX

**In Progress:**
- 🔄 Full audio merging
- 🔄 FFmpeg integration

**Future:**
- 🎯 Avatar video integration
- 🎯 Multi-language support
- 🎯 Cloud storage

---

## 📁 Project Structure

```
ai-blog-podcast/
├── backend/              # Python FastAPI backend
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── routers/
│   └── services/
├── frontend/            # React frontend
│   └── src/
├── docker-compose.yml
├── Dockerfile.*
└── README.md
```

---

## 📝 Files to Push to GitHub

Only these 3 files:
1. `README.md` - This documentation
2. `ollama_setup.bat` - Ollama installation script
3. `web_podcast_ollama.py` - Working Flask app

---

## 🎯 Features

### Podcast Types
- 🎤 Single Host - One host storytelling
- 👥 Co-Host - Two hosts dialogue
- 🎭 Multi-Speaker - Three hosts panel

### Language Support
- 🌐 English - Global audience
- 🇮🇳 Hinglish - Indian English mix

---

## 📞 Contact

For questions or support, please contact the developer.

---

**Status**: ✅ Working - Backend & Frontend functional
