# 🎬 Avatar Video Generator Guide

Complete guide to create talking avatar videos from audio using Wav2Lip AI.

---

## 🎯 What This Does

```
Audio File (MP3/WAV)
    +
Face Image (JPG/PNG)
    ↓
Wav2Lip AI Magic
    ↓
Talking Avatar Video (MP4) ✨
```

**Result:** Realistic lip-synced video where the face speaks your audio!

---

## 🚀 Quick Start

### Step 1: Setup (One-time)

```bash
python avatar_video_generator.py --setup
```

This will:
- Create necessary folders
- Check dependencies (Git, FFmpeg, Python)
- Clone Wav2Lip repository

### Step 2: Download Model

1. Go to: https://github.com/Rudrabha/Wav2Lip
2. Download: `wav2lip_gan.pth` (pretrained model)
3. Place in: `Wav2Lip/checkpoints/wav2lip_gan.pth`

### Step 3: Add Face Image

Place a front-facing photo in:
```
avatar_assets/default_face.jpg
```

**Face image tips:**
- Front-facing, clear face
- Good lighting
- Neutral expression
- JPG or PNG format
- Recommended size: 512x512 or higher

### Step 4: Test

```bash
python avatar_video_generator.py --test
```

---

## 📋 Requirements

### Software:
- ✅ Python 3.7+
- ✅ Git
- ✅ FFmpeg
- ✅ GPU (recommended but optional)

### Install FFmpeg:
**Windows:**
```bash
# Download from: https://ffmpeg.org/download.html
# Add to PATH
```

**Check installation:**
```bash
ffmpeg -version
```

---

## 🎨 Usage Methods

### Method 1: From Audio File

```python
from avatar_video_generator import generate_avatar_video

video = generate_avatar_video(
    audio_file="my_podcast.mp3",
    face_image="my_face.jpg",
    output_name="talking_avatar"
)

print(f"Video created: {video}")
```

### Method 2: Complete Pipeline (Script → Video)

```python
from avatar_video_generator import podcast_to_avatar_video

script = """
Alex: Hello everyone! Welcome to our podcast.
Sam: Thanks for joining us today!
Alex: Let's discuss AI and technology.
Sam: This is going to be exciting!
"""

video = podcast_to_avatar_video(script, "my_podcast_video")
```

This will:
1. Generate audio from script (using ElevenLabs)
2. Create lip-synced video automatically

### Method 3: Batch Processing

```python
from avatar_video_generator import batch_generate

audio_files = [
    "podcast1.mp3",
    "podcast2.mp3",
    "podcast3.mp3"
]

videos = batch_generate(audio_files, face_image="face.jpg")

print(f"Generated {len(videos)} videos!")
```

### Method 4: Interactive CLI

```bash
python avatar_video_generator.py
```

Then choose from menu:
1. Generate from audio file
2. Batch generate
3. Complete pipeline (script → video)
4. Setup

---

## 📁 File Structure

```
Mini_Project/
├── avatar_video_generator.py      # Main script
├── avatar_assets/                 # Face images
│   └── default_face.jpg          # Default face
├── avatar_videos/                 # Output videos
│   └── avatar_video.mp4          # Generated videos
├── Wav2Lip/                       # Wav2Lip repo (auto-downloaded)
│   ├── inference.py
│   └── checkpoints/
│       └── wav2lip_gan.pth       # Model (manual download)
└── generated_podcasts/            # Audio files
    └── podcast.mp3
```

---

## 🎯 Complete Workflow Example

### Scenario: Blog → Talking Avatar Video

```python
# Step 1: Generate podcast script (already done)
# You have: web_podcast_openrouter.py

# Step 2: Generate audio (already done)
# You have: standalone_podcast_generator.py

# Step 3: Generate avatar video (NEW!)
from avatar_video_generator import generate_avatar_video

# Use the audio from your podcast
audio_file = "generated_podcasts/hinglish_cohost.mp3"
face_image = "avatar_assets/my_face.jpg"

video = generate_avatar_video(
    audio_file=audio_file,
    face_image=face_image,
    output_name="my_talking_podcast"
)

print(f"✅ Talking avatar video: {video}")
```

**Result:** MP4 video with face speaking your podcast!

---

## ⚙️ Advanced Options

### Custom Face for Each Speaker

```python
# For multi-speaker podcasts
speakers = {
    "Alex": "faces/alex.jpg",
    "Sam": "faces/sam.jpg",
    "Jordan": "faces/jordan.jpg"
}

# Generate separate videos for each speaker
# Then merge them (advanced)
```

### Video Quality Settings

Edit in Wav2Lip inference:
- Resolution: Depends on input face image
- FPS: 25 (default)
- Quality: High (GAN model)

