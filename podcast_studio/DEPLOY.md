# Deployment Guide

## Railway (Cloud — Audio + Script only)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to https://railway.app and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway auto-detects Python and deploys

### Step 3: Set Environment Variables on Railway
In Railway dashboard → your project → **Variables** tab, add:
```
OPENROUTER_API_KEY = sk-or-v1-xxxxxxxxxxxx
VIDEO_ENABLED = false
```

### Step 4: Done!
Railway gives you a public URL like `https://your-app.up.railway.app`

---

## Local Machine (Full — Audio + Script + Video)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with video enabled
set VIDEO_ENABLED=true   # Windows CMD
$env:VIDEO_ENABLED="true"  # Windows PowerShell

python app.py
```
Open: http://localhost:8080

---

## Notes
- **Audio/Script generation**: Works on Railway (free tier)
- **Video generation (Wav2Lip)**: Local machine only (requires GPU + FFmpeg)
- Railway free tier: 500 hours/month, 512MB RAM — sufficient for this app
