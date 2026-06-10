@echo off
echo ============================================================
echo    COMPLETE ANIMATED PODCAST SYSTEM
echo ============================================================
echo.
echo Starting all servers...
echo.

REM Set FAL API Key
set FAL_KEY=5ac95634-d396-44b1-b09b-6378d408be22:6f35f18c9e54d1655084c7886fe7859a

echo [1/3] Starting Podcast Studio (Port 8080)...
start "Podcast Studio" cmd /k "python interactive_podcast_studio.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Animated Player (Port 5003)...
start "Animated Player" cmd /k "python working_animated_player.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting FAL Avatar Generator (Port 5004)...
start "FAL Avatar" cmd /k "python fal_avatar_generator.py"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo    ALL SERVERS STARTED!
echo ============================================================
echo.
echo 🎙️  Podcast Studio:      http://localhost:8080
echo 🎭  Animated Player:      http://localhost:5003
echo 🎬  FAL Avatar Generator: http://localhost:5004
echo.
echo Opening browsers...
timeout /t 2 /nobreak >nul

start http://localhost:8080
timeout /t 1 /nobreak >nul
start http://localhost:5003
timeout /t 1 /nobreak >nul
start http://localhost:5004

echo.
echo ============================================================
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping all servers...
taskkill /FI "WINDOWTITLE eq Podcast Studio*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Animated Player*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq FAL Avatar*" /F >nul 2>&1

echo.
echo All servers stopped.
echo ============================================================
