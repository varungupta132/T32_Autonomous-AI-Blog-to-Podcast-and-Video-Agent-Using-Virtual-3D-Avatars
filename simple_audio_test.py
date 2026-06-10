"""
Simple audio test without FFmpeg dependency
Just concatenates MP3 files directly
"""

import os
from pathlib import Path

def simple_merge_mp3(input_files, output_file):
    """Simple MP3 concatenation without FFmpeg"""
    print(f"\n🔧 Merging {len(input_files)} audio files...")
    
    with open(output_file, 'wb') as outfile:
        for i, mp3_file in enumerate(input_files, 1):
            print(f"   [{i}/{len(input_files)}] Adding {mp3_file.name}...")
            with open(mp3_file, 'rb') as infile:
                outfile.write(infile.read())
    
    file_size = os.path.getsize(output_file) / 1024 / 1024
    print(f"\n✅ Merged successfully!")
    print(f"📁 Output: {output_file}")
    print(f"💿 Size: {file_size:.2f} MB")
    
    return output_file

if __name__ == "__main__":
    print("🎙️ Simple Audio Merge Test\n")
    
    # Get audio files
    temp_dir = Path("ai-blog-podcast/backend/temp")
    audio_files = sorted(temp_dir.glob("test_segment_*.mp3"))
    
    if not audio_files:
        print("❌ No audio files found!")
        exit(1)
    
    print(f"Found {len(audio_files)} audio segments:")
    for f in audio_files:
        print(f"   • {f.name}")
    
    # Merge
    output_dir = Path("ai-blog-podcast/backend/outputs")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "test_podcast_simple.mp3"
    
    simple_merge_mp3(audio_files, output_file)
    
    print("\n🎉 Test Complete!")
    print(f"🎧 Play the podcast: {output_file}")
    print("\nNote: This is a simple concatenation.")
    print("For better quality with pauses, install FFmpeg.")
