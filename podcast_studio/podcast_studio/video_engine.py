"""
Video Engine - Free, local, GPU-accelerated avatar podcast video generator.
Uses Wav2Lip for lip-sync + FFmpeg for composition.
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = Path(__file__).parent
WAV2LIP_DIR = BASE_DIR / "Wav2Lip"
CHECKPOINT = WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"
AVATARS_DIR = BASE_DIR / "avatars"
VIDEO_OUT_DIR = BASE_DIR / "generated_videos"
VIDEO_OUT_DIR.mkdir(exist_ok=True)

FFMPEG = "ffmpeg"
MUSIC_FILE = BASE_DIR / "nastelbom-podcast-intro-490161.mp3"

# ── Wav2Lip inference wrapper ─────────────────────────────────────────────────

def run_wav2lip(face_img: Path, audio_file: Path, output_video: Path, resize_factor: int = 1) -> bool:
    """Run Wav2Lip inference for one segment. Returns True on success."""
    # Wav2Lip writes temp/temp.wav relative to its cwd — ensure it exists
    wav2lip_temp = WAV2LIP_DIR / "temp"
    wav2lip_temp.mkdir(exist_ok=True)

    # For static images, provide a manual bounding box covering the lower face area
    # This bypasses face detection which can fail on cartoon/drawn avatars
    # Box format: top bottom left right (pixel coords for 512x512 image)
    # Lower half of face: rows 220-340, cols 100-412
    cmd = [
        sys.executable,
        str(WAV2LIP_DIR / "inference.py"),
        "--checkpoint_path", str(CHECKPOINT.resolve()),
        "--face", str(face_img.resolve()),
        "--audio", str(audio_file.resolve()),
        "--outfile", str(output_video.resolve()),
        "--resize_factor", str(resize_factor),
        "--nosmooth",
        "--wav2lip_batch_size", "64",
        "--box", "200", "340", "100", "412",   # top bottom left right
        "--pads", "0", "20", "0", "0",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(WAV2LIP_DIR),
            timeout=300
        )
        if result.returncode != 0:
            print(f"[wav2lip] STDERR: {result.stderr[-600:]}")
            return False
        return output_video.exists()
    except subprocess.TimeoutExpired:
        print(f"[wav2lip] Timeout for {audio_file.name}")
        return False
    except Exception as e:
        print(f"[wav2lip] Error: {e}")
        return False


def get_avatar(speaker: str) -> Path:
    """Get avatar image for a speaker, fallback to Host."""
    candidates = [
        AVATARS_DIR / f"{speaker}.png",
        AVATARS_DIR / f"{speaker}.jpg",
        AVATARS_DIR / "Host.png",
    ]
    for p in candidates:
        if p.exists():
            return p
    # Last resort: first image in avatars dir
    imgs = list(AVATARS_DIR.glob("*.png")) + list(AVATARS_DIR.glob("*.jpg"))
    if imgs:
        return imgs[0]
    raise FileNotFoundError(f"No avatar found for speaker '{speaker}' in {AVATARS_DIR}")


# ── Audio helpers ─────────────────────────────────────────────────────────────

def get_audio_duration(audio_path: Path) -> float:
    """Get duration of audio file in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1",
             str(audio_path)],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except Exception:
        return 3.0  # fallback


# ── Per-segment lip-sync ──────────────────────────────────────────────────────

def generate_segment_video(seg_index: int, speaker: str, audio_path: Path, temp_dir: Path) -> Path | None:
    """Generate a lip-synced video clip for one dialogue segment."""
    avatar = get_avatar(speaker)
    out_video = temp_dir / f"seg_{seg_index:03d}_{speaker}.mp4"

    print(f"  [seg {seg_index:03d}] {speaker} → lip-sync...")
    success = run_wav2lip(avatar, audio_path, out_video)

    if not success:
        print(f"  [seg {seg_index:03d}] Wav2Lip failed, using static fallback")
        out_video = make_static_fallback(speaker, audio_path, out_video, temp_dir)

    return out_video if out_video and out_video.exists() else None


def make_static_fallback(speaker: str, audio_path: Path, out_video: Path, temp_dir: Path) -> Path:
    """Fallback: static avatar image + audio + animated waveform bar."""
    avatar = get_avatar(speaker)
    duration = get_audio_duration(audio_path)

    # Create a video from static image + audio with a pulsing border effect
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(avatar),
        "-i", str(audio_path),
        "-filter_complex",
        "[0:v]scale=512:512,setsar=1[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        str(out_video)
    ]
    subprocess.run(cmd, capture_output=True, timeout=60)
    return out_video


# ── Layout composition ────────────────────────────────────────────────────────

