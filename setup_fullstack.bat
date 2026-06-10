@echo off
echo ========================================
echo  AI Podcast Generator - Full Stack Setup
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd ai-blog-podcast\backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Backend installation failed!
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed
echo.

echo [2/4] Installing Frontend Dependencies...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Frontend installation failed!
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
echo.

echo [3/4] Creating required directories...
cd ..\backend
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp
echo ✅ Directories created
echo.

echo [4/4] Verifying FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: FFmpeg not found!
    echo Please install FFmpeg for audio processing
    echo Download from: https://ffmpeg.org/download.html
) else (
    echo ✅ FFmpeg is installed
)
echo.

echo ========================================
echo  Setup Complete! 🎉
echo ========================================
echo.
echo Next steps:
echo 1. Start Backend:  cd ai-blog-podcast\backend ^&^& uvicorn main:app --reload
echo 2. Start Frontend: cd ai-blog-podcast\frontend ^&^& npm run dev
echo 3. Open browser:   http://localhost:5173
echo.
echo Read FULLSTACK_AUDIO_GUIDE.md for detailed instructions
echo.
pause
