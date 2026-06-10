"""
🎬 AVATAR VIDEO GENERATOR
Audio → Talking Avatar Video using Wav2Lip

Pipeline:
1. Audio file (from ElevenLabs or any source)
2. Face image (jpg/png)
3. Wav2Lip AI → Lip-synced video

Author: AI Assistant
Date: March 3, 2026
"""

import os
import subprocess
from pathlib import Path
import shutil

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories
AVATAR_DIR = Path("avatar_assets")
OUTPUT_DIR = Path("avatar_videos")
TEMP_DIR = Path("temp_avatar")

# Wav2Lip repository path (will be cloned if not exists)
WAV2LIP_DIR = Path("Wav2Lip")

# Default face image (you can change this)
DEFAULT_FACE = AVATAR_DIR / "default_face.jpg"


# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    dependencies = {
        "git": "git --version",
        "python": "python --version",
        "ffmpeg": "ffmpeg -version"
    }
    
    missing = []
    
    for name, command in dependencies.items():
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            print(f"   ✅ {name} installed")
        except:
            print(f"   ❌ {name} NOT installed")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("\nInstall instructions:")
        if "git" in missing:
            print("   • Git: https://git-scm.com/downloads")
        if "ffmpeg" in missing:
            print("   • FFmpeg: https://ffmpeg.org/download.html")
        return False
    
    print("✅ All dependencies installed!\n")
    return True


