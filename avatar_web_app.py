"""
🎬 AVATAR WEB APP - Full Stack
Upload audio → Get talking avatar video

Uses D-ID API (easiest solution - no local setup needed!)
Browser-based, real-time preview

Author: AI Assistant
Date: March 3, 2026
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import requests
import time
import os
from pathlib import Path
import base64

app = Flask(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# D-ID API Configuration (Free tier available)
# Get your API key from: https://studio.d-id.com/
DID_API_KEY = "YOUR_DID_API_KEY_HERE"  # Replace with your key
DID_API_URL = "https://api.d-id.com"

# Directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("avatar_outputs")
AVATAR_DIR = Path("avatar_faces")

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
AVATAR_DIR.mkdir(exist_ok=True)

# Default avatar image (base64 encoded or URL)
DEFAULT_AVATAR = "https://create-images-results.d-id.com/default_presenter.jpg"


# ============================================================================
# HTML TEMPLATE
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎬 Avatar Video Generator</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
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
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-section {
            background: #f8f9fa;
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s;
        }
        
        .upload-section:hover {
            border-color: #764ba2;
            background: #f0f0f0;
        }
        
        .upload-section.dragover {
            background: #e3f2fd;
            border-color: #2196F3;
        }
        
        .file-input {
            display: none;
        }
        
        .upload-btn {
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
        
        .upload-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .avatar-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .avatar-option {
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            padding: 10px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        
        .avatar-option:hover {
            border-color: #667eea;
            transform: translateY(-5px);
        }
        
        .avatar-option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        }
        
        .avatar-option img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .generate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 50px;
            font-size: 1.2em;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            display: block;
            margin: 30px auto;
            width: 100%;
            max-width: 400px;
        }
        
        .generate-btn:hover {
            transform: translateY(-3px);
        }
        
        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .result {
            display: none;
            margin-top: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        
        .result.active {
            display: block;
        }
        
        .result h2 {
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .video-container {
            background: black;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .video-container video {
            width: 100%;
            display: block;
        }
        
        .download-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            margin: 10px;
        }
        
        .download-btn:hover {
            background: #45a049;
        }
        
        .info-box {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #c62828;
            display: none;
        }
        
        .error.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Avatar Video Generator</h1>
            <p>Upload Audio → Get Talking Avatar Video</p>
            <div class="badge">✨ Powered by D-ID AI</div>
        </div>
        
        <div class="content">
            <!-- Step 1: Upload Audio -->
            <div class="upload-section" id="uploadSection">
                <h2>📤 Step 1: Upload Audio File</h2>
                <p style="margin: 20px 0; color: #666;">
                    Drag & drop or click to upload MP3/WAV file
                </p>
                <input type="file" id="audioFile" class="file-input" accept="audio/*">
                <button class="upload-btn" onclick="document.getElementById('audioFile').click()">
                    📁 Choose Audio File
                </button>
                <div id="audioInfo" style="margin-top: 20px; display: none;">
                    <p><strong>Selected:</strong> <span id="audioName"></span></p>
                    <audio id="audioPreview" controls style="width: 100%; margin-top: 10px;"></audio>
                </div>
            </div>
            
            <!-- Step 2: Choose Avatar -->
            <div style="margin-bottom: 30px;">
                <h2>👤 Step 2: Choose Avatar</h2>
                <div class="avatar-options">
                    <div class="avatar-option selected" data-avatar="default">
                        <img src="https://via.placeholder.com/150/667eea/ffffff?text=Default" alt="Default">
                        <p>Default</p>
                    </div>
                    <div class="avatar-option" data-avatar="male1">
                        <img src="https://via.placeholder.com/150/764ba2/ffffff?text=Male+1" alt="Male 1">
                        <p>Male 1</p>
                    </div>
                    <div class="avatar-option" data-avatar="female1">
                        <img src="https://via.placeholder.com/150/667eea/ffffff?text=Female+1" alt="Female 1">
                        <p>Female 1</p>
                    </div>
                    <div class="avatar-option" data-avatar="male2">
                        <img src="https://via.placeholder.com/150/764ba2/ffffff?text=Male+2" alt="Male 2">
                        <p>Male 2</p>
                    </div>
                </div>
            </div>
            
            <!-- Step 3: Generate -->
            <button class="generate-btn" id="generateBtn" onclick="generateVideo()" disabled>
                ✨ Generate Talking Avatar
            </button>
            
            <!-- Loading -->
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <h3>Generating Your Avatar Video...</h3>
                <p>This may take 30-60 seconds</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill">0%</div>
                </div>
                <p id="statusText" style="margin-top: 10px; color: #666;">Initializing...</p>
            </div>
            
            <!-- Error -->
            <div class="error" id="error"></div>
            
            <!-- Result -->
            <div class="result" id="result">
                <h2>🎉 Your Talking Avatar Video!</h2>
                <div class="info-box">
                    <strong>✅ Video Generated Successfully!</strong><br>
                    Duration: <span id="videoDuration">--</span> seconds
                </div>
                <div class="video-container">
                    <video id="resultVideo" controls autoplay></video>
                </div>
                <div style="text-align: center;">
                    <button class="download-btn" onclick="downloadVideo()">
                        ⬇️ Download Video
                    </button>
                    <button class="upload-btn" onclick="resetForm()">
                        🔄 Create Another
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedAudio = null;
        let selectedAvatar = 'default';
        let videoUrl = null;
        
        // File upload handling
        document.getElementById('audioFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                selectedAudio = file;
                document.getElementById('audioName').textContent = file.name;
                document.getElementById('audioInfo').style.display = 'block';
                
                // Preview audio
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('audioPreview').src = e.target.result;
                };
                reader.readAsDataURL(file);
                
                // Enable generate button
                document.getElementById('generateBtn').disabled = false;
            }
        });
        
        // Drag and drop
        const uploadSection = document.getElementById('uploadSection');
        
        uploadSection.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadSection.classList.add('dragover');
        });
        
        uploadSection.addEventListener('dragleave', function(e) {
            uploadSection.classList.remove('dragover');
        });
        
        uploadSection.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('audio/')) {
                document.getElementById('audioFile').files = e.dataTransfer.files;
                document.getElementById('audioFile').dispatchEvent(new Event('change'));
            }
        });
        
        // Avatar selection
        document.querySelectorAll('.avatar-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
                this.classList.add('selected');
                selectedAvatar = this.dataset.avatar;
            });
        });
        
        // Generate video
        async function generateVideo() {
            if (!selectedAudio) {
                alert('Please upload an audio file first!');
                return;
            }
            
            // Show loading
            document.getElementById('loading').classList.add('active');
            document.getElementById('result').classList.remove('active');
            document.getElementById('error').classList.remove('active');
            document.getElementById('generateBtn').disabled = true;
            
            // Create form data
            const formData = new FormData();
            formData.append('audio', selectedAudio);
            formData.append('avatar', selectedAvatar);
            
            try {
                // Upload and generate
                updateProgress(10, 'Uploading audio...');
                
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                
                updateProgress(30, 'Processing...');
                
                const data = await response.json();
                
                if (data.success) {
                    // Poll for completion
                    await pollVideoStatus(data.video_id);
                } else {
                    throw new Error(data.error || 'Generation failed');
                }
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('loading').classList.remove('active');
                document.getElementById('error').textContent = '❌ Error: ' + error.message;
                document.getElementById('error').classList.add('active');
                document.getElementById('generateBtn').disabled = false;
            }
        }
        
        // Poll video status
        async function pollVideoStatus(videoId) {
            const maxAttempts = 60;
            let attempts = 0;
            
            const poll = async () => {
                attempts++;
                updateProgress(30 + (attempts * 1), `Generating video... (${attempts}s)`);
                
                try {
                    const response = await fetch(`/status/${videoId}`);
                    const data = await response.json();
                    
                    if (data.status === 'done') {
                        updateProgress(100, 'Complete!');
                        showResult(data.video_url, data.duration);
                    } else if (data.status === 'error') {
                        throw new Error(data.error || 'Generation failed');
                    } else if (attempts < maxAttempts) {
                        setTimeout(poll, 1000);
                    } else {
                        throw new Error('Timeout: Video generation took too long');
                    }
                } catch (error) {
                    throw error;
                }
            };
            
            poll();
        }
        
        // Update progress
        function updateProgress(percent, text) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressFill').textContent = Math.round(percent) + '%';
            document.getElementById('statusText').textContent = text;
        }
        
        // Show result
        function showResult(url, duration) {
            document.getElementById('loading').classList.remove('active');
            document.getElementById('result').classList.add('active');
            document.getElementById('resultVideo').src = url;
            document.getElementById('videoDuration').textContent = duration || '--';
            videoUrl = url;
        }
        
        // Download video
        function downloadVideo() {
            if (videoUrl) {
                const a = document.createElement('a');
                a.href = videoUrl;
                a.download = 'avatar_video.mp4';
                a.click();
            }
        }
        
        // Reset form
        function resetForm() {
            selectedAudio = null;
            document.getElementById('audioInfo').style.display = 'none';
            document.getElementById('audioFile').value = '';
            document.getElementById('result').classList.remove('active');
            document.getElementById('generateBtn').disabled = true;
        }
    </script>
</body>
</html>
"""


