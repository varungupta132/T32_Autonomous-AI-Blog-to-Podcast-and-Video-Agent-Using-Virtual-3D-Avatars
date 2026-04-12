import os
import re
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import OUTPUT_DIR, TEMP_DIR, get_history_data, save_history_data
from ai_generator import generate_ai_podcast
from tts_engine import (
    parse_script, detect_speakers, generate_audio_segment, 
    merge_audio_files, VOICE_LIBRARY
)
from avatar import generate_did_video
from video_generator import merge_avatar_videos, merge_avatar_videos_batched
from utils import get_audio_duration
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ai-generate', methods=['POST'])
def ai_generate():
    try:
        data = request.json
        content = data.get('content', '')
        title = data.get('title', '')
        ptype = data.get('podcast_type', 'single')
        audience = data.get('audience', 'global')
        openrouter_api_key = data.get('openrouter_api_key', '').replace('\u2013', '-').replace('\u2014', '-')
        
        if not content:
            return jsonify({"error": "No content provided"}), 400
            
        result = generate_ai_podcast(content, title, ptype, audience, openrouter_api_key)
        if result['success']:
            return jsonify({
                "success": True,
                "script": result['script'],
                "type": ptype,
                "audience": audience
            })
        return jsonify({"error": result.get('error', 'Unknown error')}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_script():
    try:
        data = request.json
        script = data.get('script', '')
        language = data.get('language', 'global')
        
        if not script:
            return jsonify({"error": "No script provided"}), 400
            
        dialogues = parse_script(script)
        if not dialogues:
            return jsonify({"error": "No valid dialogues found."}), 400
            
        speaker_voices = detect_speakers(dialogues, language)
        voices_for_lang = VOICE_LIBRARY.get(language, VOICE_LIBRARY["global"])
        
        return jsonify({
            "success": True,
            "total_dialogues": len(dialogues),
            "speakers": len(speaker_voices),
            "speaker_info": {
                speaker: {
                    "voice": info["voice_info"]["name"],
                    "voice_key": info["voice_key"],
                    "engine": "Microsoft EdgeTTS (FREE)"
                }
                for speaker, info in speaker_voices.items()
            },
            "available_voices": voices_for_lang,
            "dialogues": dialogues
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_podcast():
    try:
        data = request.json
        script = data.get('script', '')
        title = data.get('title', 'Untitled Podcast')
        language = data.get('language', 'global')
        bg_music = data.get('bg_music', 'none')
        emotion_overrides = data.get('emotion_overrides', {})
        voice_overrides = data.get('voice_overrides', {})
        podcast_name = data.get('name', f'podcast_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        podcast_name = re.sub(r'[^\w\-_]', '_', podcast_name)
        if not script: return jsonify({"error": "No script provided"}), 400
        
        dialogues = parse_script(script)
        if not dialogues: return jsonify({"error": "No valid dialogues found"}), 400
            
        speaker_voices = detect_speakers(dialogues, language)
        tasks = []
        all_voices = VOICE_LIBRARY.get(language, VOICE_LIBRARY["global"])
        voice_dict = {v["voice"]: v for v in all_voices}
        
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue["speaker"]
            text = dialogue["text"]
            output_path = TEMP_DIR / f"{podcast_name}_seg_{i:03d}_{speaker}.mp3"
            
            speaker_voice_config = speaker_voices[speaker]
            if speaker in voice_overrides:
                override_key = voice_overrides[speaker]
                if override_key in voice_dict:
                    speaker_voice_config = {
                        "voice_key": override_key,
                        "voice_info": {**voice_dict[override_key], "rate": "+0%", "pitch": "+0Hz"}
                    }
            tasks.append({
                "index": i, "speaker": speaker, "text": text, "output_path": output_path,
                "voice": speaker_voice_config, "emotion_override": emotion_overrides.get(speaker, "auto")
            })
            
        audio_files = [None] * len(tasks)
        progress_data = []

        def worker(task):
            try:
                _, emotion = generate_audio_segment(task["voice"], task["text"], task["output_path"], task.get("emotion_override", "auto"))
                if task["output_path"].exists():
                    return {"success": True, "index": task["index"], "path": task["output_path"], "speaker": task["speaker"], "emotion": emotion, "text": task["text"]}
                return {"success": False, "index": task["index"], "error": "File not created"}
            except Exception as e:
                return {"success": False, "index": task["index"], "error": str(e)}

        max_workers = min(len(tasks), 8)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(worker, task): task for task in tasks}
            for future in as_completed(future_to_task):
                res = future.result()
                if res["success"]:
                    idx = res["index"]
                    audio_files[idx] = res["path"]
                    progress_data.append({
                        "index": idx + 1, "speaker": res["speaker"], "emotion": res["emotion"],
                        "text": res["text"][:60] + "..." if len(res["text"]) > 60 else res["text"]
                    })
                else:
                    return jsonify({"error": f"Failed segment {res['index']+1}"}), 500
                    
        audio_files = [f for f in audio_files if f is not None]
        output_file = OUTPUT_DIR / f"{podcast_name}.mp3"
        merge_audio_files(audio_files, output_file, bg_music if bg_music != "none" else None)
        
        for file in audio_files:
            try:
                if file.exists(): file.unlink()
            except: pass
            
        history_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "title": title,
            "filename": output_file.name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "script": script
        }
        save_history_data(history_entry)
        
        progress_data.sort(key=lambda x: x["index"])
        return jsonify({
            "success": True, "filename": output_file.name,
            "file_size": f"{output_file.stat().st_size / 1024 / 1024:.2f} MB",
            "total_segments": len(audio_files), "speakers": len(speaker_voices), "progress": progress_data
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-video', methods=['POST'])
def generate_podcast_video():
    try:
        data = request.json
        script = data.get('script', '')
        title = data.get('title', 'Untitled Video Podcast')
        language = data.get('language', 'global')
        bg_music = data.get('bg_music', 'none')
        emotion_overrides = data.get('emotion_overrides', {})
        voice_overrides = data.get('voice_overrides', {})
        did_api_key = data.get('did_api_key', '').replace('\u2013', '-').replace('\u2014', '-')
        avatar_mapping = data.get('avatar_mapping', {})
        fast_mode = data.get('fast_mode', False)
        
        podcast_name = data.get('name', f'podcast_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        podcast_name = re.sub(r'[^\w\-_]', '_', podcast_name)
        
        if not did_api_key: return jsonify({"error": "D-ID API Key is required for video generation"}), 400
        if not script: return jsonify({"error": "No script provided"}), 400
        
        dialogues = parse_script(script)
        if not dialogues: return jsonify({"error": "No valid dialogues found"}), 400
            
        speaker_voices = detect_speakers(dialogues, language)
        tasks = []
        all_voices = VOICE_LIBRARY.get(language, VOICE_LIBRARY["global"])
        voice_dict = {v["voice"]: v for v in all_voices}
        
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue["speaker"]
            text = dialogue["text"]
            output_path = TEMP_DIR / f"{podcast_name}_seg_{i:03d}_{speaker}.mp3"
            
            speaker_voice_config = speaker_voices[speaker]
            if speaker in voice_overrides:
                override_key = voice_overrides[speaker]
                if override_key in voice_dict:
                    speaker_voice_config = {
                        "voice_key": override_key,
                        "voice_info": {**voice_dict[override_key], "rate": "+0%", "pitch": "+0Hz"}
                    }
                    
            avatar_img_url = avatar_mapping.get(speaker, "")
            
            tasks.append({
                "index": i, "speaker": speaker, "text": text, "output_path": output_path,
                "voice": speaker_voice_config, "emotion_override": emotion_overrides.get(speaker, "auto"),
                "avatar_img_url": avatar_img_url
            })
            
        # --- STEP 1: Generate All Audio Segments ---
        audio_tasks = []
        for i, task in enumerate(tasks):
            audio_tasks.append(task)
            
        progress_data = []
        print(f"Generating {len(audio_tasks)} audio segments...")
        with ThreadPoolExecutor(max_workers=8) as executor:
            def audio_worker(t):
                path, emotion = generate_audio_segment(t["voice"], t["text"], t["output_path"], t.get("emotion_override", "auto"))
                duration = get_audio_duration(path)
                return {"index": t["index"], "path": path, "duration": duration, "speaker": t["speaker"]}
            
            audio_results = list(executor.map(audio_worker, audio_tasks))
        
        audio_results.sort(key=lambda x: x["index"])
        
        # --- STEP 2: Group by Speaker and Create Batches ---
        speaker_batches = {} # { "Alex": [ { "combined_paths": [], "duration": 0 } ] }
        for res in audio_results:
            speaker = res["speaker"]
            if speaker not in speaker_batches:
                speaker_batches[speaker] = [{"combined_paths": [], "duration": 0}]
            
            # Check if adding this segment exceeds 60s (to stay safe for D-ID trials)
            current_batch = speaker_batches[speaker][-1]
            if current_batch["duration"] + res["duration"] > 58: # 58s buffer
                speaker_batches[speaker].append({"combined_paths": [], "duration": 0})
                current_batch = speaker_batches[speaker][-1]
            
            current_batch["combined_paths"].append(str(res["path"]))
            current_batch["duration"] += res["duration"]

        # --- STEP 3: Generate Batch Videos via D-ID ---
        batch_tasks = []
        from tts_engine import merge_audio_files
        for speaker, batches in speaker_batches.items():
            avatar_url = avatar_mapping.get(speaker, "https://create-images-results.d-id.com/api_docs/assets/noelle.jpeg")
            for b_idx, batch in enumerate(batches):
                batch_path = TEMP_DIR / f"{podcast_name}_batch_{speaker}_{b_idx}.mp3"
                # Use the existing merge_audio_files from tts_engine instead of pydub directly
                merge_audio_files(batch["combined_paths"], batch_path)
                batch_tasks.append({
                    "speaker": speaker, "audio_path": batch_path, "avatar_url": avatar_url, 
                    "batch_obj": batch, "fast_mode": fast_mode
                })

        print(f"Starting {len(batch_tasks)} batched D-ID calls (Major Optimization)...")
        video_batch_results = []
        with ThreadPoolExecutor(max_workers=min(len(batch_tasks), 10)) as executor:
            def video_worker(bt):
                vid_url = generate_did_video(str(bt["audio_path"]), bt["avatar_url"], did_api_key, fast_mode=bt["fast_mode"])
                return {"speaker": bt["speaker"], "vid_url": vid_url, "batch_obj": bt["batch_obj"]}
            
            video_batch_results = list(executor.map(video_worker, batch_tasks))

        # --- STEP 4: Assembly (Slice and Stitch) ---
        # Map back results to segments
        speaker_video_sequences = {} # { "Alex": [vid_url1, vid_url2] }
        for res in video_batch_results:
            s = res["speaker"]
            if s not in speaker_video_sequences: speaker_video_sequences[s] = []
            speaker_video_sequences[s].append(res["vid_url"])

        output_file = OUTPUT_DIR / f"{podcast_name}.mp4"
        from tts_engine import BGM_DIR
        bg_music_path = BGM_DIR / f"{bg_music}.mp3" if bg_music != "none" else None
        
        # Prepare dialogue segments metadata for the assembler
        dialogue_metadata = [
            {"speaker": res["speaker"], "duration": res["duration"]}
            for res in audio_results
        ]
        
        merge_avatar_videos_batched(speaker_video_sequences, dialogue_metadata, output_file, str(bg_music_path) if bg_music_path else None)

        # Cleanup
        for res in audio_results:
            try: res["path"].unlink()
            except: pass
        for bt in batch_tasks:
            try: bt["audio_path"].unlink()
            except: pass

        history_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "title": title + " [BATC-VIDEO]",
            "filename": output_file.name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "script": script
        }
        save_history_data(history_entry)
        
        return jsonify({
            "success": True, "filename": output_file.name,
            "file_size": f"{output_file.stat().st_size / 1024 / 1024:.2f} MB",
            "total_segments": len(audio_results), "mode": "speaker_batching"
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream/<filename>')
def stream_podcast(filename):
    file_path = OUTPUT_DIR / filename
    if file_path.exists(): return send_file(file_path, mimetype='audio/mpeg')
    return jsonify({"error": "File not found"}), 404

@app.route('/api/download/<filename>')
def download_podcast(filename):
    file_path = OUTPUT_DIR / filename
    if file_path.exists(): return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_podcast(filename):
    try:
        import json
        from database import HISTORY_FILE
        if ".." in filename or "/" in filename or "\\" in filename: return jsonify({"error": "Invalid filename"}), 400
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            file_path.unlink()
            history = get_history_data()
            history = [h for h in history if h.get("filename") != filename]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
            return jsonify({"success": True})
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history():
    try:
        history_data = get_history_data()
        files = []
        if OUTPUT_DIR.exists():
            for file in OUTPUT_DIR.glob('*.mp3'):
                metadata = next((item for item in history_data if item["filename"] == file.name), {})
                files.append({
                    "filename": file.name,
                    "title": metadata.get("title", file.name),
                    "script": metadata.get("script", "No script available."),
                    "size": f"{file.stat().st_size / 1024 / 1024:.2f} MB",
                    "created_raw": file.stat().st_mtime,
                    "created": metadata.get("date", datetime.fromtimestamp(file.stat().st_mtime).strftime("%d %b %Y, %H:%M"))
                })
        files.sort(key=lambda x: x["created_raw"], reverse=True)
        return jsonify({"success": True, "podcasts": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voices')
def get_voices():
    return jsonify({"voices": VOICE_LIBRARY})

if __name__ == '__main__':
    print("============================================================")
    print("Modularized Podcast Studio Server")
    print("============================================================")
    print("Starting app.py server at http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
