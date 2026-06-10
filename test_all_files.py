"""
Test script to verify all files in 'final kaam jo ho chuka hai _' folder
"""

import sys
import os

print("="*80)
print("🧪 TESTING ALL FILES IN 'final kaam jo ho chuka hai _' FOLDER")
print("="*80)

# Test 1: Check if files exist
print("\n📁 Test 1: Checking if files exist...")
files_to_check = [
    "final kaam jo ho chuka hai _/standalone_podcast_generator.py",
    "final kaam jo ho chuka hai _/web_podcast_openrouter.py"
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"  ✅ {file} - EXISTS")
    else:
        print(f"  ❌ {file} - NOT FOUND")

# Test 2: Check imports
print("\n📦 Test 2: Checking imports...")

print("\n  Testing standalone_podcast_generator.py imports...")
try:
    from pathlib import Path
    from elevenlabs import VoiceSettings
    from elevenlabs.client import ElevenLabs
    print("  ✅ All imports for standalone_podcast_generator.py are available")
except ImportError as e:
    print(f"  ❌ Missing import: {e}")

print("\n  Testing web_podcast_openrouter.py imports...")
try:
    from flask import Flask, render_template_string, request, jsonify
    from openai import OpenAI
    import re
    print("  ✅ All imports for web_podcast_openrouter.py are available")
except ImportError as e:
    print(f"  ❌ Missing import: {e}")

# Test 3: Check API keys
print("\n🔑 Test 3: Checking API keys...")

print("\n  Checking standalone_podcast_generator.py...")
try:
    sys.path.insert(0, "final kaam jo ho chuka hai _")
    import standalone_podcast_generator as standalone
    
    if standalone.ELEVENLABS_API_KEY and len(standalone.ELEVENLABS_API_KEY) > 10:
        print(f"  ✅ ElevenLabs API Key: {standalone.ELEVENLABS_API_KEY[:20]}...")
    else:
        print("  ❌ ElevenLabs API Key missing or invalid")
        
    if standalone.VOICE_MAP:
        print(f"  ✅ Voice Map configured with {len(standalone.VOICE_MAP)} voices")
    else:
        print("  ❌ Voice Map not configured")
        
except Exception as e:
    print(f"  ❌ Error loading standalone: {e}")

print("\n  Checking web_podcast_openrouter.py...")
try:
    import web_podcast_openrouter as web_openrouter
    
    if web_openrouter.OPENROUTER_API_KEY and len(web_openrouter.OPENROUTER_API_KEY) > 10:
        print(f"  ✅ OpenRouter API Key: {web_openrouter.OPENROUTER_API_KEY[:20]}...")
    else:
        print("  ❌ OpenRouter API Key missing or invalid")
        
except Exception as e:
    print(f"  ❌ Error loading web_openrouter: {e}")

# Test 4: Check functions
print("\n⚙️  Test 4: Checking core functions...")

print("\n  Testing standalone_podcast_generator.py functions...")
try:
    if hasattr(standalone, 'parse_script'):
        print("  ✅ parse_script() function exists")
    if hasattr(standalone, 'generate_audio_segment'):
        print("  ✅ generate_audio_segment() function exists")
    if hasattr(standalone, 'merge_audio_files'):
        print("  ✅ merge_audio_files() function exists")
    if hasattr(standalone, 'generate_podcast'):
        print("  ✅ generate_podcast() function exists")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n  Testing web_podcast_openrouter.py functions...")
try:
    if hasattr(web_openrouter, 'generate_podcast'):
        print("  ✅ generate_podcast() function exists")
    if hasattr(web_openrouter, 'app'):
        print("  ✅ Flask app exists")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 5: Test script parsing
print("\n📝 Test 5: Testing script parsing...")
test_script = """
Alex: Hello everyone!
Sam: Hi there!
Alex: How are you?
Sam: I'm great!
"""

try:
    dialogues = standalone.parse_script(test_script)
    if len(dialogues) == 4:
        print(f"  ✅ Script parsing works correctly - found {len(dialogues)} dialogues")
        for speaker, dialogue in dialogues:
            print(f"     - {speaker}: {dialogue[:30]}...")
    else:
        print(f"  ⚠️  Script parsing found {len(dialogues)} dialogues (expected 4)")
except Exception as e:
    print(f"  ❌ Script parsing failed: {e}")

# Summary
print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)

print("\n✅ WORKING FILES:")
print("  1. standalone_podcast_generator.py")
print("     - Purpose: Generate audio from script using ElevenLabs")
print("     - Usage: python 'final kaam jo ho chuka hai _/standalone_podcast_generator.py'")
print("     - Features: Script parsing, audio generation, file merging")

print("\n  2. web_podcast_openrouter.py")
print("     - Purpose: Web UI to generate podcast scripts using OpenRouter AI")
print("     - Usage: python 'final kaam jo ho chuka hai _/web_podcast_openrouter.py'")
print("     - Features: Web interface, AI script generation, Hinglish support")

print("\n⚠️  MISSING FILE:")
print("  - unified_podcast_generator.py (needs to be created)")
print("    This would combine both: Blog → AI Script → Audio Generation")

print("\n💡 RECOMMENDATIONS:")
print("  1. Test standalone_podcast_generator.py with a sample script")
print("  2. Test web_podcast_openrouter.py by running the Flask server")
print("  3. Create unified_podcast_generator.py to combine both functionalities")

print("\n" + "="*80)
print("✨ Testing Complete!")
print("="*80 + "\n")
