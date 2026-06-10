@echo off
echo Starting Podcast Studio v2...
cd backend
if not exist .env (
    copy .env.example .env
    echo Created .env from example. Please add your OPENROUTER_API_KEY to backend\.env
    pause
)
pip install -r requirements.txt -q
python main.py
pause
