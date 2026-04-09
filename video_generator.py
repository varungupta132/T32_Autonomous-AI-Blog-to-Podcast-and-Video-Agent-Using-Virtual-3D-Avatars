import os
import requests
from pathlib import Path

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return output_path
    raise Exception(f"Failed to download {url}")

def merge_avatar_videos(video_urls, output_path, bg_music_path=None):
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
    
    temp_files = []
    try:
        # Download API videos
        print(f"Downloading {len(video_urls)} generated avatar videos...")
        for i, url in enumerate(video_urls):
            temp_path = f"temp_video_{i}.mp4"
            download_file(url, temp_path)
            temp_files.append(temp_path)
                
        # Concatenate
        print("Concatenating video clips with moviepy...")
        clips = [VideoFileClip(f) for f in temp_files]
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Overlay BGM
        if bg_music_path and os.path.exists(bg_music_path):
            bgm = AudioFileClip(bg_music_path).volumex(0.1).loop(duration=final_clip.duration)
            combined_audio = CompositeAudioClip([final_clip.audio, bgm])
            final_clip = final_clip.set_audio(combined_audio)
            
        print(f"Exporting final assembled podcast video to {output_path}...")
        final_clip.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="fast"
        )
        return output_path
        
    finally:
        for clip in vars().get('clips', []):
            try: clip.close() 
            except: pass
        for f in temp_files:
            if os.path.exists(f) and f.startswith('temp_video_'):
                try: os.remove(f)
                except: pass
