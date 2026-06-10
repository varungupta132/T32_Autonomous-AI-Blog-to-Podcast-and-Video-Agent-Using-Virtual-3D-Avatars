from pathlib import Path

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


def merge_audio_files(audio_files: list, output_file: Path) -> Path:
    """
    Merge MP3 segments into one file.
    Uses pydub for proper MP3 merging if available,
    falls back to raw byte concatenation otherwise.
    """
    if PYDUB_AVAILABLE:
        combined = AudioSegment.empty()
        for f in audio_files:
            if Path(f).exists():
                combined += AudioSegment.from_mp3(str(f))
        combined.export(str(output_file), format="mp3")
    else:
        # Raw concat fallback (works for most players but not spec-compliant)
        with open(output_file, 'wb') as out:
            for f in audio_files:
                if Path(f).exists():
                    with open(f, 'rb') as seg:
                        out.write(seg.read())

    return output_file