### GPU vs CPU

**GPU (Recommended):**
- Faster (2-3 minutes per video)
- Better quality
- Requires CUDA

**CPU (Fallback):**
- Slower (5-10 minutes per video)
- Still works fine
- No special requirements

---

## 🐛 Troubleshooting

### Issue 1: "Wav2Lip not found"
**Solution:**
```bash
python avatar_video_generator.py --setup
```

### Issue 2: "Model not found"
**Solution:**
- Download `wav2lip_gan.pth` from GitHub
- Place in `Wav2Lip/checkpoints/`

### Issue 3: "FFmpeg not found"
**Solution:**
- Install FFmpeg
- Add to system PATH
- Restart terminal

### Issue 4: "Face not detected"
**Solution:**
- Use clear, front-facing photo
- Good lighting
- Face should be visible
- Try different image

### Issue 5: "Out of memory"
**Solution:**
- Use smaller face image
- Close other applications
- Use CPU mode (slower but works)

### Issue 6: Video quality poor
**Solution:**
- Use higher resolution face image
- Better lighting in face photo
- Use GAN model (not regular)

---

## 📊 Performance

### Generation Time:
| Hardware | Time per Minute |
|----------|----------------|
| GPU (NVIDIA) | 1-2 minutes |
| CPU (Modern) | 5-10 minutes |
| CPU (Old) | 10-20 minutes |

### File Sizes:
- Input audio: ~1 MB per minute
- Input face: 100-500 KB
- Output video: 5-10 MB per minute

---

## 🎨 Tips for Best Results

### Face Image:
1. ✅ Front-facing, centered
2. ✅ Good lighting (no shadows)
3. ✅ Neutral expression
4. ✅ Clear, high resolution
5. ✅ Single person only
6. ❌ Avoid: Side angles, multiple faces, sunglasses

### Audio:
1. ✅ Clear speech
2. ✅ Good quality (not distorted)
3. ✅ Proper volume
4. ✅ Minimal background noise

### Output:
- Videos are MP4 format
- HD quality (depends on input)
- Ready for YouTube/social media
- Can be edited further if needed

---

## 🔗 Integration with Your System

### Current Pipeline:
```
Blog Content
    ↓
web_podcast_openrouter.py (Script generation)
    ↓
standalone_podcast_generator.py (Audio generation)
    ↓
avatar_video_generator.py (Video generation) ← NEW!
    ↓
Talking Avatar Video ✨
```

### Complete Automation:

```python
# One command to rule them all!
from avatar_video_generator import podcast_to_avatar_video

script = """
Alex: Welcome to AI podcast!
Sam: Let's discuss technology!
"""

video = podcast_to_avatar_video(script, "complete_podcast")

# Done! You have:
# - Audio file
# - Video file with talking avatar
```

---

## 🎯 Use Cases

1. **YouTube Videos** - Talking head videos
2. **Social Media** - Short clips with avatar
3. **Educational Content** - Explainer videos
4. **Podcasts** - Visual version of audio
5. **Presentations** - Automated speaker videos
6. **Marketing** - Product explanation videos

---

## 📝 Example Scripts

### Example 1: Simple Generation
```bash
python avatar_video_generator.py --test
```

### Example 2: Custom Audio
```python
from avatar_video_generator import generate_avatar_video

generate_avatar_video(
    "my_audio.mp3",
    "my_face.jpg",
    "output_video"
)
```

### Example 3: Batch Processing
```python
from avatar_video_generator import batch_generate

audios = ["ep1.mp3", "ep2.mp3", "ep3.mp3"]
batch_generate(audios, "host_face.jpg")
```

---

## 🚀 Next Steps

1. ✅ Setup Wav2Lip: `python avatar_video_generator.py --setup`
2. ✅ Download model (manual step)
3. ✅ Add face image
4. ✅ Test: `python avatar_video_generator.py --test`
5. ✅ Generate your first video!

---

## 💡 Pro Tips

1. **Multiple Faces**: Create different videos for each speaker, then merge
2. **Background**: Use green screen face images for easy background replacement
3. **Quality**: Higher resolution face = better video quality
4. **Speed**: GPU makes it 5x faster
5. **Automation**: Integrate with your podcast pipeline for full automation

---

## 🎉 Summary

**What you get:**
- ✅ Audio → Video conversion
- ✅ Realistic lip-sync
- ✅ Free and open-source
- ✅ Easy to use
- ✅ Integrates with your podcast system

**Perfect for:**
- Creating visual podcasts
- YouTube content
- Social media videos
- Automated video generation

---

**Ready to create talking avatars! 🎬✨**
