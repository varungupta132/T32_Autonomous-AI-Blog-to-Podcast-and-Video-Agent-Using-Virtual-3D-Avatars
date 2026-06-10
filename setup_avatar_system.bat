@echo off
echo ========================================
echo  Avatar Video System Setup
echo ========================================
echo.

echo [1/5] Creating directories...
python -c "from pathlib import Path; Path('avatar_assets').mkdir(exist_ok=True); Path('avatar_videos').mkdir(exist_ok=True); Path('temp_avatar').mkdir(exist_ok=True)"
echo ✅ Directories created
echo.

echo [2/5] Checking dependencies...
echo.
echo Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git not found!
    echo Please install from: https://git-scm.com/downloads
    pause
    exit /b 1
) else (
    echo ✅ Git installed
)

echo.
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FFmpeg not found!
    echo Please install from: https://ffmpeg.org/download.html
    pause
    exit /b 1
) else (
    echo ✅ FFmpeg installed
)

echo.
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    pause
    exit /b 1
) else (
    echo ✅ Python installed
)

echo.
echo [3/5] Cloning Wav2Lip repository...
if exist "Wav2Lip" (
    echo ✅ Wav2Lip already exists
) else (
    git clone https://github.com/Rudrabha/Wav2Lip.git
    if %errorlevel% neq 0 (
        echo ❌ Failed to clone Wav2Lip
        pause
        exit /b 1
    )
    echo ✅ Wav2Lip cloned
)

echo.
echo [4/5] Installing Python dependencies...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet
pip install opencv-python librosa numpy scipy --quiet
echo ✅ Dependencies installed

echo.
echo [5/5] Setup instructions...
echo.
echo ========================================
echo  MANUAL STEPS REQUIRED
echo ========================================
echo.
echo 1. Download Wav2Lip Model:
echo    URL: https://github.com/Rudrabha/Wav2Lip
echo    File: wav2lip_gan.pth
echo    Place in: Wav2Lip\checkpoints\wav2lip_gan.pth
echo.
echo 2. Add Face Image:
echo    Place your face photo in: avatar_assets\default_face.jpg
echo    Requirements:
echo    - Front-facing
echo    - Good lighting
echo    - Clear face
echo    - JPG or PNG format
echo.
echo 3. Test the system:
echo    python avatar_video_generator.py --test
echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
pause
