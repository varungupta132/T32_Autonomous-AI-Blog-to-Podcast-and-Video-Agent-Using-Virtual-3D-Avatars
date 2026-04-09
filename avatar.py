import os
import time
import requests
import base64

def generate_did_video(audio_path, source_image_url, api_key):
    """
    Calls the D-ID API to generate a talking head video based on local audio and an image URL.
    """
    print(f"Generating D-ID video for avatar {source_image_url[:30]}...")

    url = "https://api.d-id.com/talks"
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {api_key}"
    }

    # 1. Upload local audio to D-ID
    if os.path.exists(audio_path):
        files = { "audio": (os.path.basename(audio_path), open(audio_path, 'rb'), "audio/mpeg") }
        upload_res = requests.post(
            "https://api.d-id.com/audios", 
            headers={"authorization": f"Basic {api_key}"}, 
            files=files
        )
        if upload_res.status_code in [200, 201]:
            audio_url = upload_res.json().get('url')
        else:
            raise Exception(f"Failed to upload audio to D-ID: {upload_res.text}")
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

    response = requests.post(url, json=payload, headers=post_headers)
    if response.status_code not in [200, 201]:
        raise Exception(f"D-ID API Error: {response.text}")
        
    data = response.json()
    talk_id = data.get("id")
    
    if not talk_id:
        raise Exception(f"No talk ID returned from D-ID: {data}")
        
    print(f"Talk ID '{talk_id}' created. Polling for completion...")
    
    # 3. Poll for completion
    poll_url = f"{url}/{talk_id}"
    for _ in range(60): # 3 minutes max
        time.sleep(3)
        poll_res = requests.get(poll_url, headers=headers)
        poll_data = poll_res.json()
        status = poll_data.get('status')
        if status == 'done':
            return poll_data.get('result_url')
        elif status in ['error', 'rejected']:
            raise Exception(f"D-ID Video Generation Failed: {poll_data}")
            
    raise Exception("D-ID Video Generation timed out.")
