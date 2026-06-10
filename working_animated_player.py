"""
🎬 Working Animated Podcast Player
Simple, reliable avatar animation without complex dependencies
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import os

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('working_player.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        file = request.files['audio']
        filename = f"podcast_{os.urandom(4).hex()}.mp3"
        filepath = UPLOAD_DIR / filename
        file.save(filepath)
        
        print(f"✓ Audio uploaded: {filename}")
        
        return jsonify({
            "success": True,
            "audio_url": f"/uploads/{filename}",
            "message": "Audio uploaded successfully!"
        })
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_file(UPLOAD_DIR / filename)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 WORKING ANIMATED PODCAST PLAYER")
    print("="*60)
    print("\n🚀 Server: http://localhost:5003")
    print("✨ Features:")
    print("   • Upload any audio file")
    print("   • Animated 3D avatars")
    print("   • Auto speaker detection")
    print("   • Live playback")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
