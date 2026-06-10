@echo off
echo ============================================================
echo    FAL AI AVATAR VIDEO GENERATOR
echo ============================================================
echo.
echo Checking FAL_KEY environment variable...
echo.

if "%FAL_KEY%"=="" (
    echo ❌ ERROR: FAL_KEY not set!
    echo.
    echo Please set your FAL API key:
    echo    set FAL_KEY=your_api_key_here
    echo.
    echo Get your key from: https://fal.ai/dashboard/keys
    echo.
    pause
    exit /b 1
)

echo ✓ FAL_KEY is set
echo.
echo Starting server on http://localhost:5004
echo.
echo Opening browser...
start http://localhost:5004
echo.
echo Server is running! Press Ctrl+C to stop.
echo ============================================================
echo.

python fal_avatar_generator.py
