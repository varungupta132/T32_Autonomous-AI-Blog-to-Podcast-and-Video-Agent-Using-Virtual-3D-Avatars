import os
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

def get_retry_session(retries=5, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def download_file(url, output_path):
    session = get_retry_session()
    try:
        response = session.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            return output_path
        raise Exception(f"Failed to download {url} with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Download connection error for {url}: {e}")

def merge_avatar_videos(video_urls, output_path, bg_music_path=None):
    """Original method: for segment-by-segment processing"""
    from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, afx
    
    temp_files = [f"temp_video_{i}.mp4" for i in range(len(video_urls))]
    
    def download_task(args):
        url, temp_path = args
        if str(url).startswith('http://') or str(url).startswith('https://'):
            download_file(url, temp_path)
        else:
            import shutil
            shutil.copy(url, temp_path)
        return temp_path

    try:
        print(f"Downloading {len(video_urls)} generated avatar videos in parallel...")
        with ThreadPoolExecutor(max_workers=min(len(video_urls), 10)) as executor:
            list(executor.map(download_task, zip(video_urls, temp_files)))
                
        print("Concatenating video clips with moviepy...")
        clips = [VideoFileClip(f) for f in temp_files]
        final_clip = concatenate_videoclips(clips, method="compose")
        
        if bg_music_path and os.path.exists(bg_music_path):
            bgm = AudioFileClip(bg_music_path).with_effects([afx.MultiplyVolume(0.1), afx.AudioLoop(duration=final_clip.duration)])
            combined_audio = CompositeAudioClip([final_clip.audio, bgm])
            final_clip = final_clip.with_audio(combined_audio)
            
        final_clip.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", threads=8, logger=None)
        return output_path
        
    finally:
        for f in temp_files:
            if os.path.exists(f): 
                try: os.remove(f)
                except: pass

def merge_avatar_videos_batched(speaker_video_map, dialogue_segments, output_path, bg_music_path=None):
    """
    New high-speed method: Slices and stitches long speaker videos.
    speaker_video_map: { "Alex": "url_or_local_path", ... }
    dialogue_segments: [ {"speaker": "Alex", "duration": 5.2}, ... ]
    """
    from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, afx
    
    download_tasks = []
    speaker_temp_files = {}
    
    try:
        # 1. Download speaker batch videos
        for speaker, url in speaker_video_map.items():
            temp_path = f"batch_{speaker}.mp4"
            speaker_temp_files[speaker] = temp_path
            download_tasks.append((url, temp_path))
            
        print(f"Downloading {len(download_tasks)} speaker batch videos...")
        with ThreadPoolExecutor(max_workers=len(download_tasks) or 1) as executor:
            def download_task(args):
                url, path = args
                return download_file(url, path) if str(url).startswith('http') else shutil.copy(url, path)
            import shutil
            list(executor.map(download_task, download_tasks))

        # 2. Open speaker clips
        speaker_clips = {speaker: VideoFileClip(path) for speaker, path in speaker_temp_files.items()}
        
        # 3. Slice and Stitch
        print("Assembling final video from speaker batches...")
        final_dialogue_clips = []
        speaker_offsets = {speaker: 0 for speaker in speaker_clips}
        
        for i, seg in enumerate(dialogue_segments):
            speaker = seg["speaker"]
            dur = seg["duration"]
            
            if speaker in speaker_clips:
                clip = speaker_clips[speaker]
                start = speaker_offsets[speaker]
                end = start + dur
                
                # Use subclipped (MoviePy 2.x syntax)
                dialogue_clip = clip.subclipped(start, end)
                final_dialogue_clips.append(dialogue_clip)
                
                speaker_offsets[speaker] = end
            else:
                print(f"Warning: Speaker {speaker} missing from video map!")

        # 4. Concatenate with method="chain" (much faster as resolutions are identical)
        final_clip = concatenate_videoclips(final_dialogue_clips, method="chain")
        
        # 5. Overlay BGM
        if bg_music_path and os.path.exists(bg_music_path):
            bgm = AudioFileClip(bg_music_path).with_effects([afx.MultiplyVolume(0.1), afx.AudioLoop(duration=final_clip.duration)])
            combined_audio = CompositeAudioClip([final_clip.audio, bgm])
            final_clip = final_clip.with_audio(combined_audio)
            
        print(f"Exporting optimized assembly to {output_path}...")
        final_clip.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", threads=8, logger=None)
        
        # Close everything
        for clip in speaker_clips.values(): clip.close()
        for clip in final_dialogue_clips: clip.close()
        final_clip.close()
        
        return output_path

    finally:
        for path in speaker_temp_files.values():
            if os.path.exists(path):
                try: os.remove(path)
                except: pass
