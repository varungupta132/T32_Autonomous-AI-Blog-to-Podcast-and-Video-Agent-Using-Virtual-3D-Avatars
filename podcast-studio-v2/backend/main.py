"""
Podcast Studio v2 — Production-ready Flask backend
Fixes from code review:
  - API key in .env (not hardcoded)
  - Input validation + length limits
  - Rate limiting (Flask-Limiter)
  - SQLite database for podcast history
  - Proper MP3 merging via pydub
  - Structured services (llm / tts / merger)
  - Error handling throughout
  - Security headers via Flask-Talisman (optional)
"""

import re
import time
import traceback
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import (
    OUTPUT_DIR, TEMP_DIR, MAX_BLOG_LENGTH, RATE_LIMIT_PER_MINUTE, SECRET_KEY
)
from models.database import init_db, SessionLocal, Podcast
from services.llm_service import generate_ai_podcast
from services.tts_service import parse_script, detect_speakers, generate_all_segments
from services.audio_merger import merge_audio_files

# ── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__, template_folder="../frontend/templates")
app.secret_key = SECRET_KEY

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[f"{RATE_LIMIT_PER_MINUTE} per minute"],
    storage_uri="memory://",
)

# Initialise DB on startup
init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_name(name: str) -> str:
    return re.sub(r'[^\w\-_]', '_', name)[:80]


def _validate_content(content: str) -> str | None:
    """Return error string if invalid, else None."""
    if not content or not content.strip():
        return "Content is required."
    if len(content) > MAX_BLOG_LENGTH:
        return f"Content too long. Max {MAX_BLOG_LENGTH} characters."
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ai-generate', methods=['POST'])
@limiter.limit("10 per minute")
def ai_generate():
    data = request.get_json(silent=True) or {}
    content = data.get('content', '').strip()
    title   = data.get('title', '').strip()[:200]
    ptype   = data.get('podcast_type', 'single')
    audience = data.get('audience', 'global')

    err = _validate_content(content)
    if err:
        return jsonify({"error": err}), 400

    if ptype not in ('single', 'co-host', 'multi-host'):
        return jsonify({"error": "Invalid podcast_type"}), 400
    if audience not in ('global', 'indian'):
        return jsonify({"error": "Invalid audience"}), 400

    result = generate_ai_podcast(content, title, ptype, audience)
    if not result['success']:
        return jsonify({"error": result['error']}), 500

    return jsonify({"success": True, "script": result['script'], "type": ptype, "audience": audience})


@app.route('/api/analyze', methods=['POST'])
def analyze_script_route():
    data = request.get_json(silent=True) or {}
    script = data.get('script', '').strip()
    if not script:
        return jsonify({"error": "No script provided"}), 400

    dialogues = parse_script(script)
    if not dialogues:
        return jsonify({"error": "No valid dialogues found. Format: Speaker: Dialogue"}), 400

    speaker_voices = detect_speakers(dialogues)
    return jsonify({
        "success": True,
        "total_dialogues": len(dialogues),
        "speakers": len(speaker_voices),
        "speaker_info": {
            spk: {"voice": info["voice_info"]["name"], "engine": "Microsoft EdgeTTS (FREE)"}
            for spk, info in speaker_voices.items()
        },
    })


