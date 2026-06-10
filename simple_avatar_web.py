"""
🎬 SIMPLE AVATAR WEB APP
Upload audio → See animated avatar talking
100% FREE - No API needed!

Uses browser-based animation with default avatars
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
from pathlib import Path
import base64
import json

app = Flask(__name__)

# Directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ============================================================================
# HTML TEMPLATE WITH ANIMATED AVATARS
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎬 Animated Avatar</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 10px;
        }
        
        .content { padding: 40px; }
        
        .avatar-display {
            background: #000;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        .avatar-container {
            position: relative;
            width: 300px;
            height: 300px;
        }
        
        .avatar-face {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 120px;
            animation: idle 3s ease-in-out infinite;
        }
        
        .avatar-face.talking {
            animation: talking 0.3s ease-in-out infinite;
        }
        
        @keyframes idle {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        @keyframes talking {
            0%, 100% { transform: scale(1) translateY(0); }
            50% { transform: scale(1.05) translateY(-5px); }
        }
        
        .avatar-mouth {
            position: absolute;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 30px;
            background: #333;
            border-radius: 0 0 30px 30px;
            transition: all 0.1s;
        }
        
        .avatar-mouth.talking {
            height: 40px;
            animation: mouth 0.2s ease-in-out infinite;
        }
        
        @keyframes mouth {
            0%, 100% { height: 30px; }
            50% { height: 45px; }
        }
        
        .avatar-eyes {
            position: absolute;
            top: 100px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 40px;
        }
        
        .eye {
            width: 20px;
            height: 20px;
            background: #333;
            border-radius: 50%;
            animation: blink 4s ease-in-out infinite;
        }
        
        @keyframes blink {
            0%, 98%, 100% { height: 20px; }
            99% { height: 2px; }
        }
        
        .upload-section {
            background: #f8f9fa;
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .file-input { display: none; }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            margin: 10px;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .avatar-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .avatar-option {
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            padding: 15px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
            font-size: 50px;
        }
        
        .avatar-option:hover {
            border-color: #667eea;
            transform: translateY(-5px);
        }
        
        .avatar-option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        }
        
        .status {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 1.1em;
        }
        
        .waveform {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 3px;
            height: 50px;
            align-items: flex-end;
        }
        
        .wave-bar {
            width: 4px;
            background: rgba(255,255,255,0.5);
            border-radius: 2px;
            animation: wave 0.5s ease-in-out infinite;
        }
        
        @keyframes wave {
            0%, 100% { height: 10px; }
            50% { height: 40px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Animated Avatar</h1>
            <p>Upload Audio → See Avatar Talk</p>
            <div class="badge">✨ 100% Free - No API Needed</div>
        </div>
        
        <div class="content">
            <!-- Avatar Display -->
            <div class="avatar-display">
                <div class="avatar-container">
                    <div class="avatar-face" id="avatarFace">
                        <span id="avatarEmoji">😊</span>
                    </div>
                    <div class="avatar-eyes">
                        <div class="eye"></div>
                        <div class="eye"></div>
                    </div>
                    <div class="avatar-mouth" id="avatarMouth"></div>
                    
                    <!-- Waveform -->
                    <div class="waveform" id="waveform" style="display: none;">
                        <div class="wave-bar" style="animation-delay: 0s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.1s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.2s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.3s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.4s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.3s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.2s;"></div>
                        <div class="wave-bar" style="animation-delay: 0.1s;"></div>
                    </div>
                </div>
            </div>
            
            <!-- Status -->
            <div class="status" id="status">
                👋 Choose an avatar and upload audio to start!
            </div>
            
            <!-- Avatar Selector -->
            <div class="avatar-selector">
                <div class="avatar-option selected" data-emoji="😊" onclick="selectAvatar('😊')">
                    😊<br><small>Happy</small>
                </div>
                <div class="avatar-option" data-emoji="🤖" onclick="selectAvatar('🤖')">
                    🤖<br><small>Robot</small>
                </div>
                <div class="avatar-option" data-emoji="👨" onclick="selectAvatar('👨')">
                    👨<br><small>Man</small>
                </div>
                <div class="avatar-option" data-emoji="👩" onclick="selectAvatar('👩')">
                    👩<br><small>Woman</small>
                </div>
                <div class="avatar-option" data-emoji="🧑‍💼" onclick="selectAvatar('🧑‍💼')">
                    🧑‍💼<br><small>Professional</small>
                </div>
                <div class="avatar-option" data-emoji="👽" onclick="selectAvatar('👽')">
                    👽<br><small>Alien</small>
                </div>
            </div>
            
            <!-- Upload Section -->
            <div class="upload-section">
                <h3>📤 Upload Audio File</h3>
                <p style="margin: 15px 0; color: #666;">MP3, WAV, or any audio format</p>
                <input type="file" id="audioFile" class="file-input" accept="audio/*">
                <button class="btn" onclick="document.getElementById('audioFile').click()">
                    📁 Choose Audio File
                </button>
            </div>
            
            <!-- Controls -->
            <div class="controls">
                <button class="btn" id="playBtn" onclick="playAudio()" disabled>
                    ▶️ Play
                </button>
                <button class="btn" id="pauseBtn" onclick="pauseAudio()" disabled style="display: none;">
                    ⏸️ Pause
                </button>
                <button class="btn" id="stopBtn" onclick="stopAudio()" disabled>
                    ⏹️ Stop
                </button>
            </div>
            
            <!-- Hidden audio element -->
            <audio id="audioPlayer" style="display: none;"></audio>
        </div>
    </div>
    
    <script>
        let audioPlayer = document.getElementById('audioPlayer');
        let avatarFace = document.getElementById('avatarFace');
        let avatarMouth = document.getElementById('avatarMouth');
        let waveform = document.getElementById('waveform');
        let selectedEmoji = '😊';
        let audioContext = null;
        let analyser = null;
        
        // Select avatar
        function selectAvatar(emoji) {
            selectedEmoji = emoji;
            document.getElementById('avatarEmoji').textContent = emoji;
            
            // Update selected state
            document.querySelectorAll('.avatar-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            event.target.closest('.avatar-option').classList.add('selected');
        }
        
        // File upload
        document.getElementById('audioFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const url = URL.createObjectURL(file);
                audioPlayer.src = url;
                
                document.getElementById('status').textContent = '✅ Audio loaded: ' + file.name;
                document.getElementById('playBtn').disabled = false;
                document.getElementById('stopBtn').disabled = false;
            }
        });
        
        // Play audio
        function playAudio() {
            audioPlayer.play();
            startTalking();
            
            document.getElementById('playBtn').style.display = 'none';
            document.getElementById('pauseBtn').style.display = 'inline-block';
            document.getElementById('pauseBtn').disabled = false;
            document.getElementById('status').textContent = '🎤 Avatar is talking...';
        }
        
        // Pause audio
        function pauseAudio() {
            audioPlayer.pause();
            stopTalking();
            
            document.getElementById('playBtn').style.display = 'inline-block';
            document.getElementById('pauseBtn').style.display = 'none';
            document.getElementById('status').textContent = '⏸️ Paused';
        }
        
        // Stop audio
        function stopAudio() {
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            stopTalking();
            
            document.getElementById('playBtn').style.display = 'inline-block';
            document.getElementById('pauseBtn').style.display = 'none';
            document.getElementById('status').textContent = '⏹️ Stopped';
        }
        
        // Start talking animation
        function startTalking() {
            avatarFace.classList.add('talking');
            avatarMouth.classList.add('talking');
            waveform.style.display = 'flex';
        }
        
        // Stop talking animation
        function stopTalking() {
            avatarFace.classList.remove('talking');
            avatarMouth.classList.remove('talking');
            waveform.style.display = 'none';
        }
        
        // Audio ended
        audioPlayer.addEventListener('ended', function() {
            stopAudio();
            document.getElementById('status').textContent = '✅ Finished!';
        });
        
        // Drag and drop
        const uploadSection = document.querySelector('.upload-section');
        
        uploadSection.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#764ba2';
            this.style.background = '#e3f2fd';
        });
        
        uploadSection.addEventListener('dragleave', function(e) {
            this.style.borderColor = '#667eea';
            this.style.background = '#f8f9fa';
        });
        
        uploadSection.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#667eea';
            this.style.background = '#f8f9fa';
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('audio/')) {
                document.getElementById('audioFile').files = e.dataTransfer.files;
                document.getElementById('audioFile').dispatchEvent(new Event('change'));
            }
        });
    </script>
</body>
</html>
"""


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_DIR, filename)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 SIMPLE ANIMATED AVATAR WEB APP")
    print("="*60)
    print("\n✨ Features:")
    print("   • Upload any audio file")
    print("   • Choose from 6 animated avatars")
    print("   • See avatar talk with lip-sync animation")
    print("   • 100% FREE - No API needed!")
    print("   • Works completely in browser")
    print("\n🌐 Starting server...")
    print("   Open: http://localhost:5000")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, port=5000)
