"""
Test ElevenLabs API Key
Quick test to check if API key is working
"""

from elevenlabs.client import ElevenLabs

# API Key to test
API_KEY = "sk_V2_hgu_kOf1AlxV1qq_DoKDSwJp0SaUBEwWNW4riDRCO8rgiuFW"

def test_api_key():
    """Test if API key is valid and working"""
    
    print("🔑 Testing ElevenLabs API Key...")
    print("="*60)
    print(f"\nAPI Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print("")
    
    try:
        # Initialize client
        print("1️⃣ Initializing ElevenLabs client...")
        client = ElevenLabs(api_key=API_KEY)
        print("   ✅ Client initialized")
        
        # Test with a simple text-to-speech request
        print("\n2️⃣ Testing text-to-speech generation...")
        print("   Text: 'Hello, this is a test.'")
        
        # Use a default voice (Adam)
        voice_id = "pNInz6obpgDQGcFmaJgB"
        
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text="Hello, this is a test.",
            model_id="eleven_multilingual_v2"
        )
        
        # Try to get first chunk
        audio_bytes = b""
        for chunk in audio_generator:
            audio_bytes += chunk
            break  # Just get first chunk to test
        
        if audio_bytes:
            print("   ✅ Audio generated successfully!")
            print(f"   📊 Received {len(audio_bytes)} bytes of audio data")
            
            print("\n" + "="*60)
            print("✅ API KEY IS WORKING!")
            print("="*60)
            print("\n🎉 Status: VALID")
            print("🎤 Voice Generation: Working")
            print("📡 API Connection: Active")
            print("\n✨ You can use this API key for podcast generation!")
            
            return True
        else:
            print("   ❌ No audio data received")
            return False
            
    except Exception as e:
        error_msg = str(e)
        
        print("\n" + "="*60)
        print("❌ API KEY TEST FAILED!")
        print("="*60)
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            print("\n🚫 Status: INVALID")
            print("❌ Error: API key is not valid or expired")
            print("\n💡 Possible reasons:")
            print("   • API key is incorrect")
            print("   • API key has expired")
            print("   • API key has been revoked")
            
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            print("\n⚠️  Status: QUOTA EXCEEDED")
            print("❌ Error: API quota/limit reached")
            print("\n💡 Solution:")
            print("   • Wait for quota to reset")
            print("   • Upgrade your plan")
            print("   • Use a different API key")
            
        elif "403" in error_msg or "Forbidden" in error_msg:
            print("\n🚫 Status: ACCESS DENIED")
            print("❌ Error: API key doesn't have required permissions")
            
        else:
            print(f"\n❌ Error: {error_msg}")
        
        return False

if __name__ == "__main__":
    print("\n")
    success = test_api_key()
    print("\n")
    
    if success:
        exit(0)
    else:
        exit(1)