@app.route('/api/generate', methods=['POST'])
@limiter.limit("5 per minute")
def generate_podcast():
    data = request.get_json(silent=True) or {}
    script = data.get('script', '').strip()
    raw_name = data.get('name', f'podcast_{int(time.time())}')
    podcast_name = _safe_name(raw_name)

    if not script:
        return jsonify({"error": "No script provided"}), 400

    dialogues = parse_script(script)
    if not dialogues:
        return jsonify({"error": "No valid dialogues found"}), 400

    speaker_voices = detect_speakers(dialogues)

    # Build task list for batch generation
    tasks = [
        {
            "index": i,
            "speaker": d["speaker"],
            "text": d["text"],
            "output_path": TEMP_DIR / f"{podcast_name}_seg_{i:03d}_{d['speaker']}.mp3",
            "voice_info": speaker_voices[d["speaker"]]["voice_info"],
        }
        for i, d in enumerate(dialogues)
    ]

    # Generate all segments in one asyncio.run() call — avoids threading/DNS issues
    try:
        emotions = generate_all_segments(tasks)
    except Exception as e:
        import sys
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

    # Verify all files exist
    audio_files = []
    progress_data = []
    for i, task in enumerate(tasks):
        if task["output_path"].exists():
            audio_files.append(task["output_path"])
            progress_data.append({
                "index": i + 1,
                "speaker": task["speaker"],
                "emotion": emotions[i],
                "text": task["text"][:60] + ("..." if len(task["text"]) > 60 else ""),
            })
        else:
            return jsonify({"error": f"Segment {i+1} ({task['speaker']}) failed to generate"}), 500

    output_file = OUTPUT_DIR / f"{podcast_name}.mp3"
    try:
        merge_audio_files(audio_files, output_file)
    except Exception as e:
        return jsonify({"error": f"Merge failed: {e}"}), 500
    finally:
        for f in audio_files:
            try:
                Path(f).unlink(missing_ok=True)
            except Exception:
                pass

    if not output_file.exists():
        return jsonify({"error": "Output file missing after merge"}), 500

    file_size_mb = round(output_file.stat().st_size / 1024 / 1024, 2)
    progress_data.sort(key=lambda x: x["index"])
    # Persist to DB
    db = SessionLocal()
    try:
        record = Podcast(
            name=podcast_name,
            podcast_type=data.get('podcast_type', 'unknown'),
            audience=data.get('audience', 'unknown'),
            script=script,
            filename=output_file.name,
            file_size_mb=file_size_mb,
            total_segments=len(audio_files),
            speakers=len(speaker_voices),
            status="done",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    except Exception:
        record_id = None
    finally:
        db.close()

    return jsonify({
        "success": True,
        "id": record_id,
        "filename": output_file.name,
        "file_size": f"{file_size_mb} MB",
        "total_segments": len(audio_files),
        "speakers": len(speaker_voices),
        "progress": progress_data,
    })


@app.route('/api/history')
def get_history():
    db = SessionLocal()
    try:
        records = db.query(Podcast).order_by(Podcast.created_at.desc()).limit(50).all()
        return jsonify([
            {
                "id": r.id,
                "name": r.name,
                "title": r.title,
                "type": r.podcast_type,
                "audience": r.audience,
                "filename": r.filename,
                "file_size": f"{r.file_size_mb} MB" if r.file_size_mb else "—",
                "segments": r.total_segments,
                "speakers": r.speakers,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
                "status": r.status,
            }
            for r in records
        ])
    finally:
        db.close()


@app.route('/api/stream/<filename>')
def stream_podcast(filename):
    # Prevent path traversal
    filename = Path(filename).name
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, mimetype='audio/mpeg')


@app.route('/api/download/<filename>')
def download_podcast(filename):
    filename = Path(filename).name
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)


@app.route('/api/delete/<int:podcast_id>', methods=['DELETE'])
def delete_podcast(podcast_id):
    db = SessionLocal()
    try:
        record = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not record:
            return jsonify({"error": "Not found"}), 404
        # Delete file
        if record.filename:
            fp = OUTPUT_DIR / record.filename
            fp.unlink(missing_ok=True)
        db.delete(record)
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route('/api/voices')
def get_voices():
    from config import VOICE_LIBRARY
    return jsonify({
        "voices": [
            {"key": k, "name": v["name"], "voice_id": v["voice"]}
            for k, v in VOICE_LIBRARY.items()
        ]
    })


@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({"error": "Too many requests. Please slow down."}), 429


@app.errorhandler(500)
def internal_error(e):
    traceback.print_exc()
    return jsonify({"error": "Internal server error"}), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Podcast Studio v2")
    print("=" * 60)
    print("  http://localhost:8080")
    print("=" * 60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=8080)
