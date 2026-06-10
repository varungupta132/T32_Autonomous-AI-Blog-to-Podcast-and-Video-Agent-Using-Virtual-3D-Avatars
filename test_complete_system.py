"""
🧪 Complete System Test
Test all components of the animated podcast system
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_file(filepath, description):
    """Check if file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_dependency(module_name):
    """Check if Python module is installed"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} installed")
        return True
    except ImportError:
        print(f"❌ {module_name} NOT installed")
        return False

def main():
    print_header("COMPLETE SYSTEM TEST")
    
    all_passed = True
    
    # Test 1: Check Core Files
    print_header("Test 1: Core Files")
    files_to_check = [
        ("interactive_podcast_studio.py", "Podcast Studio"),
        ("working_animated_player.py", "Animated Player"),
        ("fal_avatar_generator.py", "FAL Avatar Generator"),
        ("templates/index.html", "Podcast Studio Template"),
        ("templates/working_player.html", "Animated Player Template"),
        ("templates/fal_avatar_player.html", "FAL Avatar Template"),
        ("requirements.txt", "Requirements File"),
        (".env", "Environment Config"),
        ("README.md", "README"),
        ("COMPLETE_PROJECT_GUIDE.md", "Complete Guide"),
    ]
    
    for filepath, desc in files_to_check:
        if not check_file(filepath, desc):
            all_passed = False
    
    # Test 2: Check Dependencies
    print_header("Test 2: Python Dependencies")
    dependencies = [
        "flask",
        "edge_tts",
        "librosa",
        "numpy",
        "soundfile",
        "fal_client",
        "dotenv",
    ]
    
    for dep in dependencies:
        if not check_dependency(dep):
            all_passed = False
    
    # Test 3: Check Directories
    print_header("Test 3: Required Directories")
    directories = [
        "uploads",
        "generated_podcasts",
        "avatar_videos",
        "templates",
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✓ Directory exists: {directory}/")
        else:
            print(f"⚠️  Creating directory: {directory}/")
            path.mkdir(exist_ok=True)
    
    # Test 4: Check Environment Variables
    print_header("Test 4: Environment Variables")
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        fal_key = os.getenv('FAL_KEY')
        if fal_key:
            print(f"✓ FAL_KEY is set: {fal_key[:20]}...")
        else:
            print("❌ FAL_KEY not set in .env")
            all_passed = False
    except Exception as e:
        print(f"❌ Error loading .env: {str(e)}")
        all_passed = False
    
    # Test 5: Check Batch Files
    print_header("Test 5: Launcher Scripts")
    launchers = [
        "START_ALL.bat",
        "start_podcast_studio.bat",
        "start_working_player.bat",
        "start_fal_avatar.bat",
    ]
    
    for launcher in launchers:
        if not check_file(launcher, f"Launcher: {launcher}"):
            all_passed = False
    
    # Test 6: Port Availability
    print_header("Test 6: Port Availability")
    import socket
    
    ports = {
        8080: "Podcast Studio",
        5003: "Animated Player",
        5004: "FAL Avatar Generator",
    }
    
    for port, name in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} ({name}) is already in use")
        else:
            print(f"✓ Port {port} ({name}) is available")
    
    # Final Summary
    print_header("TEST SUMMARY")
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour system is ready to use!")
        print("\nTo start all servers:")
        print("  START_ALL.bat")
        print("\nOr start individually:")
        print("  python interactive_podcast_studio.py")
        print("  python working_animated_player.py")
        print("  python fal_avatar_generator.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above and run again.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
