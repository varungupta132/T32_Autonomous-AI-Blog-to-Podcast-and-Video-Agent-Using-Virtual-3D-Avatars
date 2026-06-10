import os
import time
import requests
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

def create_fallback_video(audio_path, source_image_url):
    print("Generating local fallback video due to D-ID failure...")
    from moviepy import ImageClip, AudioFileClip
    import tempfile
    
    if source_image_url.startswith("http"):
        import requests
        img_data = requests.get(source_image_url).content
        fd, temp_img = tempfile.mkstemp(suffix=".jpg")
        with os.fdopen(fd, 'wb') as f:
            f.write(img_data)
        img_path = temp_img
    else:
        img_path = source_image_url

    audio_clip = AudioFileClip(audio_path)
    video_clip = ImageClip(img_path).with_duration(audio_clip.duration)
    
    # Ensure dimensions are even for libx264
    w, h = video_clip.size
    new_w = w if w % 2 == 0 else w - 1
    new_h = h if h % 2 == 0 else h - 1
    if (new_w, new_h) != (w, h):
        video_clip = video_clip.resized(new_size=(new_w, new_h))
        
    video_clip = video_clip.with_audio(audio_clip)
    
    output_path = tempfile.mktemp(suffix=".mp4", dir=os.path.dirname(audio_path) or ".")
    print(f"Writing fallback video to {output_path}")
    video_clip.write_videofile(output_path, fps=1, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
    
    if source_image_url.startswith("http"):
        try: os.remove(img_path)
        except: pass
        
    return output_path

def generate_did_video(audio_path, source_image_url, api_key, fast_mode=False):
    """
    Calls the D-ID API to generate a talking head video based on local audio and an image URL.
    If fast_mode is True, it bypasses D-ID and creates a static video locally.
    """
    if fast_mode:
        print("Fast mode enabled. Generating local static video...")
        return create_fallback_video(audio_path, source_image_url)

    print(f"Generating D-ID video for avatar {source_image_url[:40]}...")

    url = "https://api.d-id.com/talks"
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {api_key}"
    }

    session = get_retry_session()

    try:
        # 1. Upload local audio to D-ID
        if os.path.exists(audio_path):
            files = { "audio": (os.path.basename(audio_path), open(audio_path, 'rb'), "audio/mpeg") }
            upload_res = session.post(
                "https://api.d-id.com/audios", 
                headers={"authorization": f"Basic {api_key}"}, 
                files=files,
                timeout=60 # Extended timeout for upload
            )
            if upload_res.status_code in [200, 201]:
                audio_url = upload_res.json().get('url')
            else:
                raise Exception(f"Failed to upload audio to D-ID. Status: {upload_res.status_code}, Response: {upload_res.text}")
        else:
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # 2. Trigger Video Generation
        payload = {
            "script": {
                "type": "audio",
                "audio_url": audio_url
            },
            "source_url": source_image_url
        }
        
        post_headers = headers.copy()
        post_headers["content-type"] = "application/json"

        response = session.post(url, json=payload, headers=post_headers, timeout=60)
        if response.status_code not in [200, 201]:
            raise Exception(f"D-ID API Error. Status: {response.status_code}, Response: {response.text}")
            
        data = response.json()
        talk_id = data.get("id")
        
        if not talk_id:
            raise Exception(f"No talk ID returned from D-ID: {data}")
            
        print(f"Talk ID '{talk_id}' created. Polling for completion...")
        
        # 3. Poll for completion
        poll_url = f"{url}/{talk_id}"
        for attempt in range(120): # Increased to 10 mins (120 * 5)
            time.sleep(5)
            poll_res = session.get(poll_url, headers=headers, timeout=30)
            if poll_res.status_code not in [200, 201]:
                print(f"Polling HTTP Error {poll_res.status_code}: {poll_res.text}")
                continue # Retry next iteration
                
            poll_data = poll_res.json()
            status = poll_data.get('status')
            if status == 'done':
                return poll_data.get('result_url')
            elif status in ['error', 'rejected']:
                raise Exception(f"D-ID Video Generation Failed on remote server: {poll_data}")
                
        raise Exception("D-ID Video Generation timed out after 10 minutes of polling.")
        
    except Exception as e:
        print(f"D-ID API Error encountered: {e}. Falling back to static video.")
        return create_fallback_video(audio_path, source_image_url)