# ============================================================================
# API FUNCTIONS
# ============================================================================

def create_did_video(audio_file, avatar_image=DEFAULT_AVATAR):
    """
    Create talking avatar video using D-ID API
    
    Args:
        audio_file: Path to audio file
        avatar_image: URL or base64 of avatar image
        
    Returns:
        video_id for polling status
    """
    
    # Read audio file
    with open(audio_file, 'rb') as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')
    
    # D-ID API request
    headers = {
        'Authorization': f'Basic {DID_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'source_url': avatar_image,
        'script': {
            'type': 'audio',
            'audio_url': f'data:audio/mp3;base64,{audio_data}'
        },
        'config': {
            'fluent': True,
            'pad_audio': 0
        }
    }
    
    response = requests.post(
        f'{DID_API_URL}/talks',
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        return response.json()['id']
    else:
        raise Exception(f"D-ID API error: {response.text}")


def get_video_status(video_id):
    """Get video generation status from D-ID"""
    
    headers = {
        'Authorization': f'Basic {DID_API_KEY}'
    }
    
    response = requests.get(
        f'{DID_API_URL}/talks/{video_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        return {
            'status': data['status'],
            'video_url': data.get('result_url'),
            'duration': data.get('duration')
        }
    else:
        return {'status': 'error', 'error': response.text}


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/generate', methods=['POST'])
def generate():
    """Generate avatar video from uploaded audio"""
    
    try:
        # Get uploaded audio
        audio_file = request.files.get('audio')
        avatar = request.form.get('avatar', 'default')
        
        if not audio_file:
            return jsonify({'success': False, 'error': 'No audio file uploaded'})
        
        # Save audio
        audio_path = UPLOAD_DIR / audio_file.filename
        audio_file.save(audio_path)
        
        # Create video with D-ID
        video_id = create_did_video(audio_path)
        
        return jsonify({
            'success': True,
            'video_id': video_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/status/<video_id>')
def status(video_id):
    """Check video generation status"""
    
    try:
        status_data = get_video_status(video_id)
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_DIR, filename)


@app.route('/outputs/<filename>')
def output_file(filename):
    """Serve generated videos"""
    return send_from_directory(OUTPUT_DIR, filename)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 AVATAR VIDEO WEB APP")
    print("="*60)
    print("\n✨ Features:")
    print("   • Upload audio file")
    print("   • Choose avatar")
    print("   • Get lip-synced video")
    print("   • Download result")
    print("\n🌐 Open: http://localhost:5000")
    print("\n⚠️  Note: You need D-ID API key")
    print("   Get it from: https://studio.d-id.com/")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
