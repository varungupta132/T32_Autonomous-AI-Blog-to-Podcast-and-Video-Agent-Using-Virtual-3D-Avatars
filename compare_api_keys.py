"""
Compare Multiple ElevenLabs API Keys
Test which one is working
"""

from elevenlabs.client import ElevenLabs

# API Keys to test
API_KEYS = {
    "New Key": "sk_V2_hgu_kOf1AlxV1qq_DoKDSwJp0SaUBEwWNW4riDRCO8rgiuFW",
    "Old Key (from notebook)": "sk_33c17748cbd7ba62cc21225bb2e995d33844a7671dd4f115"
}

def test_single_key(name, api_key):
    """Test a single API key"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Key: {api_key[:15]}...{api_key[-10:]}")
    print('='*60)
    
    try:
        client = ElevenLabs(api_key=api_key)
        
        # Quick test
        audio_generator = client.text_to_speech.convert(
            voice_id="pNInz6obpgDQGcFmaJgB",
            text="Test",
            model_id="eleven_multilingual_v2"
        )
        
        # Get first chunk
        for chunk in audio_generator:
            if chunk:
                print(f"✅ {name}: WORKING!")
                print(f"   Status: Valid and Active")
                return True
        
        return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ {name}: FAILED")
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            print(f"   Status: Invalid or Expired")
        elif "quota" in error_msg.lower():
            print(f"   Status: Quota Exceeded")
        else:
            print(f"   Error: {error_msg[:100]}")
        
        return False

def main():
    print("\n" + "="*60)
    print("🔑 ELEVENLABS API KEY COMPARISON TEST")
    print("="*60)
    
    results = {}
    
    for name, key in API_KEYS.items():
        results[name] = test_single_key(name, key)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    working_keys = [name for name, status in results.items() if status]
    
    if working_keys:
        print(f"\n✅ Working Keys: {len(working_keys)}")
        for name in working_keys:
            key = API_KEYS[name]
            print(f"   • {name}")
            print(f"     Key: {key}")
    else:
        print("\n❌ No working keys found!")
    
    failed_keys = [name for name, status in results.items() if not status]
    if failed_keys:
        print(f"\n❌ Failed Keys: {len(failed_keys)}")
        for name in failed_keys:
            print(f"   • {name}")
    
    print("\n" + "="*60)
    
    if working_keys:
        print("\n🎯 RECOMMENDATION:")
        print(f"   Use: {working_keys[0]}")
        print(f"   Key: {API_KEYS[working_keys[0]]}")
    else:
        print("\n⚠️  WARNING: No valid API keys!")
        print("   You need to get a new API key from:")
        print("   https://elevenlabs.io/app/settings/api-keys")
    
    print("\n")

if __name__ == "__main__":
    main()
