import subprocess
import re
import imageio_ffmpeg

def get_audio_duration(file_path):
    """
    Extracts the duration of an audio file using ffmpeg -i, 
    bypassing the need for ffprobe.
    Returns duration in seconds (float).
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    try:
        # ffmpeg -i outputs file information to stderr
        result = subprocess.run(
            [ffmpeg_exe, "-i", str(file_path)],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Look for the Duration line: "  Duration: 00:00:05.12, start: 0.000000, bitrate: 128 kb/s"
        match = re.search(r"Duration:\s+(\d+):(\d+):(\d+\.\d+)", result.stderr)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            return hours * 3600 + minutes * 60 + seconds
        
        print(f"Warning: Could not parse duration for {file_path} from ffmpeg output.")
        return 0.0
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return 0.0