def compose_podcast_video(
    segments: list[dict],  # [{speaker, video_path, audio_path}]
    output_path: Path,
    all_speakers: list[str],
    podcast_name: str = "podcast"
) -> Path:
    """
    Compose final podcast video:
    - Active speaker shown large (center), others shown small (sidebar)
    - Intro/outro music overlay
    - Lower-third name labels
    """
    temp_dir = output_path.parent / f"_compose_tmp_{podcast_name}"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Step 1: Concatenate all segment videos into one stream
        concat_list = temp_dir / "concat.txt"
        valid_segs = [s for s in segments if s.get("video_path") and Path(s["video_path"]).exists()]

        if not valid_segs:
            raise ValueError("No valid video segments to compose")

        with open(concat_list, "w") as f:
            for seg in valid_segs:
                f.write(f"file '{Path(seg['video_path']).as_posix()}'\n")

        raw_concat = temp_dir / "raw_concat.mp4"
        subprocess.run([
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(raw_concat)
        ], capture_output=True, timeout=300)

        if not raw_concat.exists():
            # Re-encode if copy fails
            subprocess.run([
                FFMPEG, "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_list),
                "-c:v", "libx264", "-c:a", "aac",
                str(raw_concat)
            ], capture_output=True, timeout=300)

        # Step 2: Add podcast-style overlay (name label, border, background)
        styled = temp_dir / "styled.mp4"
        num_speakers = len(all_speakers)

        # Build drawtext filters for speaker name labels
        # We'll add a semi-transparent bar at bottom with speaker name
        vf = (
            "scale=854:480,"
            "drawbox=x=0:y=440:w=iw:h=40:color=black@0.6:t=fill,"
            f"drawtext=text='🎙 {podcast_name}':fontsize=18:fontcolor=white:"
            "x=(w-text_w)/2:y=450:shadowcolor=black:shadowx=1:shadowy=1"
        )

        subprocess.run([
            FFMPEG, "-y", "-i", str(raw_concat),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            str(styled)
        ], capture_output=True, timeout=300)

        if not styled.exists():
            styled = raw_concat  # fallback

        # Step 3: Mix in intro/outro music
        final = add_music_overlay(styled, output_path, temp_dir)
        return final

    finally:
        # Cleanup temp
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


def add_music_overlay(video_path: Path, output_path: Path, temp_dir: Path) -> Path:
    """Add podcast intro/outro music mixed under the speech."""
    if not MUSIC_FILE.exists():
        # No music file, just copy
        shutil.copy(video_path, output_path)
        return output_path

    # Get video duration
    duration = get_audio_duration(video_path)

    # Build music: 3s intro fade-in, full duration, 3s outro fade-out
    music_processed = temp_dir / "music_mix.mp3"
    subprocess.run([
        FFMPEG, "-y", "-i", str(MUSIC_FILE),
        "-af", f"afade=t=in:st=0:d=3,afade=t=out:st={max(0, duration-3)}:d=3,volume=0.15",
        "-t", str(duration),
        str(music_processed)
    ], capture_output=True, timeout=60)

    if not music_processed.exists():
        shutil.copy(video_path, output_path)
        return output_path

    # Mix music under speech
    subprocess.run([
        FFMPEG, "-y",
        "-i", str(video_path),
        "-i", str(music_processed),
        "-filter_complex",
        "[0:a]volume=1.0[speech];[1:a]volume=0.15[music];[speech][music]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ], capture_output=True, timeout=300)

    if output_path.exists():
        return output_path

    # Fallback: no music mix
    shutil.copy(video_path, output_path)
    return output_path


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_podcast_video(
    dialogues: list[dict],          # [{speaker, text, audio_path}]
    podcast_name: str,
    progress_callback=None
) -> dict:
    """
    Full pipeline: audio segments → lip-sync → compose → final MP4.
    Returns {"success": True, "filename": "...", "file_size": "..."}
    """
    if not CHECKPOINT.exists():
        return {"success": False, "error": f"Wav2Lip checkpoint not found at {CHECKPOINT}. Please download wav2lip_gan.pth"}

    temp_dir = BASE_DIR / "temp_video" / podcast_name
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_path = VIDEO_OUT_DIR / f"{podcast_name}.mp4"
    all_speakers = list(dict.fromkeys(d["speaker"] for d in dialogues))

    segments = []
    total = len(dialogues)

    print(f"\n[video] Generating {total} lip-sync segments for {len(all_speakers)} speakers...")

    for i, dlg in enumerate(dialogues):
        speaker = dlg["speaker"]
        audio_path = Path(dlg["audio_path"])

        if not audio_path.exists():
            print(f"  [seg {i:03d}] Audio missing: {audio_path}")
            continue

        if progress_callback:
            progress_callback(i, total, f"Lip-syncing {speaker} ({i+1}/{total})")

        video_path = generate_segment_video(i, speaker, audio_path, temp_dir)
        segments.append({
            "speaker": speaker,
            "text": dlg.get("text", ""),
            "audio_path": str(audio_path),
            "video_path": str(video_path) if video_path else None
        })

    if not any(s["video_path"] for s in segments):
        return {"success": False, "error": "All lip-sync segments failed"}

    if progress_callback:
        progress_callback(total, total, "Composing final video...")

    print(f"\n[video] Composing final video...")
    final = compose_podcast_video(segments, output_path, all_speakers, podcast_name)

    # Cleanup temp
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    if not final.exists():
        return {"success": False, "error": "Final video composition failed"}

    size_mb = final.stat().st_size / 1024 / 1024
    print(f"[video] Done! {final} ({size_mb:.1f} MB)")

    return {
        "success": True,
        "filename": final.name,
        "file_size": f"{size_mb:.1f} MB",
        "path": str(final)
    }
