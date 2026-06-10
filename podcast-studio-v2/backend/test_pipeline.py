"""Quick end-to-end test: TTS + merge pipeline"""
import sys
sys.path.insert(0, '.')

from services.tts_service import parse_script, detect_speakers, generate_segment
from services.audio_merger import merge_audio_files
from pathlib import Path

SCRIPT = """Alex: Welcome everyone to our AI podcast today!
Sam: Thanks Alex! I am really excited to discuss artificial intelligence.
Alex: AI is transforming every industry from healthcare to education.
Sam: Absolutely! The possibilities are truly endless and exciting.
Alex: Thanks for joining us today everyone, see you next time!
Sam: Goodbye everyone, take care!"""

dialogues = parse_script(SCRIPT)
speakers = detect_speakers(dialogues)
print(f"Parsed {len(dialogues)} lines, {len(speakers)} speakers: {list(speakers.keys())}")

Path("temp_audio").mkdir(exist_ok=True)
Path("generated_podcasts").mkdir(exist_ok=True)

audio_files = []
for i, d in enumerate(dialogues):
    out = Path("temp_audio") / f"test_seg_{i:03d}.mp3"
    emotion = generate_segment(speakers[d["speaker"]]["voice_info"], d["text"], out)
    size = out.stat().st_size
    print(f"  [{i+1}] {d['speaker']} ({emotion}) -> {size} bytes")
    audio_files.append(out)

out_file = Path("generated_podcasts") / "test_output.mp3"
merge_audio_files(audio_files, out_file)
kb = out_file.stat().st_size / 1024
print(f"\nMerged -> {out_file} ({kb:.1f} KB)")

for f in audio_files:
    f.unlink(missing_ok=True)

print("Pipeline OK!")
