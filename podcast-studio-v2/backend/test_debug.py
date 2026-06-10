import sys
sys.path.insert(0, '.')
from services.tts_service import parse_script, detect_speakers, generate_all_segments
from pathlib import Path

script = "Alex: Hello world!\nSam: Hi there!"
dialogues = parse_script(script)
speakers = detect_speakers(dialogues)

Path("temp_audio").mkdir(exist_ok=True)
tasks = [
    {
        "index": i,
        "speaker": d["speaker"],
        "text": d["text"],
        "output_path": Path("temp_audio") / f"dbg_{i}.mp3",
        "voice_info": speakers[d["speaker"]]["voice_info"],
    }
    for i, d in enumerate(dialogues)
]

print("Tasks:", [(t["speaker"], str(t["output_path"])) for t in tasks])
emotions = generate_all_segments(tasks)
print("Emotions:", emotions)
for t in tasks:
    exists = t["output_path"].exists()
    size = t["output_path"].stat().st_size if exists else 0
    print(f"  {t['output_path']}: exists={exists}, size={size}")
