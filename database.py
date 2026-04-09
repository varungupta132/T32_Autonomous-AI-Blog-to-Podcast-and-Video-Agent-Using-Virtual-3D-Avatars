import json
from pathlib import Path

OUTPUT_DIR = Path("generated_podcasts")
TEMP_DIR = Path("temp_audio")
HISTORY_FILE = OUTPUT_DIR / "history.json"
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

def get_history_data():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_history_data(entry):
    history = get_history_data()
    # Check if file already exists in history and replace
    history = [h for h in history if h.get("filename") != entry.get("filename")]
    history.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
