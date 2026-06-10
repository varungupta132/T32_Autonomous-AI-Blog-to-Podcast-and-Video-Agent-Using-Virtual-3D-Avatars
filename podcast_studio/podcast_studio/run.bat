@echo off
echo.
echo  ==========================================
echo   PODCAST STUDIO + AVATAR VIDEO
echo  ==========================================
echo   Starting server...
echo   Open: http://localhost:8080
echo.
echo   FEATURES:
echo   - AI Script Generation (OpenRouter)
echo   - Text-to-Speech (EdgeTTS, 60+ languages)
echo   - Avatar Video (Wav2Lip, FREE + local)
echo  ==========================================
echo.
cd /d "%~dp0"
python app.py
pause
