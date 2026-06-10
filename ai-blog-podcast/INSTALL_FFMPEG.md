# Install FFmpeg on Windows

FFmpeg is required for audio processing. Here are the easiest ways to install it:

## Option 1: Using Chocolatey (Recommended)

If you have Chocolatey installed:
```powershell
choco install ffmpeg
```

## Option 2: Using Winget

```powershell
winget install Gyan.FFmpeg
```

## Option 3: Manual Installation

1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Download the "ffmpeg-release-essentials.zip"
3. Extract to `C:\ffmpeg`
4. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\ffmpeg\bin`
5. Restart PowerShell

## Verify Installation

```powershell
ffmpeg -version
```

You should see FFmpeg version information.

## After Installing FFmpeg

Restart your backend server:
```powershell
cd ai-blog-podcast\backend
.\venv\Scripts\Activate.ps1
python run.py
```
