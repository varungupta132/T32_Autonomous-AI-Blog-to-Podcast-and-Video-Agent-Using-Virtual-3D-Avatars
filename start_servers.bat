@echo off
echo ========================================
echo  Starting AI Podcast Generator Servers
echo ========================================
echo.

echo Starting Backend Server on port 8000...
start "Backend Server" cmd /k "cd ai-blog-podcast\backend && uvicorn main:app --reload --port 8000"
timeout /t 3 >nul

echo Starting Frontend Server on port 5173...
start "Frontend Server" cmd /k "cd ai-blog-podcast\frontend && npm run dev"
timeout /t 3 >nul

echo.
echo ========================================
echo  Servers Started! 🚀
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Backend Server*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend Server*" /T /F >nul 2>&1
echo ✅ Servers stopped