def setup_wav2lip():
    """Clone and setup Wav2Lip repository"""
    print("📦 Setting up Wav2Lip...")
    
    if WAV2LIP_DIR.exists():
        print("   ✅ Wav2Lip already exists")
        return True
    
    try:
        print("   📥 Cloning Wav2Lip repository...")
        subprocess.run([
            "git", "clone",
            "https://github.com/Rudrabha/Wav2Lip.git"
        ], check=True)
        
        print("   ✅ Wav2Lip cloned successfully")
        
        # Download pretrained model
        print("\n   📥 Downloading pretrained model...")
        print("   ⚠️  Manual step required:")
        print("   1. Download model from: https://github.com/Rudrabha/Wav2Lip")
        print("   2. Place in: Wav2Lip/checkpoints/")
        print("   3. File name: wav2lip_gan.pth")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    dirs = [AVATAR_DIR, OUTPUT_DIR, TEMP_DIR]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ {dir_path}")
    
    print()


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def generate_avatar_video(audio_file, face_image=None, output_name="avatar_video"):
    """
    Generate talking avatar video from audio
    
    Args:
        audio_file: Path to audio file (mp3/wav)
        face_image: Path to face image (jpg/png) - optional
        output_name: Name for output video (without extension)
        
    Returns:
        Path to generated video file
    """
    
    print("🎬 AVATAR VIDEO GENERATOR")
    print("="*60)
    
    # Step 1: Validate inputs
    print("\n📝 Step 1: Validating inputs...")
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"   ❌ Audio file not found: {audio_file}")
        return None
    print(f"   ✅ Audio: {audio_path.name}")
    
    # Use default face if not provided
    if face_image is None:
        if DEFAULT_FACE.exists():
            face_path = DEFAULT_FACE
        else:
            print(f"   ❌ No face image provided and default not found")
            print(f"   💡 Place a face image at: {DEFAULT_FACE}")
            return None
    else:
        face_path = Path(face_image)
        if not face_path.exists():
            print(f"   ❌ Face image not found: {face_image}")
            return None
    
    print(f"   ✅ Face: {face_path.name}")
    
    # Step 2: Check Wav2Lip
    print("\n🔧 Step 2: Checking Wav2Lip...")
    
    if not WAV2LIP_DIR.exists():
        print("   ❌ Wav2Lip not found!")
        print("   💡 Run setup first: python avatar_video_generator.py --setup")
        return None
    
    inference_script = WAV2LIP_DIR / "inference.py"
    if not inference_script.exists():
        print("   ❌ Wav2Lip inference script not found")
        return None
    
    checkpoint = WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"
    if not checkpoint.exists():
        print("   ❌ Wav2Lip model not found!")
        print("   💡 Download from: https://github.com/Rudrabha/Wav2Lip")
        print(f"   💡 Place at: {checkpoint}")
        return None
    
    print("   ✅ Wav2Lip ready")
    
    # Step 3: Generate video
    print("\n🎥 Step 3: Generating video...")
    print("   ⏳ This may take 1-3 minutes...")
    
    output_path = OUTPUT_DIR / f"{output_name}.mp4"
    
    try:
        # Run Wav2Lip inference
        cmd = [
            "python",
            str(inference_script),
            "--checkpoint_path", str(checkpoint),
            "--face", str(face_path),
            "--audio", str(audio_path),
            "--outfile", str(output_path)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(WAV2LIP_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and output_path.exists():
            file_size = output_path.stat().st_size / 1024 / 1024
            
            print("   ✅ Video generated successfully!")
            print(f"\n📊 Output:")
            print(f"   • File: {output_path.name}")
            print(f"   • Size: {file_size:.2f} MB")
            print(f"   • Path: {output_path.absolute()}")
            
            return output_path
        else:
            print("   ❌ Video generation failed")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def batch_generate(audio_files, face_image=None):
    """
    Generate multiple avatar videos from multiple audio files
    
    Args:
        audio_files: List of audio file paths
        face_image: Face image to use for all videos
        
    Returns:
        List of generated video paths
    """
    
    print("🎬 BATCH AVATAR VIDEO GENERATION")
    print("="*60)
    print(f"\n📊 Processing {len(audio_files)} audio files...\n")
    
    videos = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {Path(audio_file).name}")
        print("-"*60)
        
        output_name = f"avatar_{i}_{Path(audio_file).stem}"
        video = generate_avatar_video(audio_file, face_image, output_name)
        
        if video:
            videos.append(video)
            print(f"✅ Success: {video.name}")
        else:
            print(f"❌ Failed: {Path(audio_file).name}")
    
    print("\n" + "="*60)
    print(f"🎉 Batch Complete: {len(videos)}/{len(audio_files)} successful")
    
    return videos


# ============================================================================
# INTEGRATION WITH PODCAST SYSTEM
# ============================================================================

def podcast_to_avatar_video(script, output_name="podcast_avatar"):
    """
    Complete pipeline: Script → Audio → Avatar Video
    
    Args:
        script: Podcast script text
        output_name: Name for output files
        
    Returns:
        Path to generated video
    """
    
    print("🎙️ PODCAST TO AVATAR VIDEO PIPELINE")
    print("="*60)
    
    # Step 1: Generate audio from script
    print("\n🎤 Step 1: Generating audio from script...")
    
    try:
        # Import from standalone generator
        import sys
        sys.path.append('.')
        from standalone_podcast_generator import generate_podcast
        
        # Generate audio
        audio_file = generate_podcast(script, output_name)
        
        if not audio_file:
            print("   ❌ Audio generation failed")
            return None
        
        print(f"   ✅ Audio generated: {audio_file}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   💡 Make sure standalone_podcast_generator.py is available")
        return None
    
    # Step 2: Generate avatar video
    print("\n🎬 Step 2: Generating avatar video...")
    
    video_file = generate_avatar_video(audio_file, output_name=output_name)
    
    if video_file:
        print("\n" + "="*60)
        print("🎉 COMPLETE PIPELINE SUCCESS!")
        print("="*60)
        print(f"\n📊 Generated:")
        print(f"   • Audio: {audio_file}")
        print(f"   • Video: {video_file}")
        
        return video_file
    else:
        print("\n❌ Video generation failed")
        return None


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI interface"""
    import sys
    
    print("\n" + "="*60)
    print(" 🎬 AVATAR VIDEO GENERATOR")
    print(" Audio → Talking Avatar Video")
    print("="*60)
    
    # Check for setup flag
    if "--setup" in sys.argv:
        print("\n🔧 SETUP MODE\n")
        create_directories()
        
        if not check_dependencies():
            print("\n❌ Please install missing dependencies first!")
            return
        
        if setup_wav2lip():
            print("\n✅ Setup complete!")
            print("\n📝 Next steps:")
            print("   1. Download Wav2Lip model (wav2lip_gan.pth)")
            print("   2. Place in: Wav2Lip/checkpoints/")
            print("   3. Add face image to: avatar_assets/default_face.jpg")
            print("   4. Run: python avatar_video_generator.py --test")
        else:
            print("\n❌ Setup failed!")
        
        return
    
    # Check for test flag
    if "--test" in sys.argv:
        print("\n🧪 TEST MODE\n")
        
        # Check if we have test files
        test_audio = "generated_podcasts/hinglish_cohost.mp3"
        
        if not Path(test_audio).exists():
            print(f"❌ Test audio not found: {test_audio}")
            print("💡 Generate a podcast first using standalone_podcast_generator.py")
            return
        
        print(f"✅ Using test audio: {test_audio}")
        
        video = generate_avatar_video(test_audio, output_name="test_avatar")
        
        if video:
            print("\n🎉 Test successful!")
            print(f"🎥 Video: {video}")
        else:
            print("\n❌ Test failed!")
        
        return
    
    # Interactive mode
    print("\nOptions:")
    print("1. Generate avatar video from audio file")
    print("2. Batch generate from multiple audio files")
    print("3. Complete pipeline (script → audio → video)")
    print("4. Setup Wav2Lip")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        audio_file = input("Audio file path: ").strip()
        face_image = input("Face image path (press Enter for default): ").strip()
        output_name = input("Output name: ").strip() or "avatar_video"
        
        face = face_image if face_image else None
        video = generate_avatar_video(audio_file, face, output_name)
        
        if video:
            print(f"\n✅ Video generated: {video}")
    
    elif choice == "2":
        print("\nEnter audio file paths (one per line, empty line to finish):")
        audio_files = []
        while True:
            path = input().strip()
            if not path:
                break
            audio_files.append(path)
        
        if audio_files:
            face_image = input("Face image path (press Enter for default): ").strip()
            face = face_image if face_image else None
            
            videos = batch_generate(audio_files, face)
            print(f"\n✅ Generated {len(videos)} videos")
    
    elif choice == "3":
        print("\nPaste your script (press Enter twice when done):")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        
        script = "\n".join(lines)
        output_name = input("Output name: ").strip() or "podcast_avatar"
        
        video = podcast_to_avatar_video(script, output_name)
        
        if video:
            print(f"\n✅ Video generated: {video}")
    
    elif choice == "4":
        create_directories()
        check_dependencies()
        setup_wav2lip()
    
    else:
        print("❌ Invalid choice!")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
USAGE EXAMPLES:

1. Setup (first time):
   python avatar_video_generator.py --setup

2. Test with existing audio:
   python avatar_video_generator.py --test

3. Generate from audio file:
   from avatar_video_generator import generate_avatar_video
   
   video = generate_avatar_video(
       audio_file="my_audio.mp3",
       face_image="my_face.jpg",
       output_name="my_video"
   )

4. Complete pipeline (script to video):
   from avatar_video_generator import podcast_to_avatar_video
   
   script = '''
   Alex: Hello everyone!
   Sam: Welcome to our show!
   '''
   
   video = podcast_to_avatar_video(script, "my_podcast")

5. Batch processing:
   from avatar_video_generator import batch_generate
   
   audio_files = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]
   videos = batch_generate(audio_files, "face.jpg")

REQUIREMENTS:
- Python 3.7+
- Git
- FFmpeg
- Wav2Lip (auto-downloaded)
- GPU recommended (but CPU works, just slower)

SETUP STEPS:
1. Run: python avatar_video_generator.py --setup
2. Download Wav2Lip model: https://github.com/Rudrabha/Wav2Lip
3. Place model in: Wav2Lip/checkpoints/wav2lip_gan.pth
4. Add face image: avatar_assets/default_face.jpg
5. Test: python avatar_video_generator.py --test

OUTPUT:
- Videos saved in: avatar_videos/
- Format: MP4
- Quality: HD (depends on input face image)
"""


if __name__ == "__main__":
    main()
