"""
Simple Animated Podcast Player - Working Version
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import os

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('simple_player.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        file = request.files['audio']
        filename = f"podcast_{os.urandom(4).hex()}.mp3"
        filepath = UPLOAD_DIR / filename
        file.save(filepath)
        
        return jsonify({
            "success": True,
            "audio_url": f"/uploads/{filename}",
            "message": "Audio uploaded successfully!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_file(UPLOAD_DIR / filename)

if __name__ == '__main__':
    print("\n🎬 Simple Animated Player - http://localhost:5002\n")
    app.run(debug=True, host='0.0.0.0', port=5002)
