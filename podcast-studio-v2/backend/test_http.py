"""Test the HTTP API endpoints"""
import requests
import json

BASE = "http://localhost:8080"

# Test 1: homepage
r = requests.get(BASE)
print(f"GET / -> {r.status_code}")

# Test 2: generate audio
script = """Alex: Welcome everyone to our AI podcast today!
Sam: Thanks Alex! I am really excited to discuss artificial intelligence.
Alex: AI is transforming every industry from healthcare to education.
Sam: Absolutely! The possibilities are truly endless.
Alex: Thanks for joining us today everyone!
Sam: Goodbye everyone, take care!"""

payload = {
    "script": script,
    "name": "http_test_podcast",
    "podcast_type": "co-host",
    "audience": "global"
}

print("\nPOST /api/generate ...")
r = requests.post(f"{BASE}/api/generate", json=payload, timeout=120)
print(f"Status: {r.status_code}")
data = r.json()
print(json.dumps(data, indent=2))

if data.get("success"):
    filename = data["filename"]
    # Test stream
    r2 = requests.get(f"{BASE}/api/stream/{filename}")
    print(f"\nGET /api/stream/{filename} -> {r2.status_code}, {len(r2.content)} bytes")

    # Test history
    r3 = requests.get(f"{BASE}/api/history")
    hist = r3.json()
    print(f"\nGET /api/history -> {r3.status_code}, {len(hist)} records")
    if hist:
        print(f"  Latest: {hist[0]}")
