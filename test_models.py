"""
Test different OpenRouter models for blog-to-podcast conversion
"""

from openai import OpenAI
import time

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Test blog content
TEST_BLOG = """
Artificial Intelligence is transforming our world. AI helps doctors diagnose diseases faster, 
helps students learn better, and makes our daily tasks easier. From voice assistants to 
self-driving cars, AI is everywhere. However, we must use AI responsibly and ethically.
"""

# Models to test
MODELS = [
    "meta-llama/llama-3-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "nvidia/nemotron-3-nano-30b-a3b:free"
]

# Simple prompt for testing
PROMPT = """Convert this blog into a podcast script with 2 hosts (Alex and Sam).

Blog: {blog}

Write 6-8 dialogue lines. Format: Speaker: Dialogue

Start:"""

def test_model(model_name, blog_content):
    """Test a single model"""
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print('='*80)
    
    try:
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': PROMPT.format(blog=blog_content)
                }
            ],
            max_tokens=500
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        script = response.choices[0].message.content
        
        # Count dialogues
        dialogue_count = len([line for line in script.split('\n') if ':' in line and len(line) > 10])
        
        print(f"\n✅ SUCCESS")
        print(f"⏱️  Time: {duration:.2f} seconds")
        print(f"💬 Dialogues: {dialogue_count}")
        print(f"📝 Script Preview:")
        print("-" * 80)
        print(script[:400] + "..." if len(script) > 400 else script)
        
        return {
            'model': model_name,
            'success': True,
            'time': duration,
            'dialogue_count': dialogue_count,
            'script_length': len(script),
            'script': script
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ FAILED")
        print(f"Error: {error_msg}")
        
        # Check error type
        if '429' in error_msg:
            error_type = "Rate Limited"
        elif '404' in error_msg:
            error_type = "Not Available"
        elif '401' in error_msg or 'quota' in error_msg.lower():
            error_type = "Quota Exceeded"
        else:
            error_type = "Unknown Error"
        
        return {
            'model': model_name,
            'success': False,
            'error': error_type,
            'error_detail': error_msg[:200]
        }

# Run tests
print("\n" + "="*80)
print("🧪 TESTING OPENROUTER MODELS FOR BLOG-TO-PODCAST")
print("="*80)
print(f"\nTest Blog Content:")
print("-" * 80)
print(TEST_BLOG)
print("-" * 80)

results = []
for model in MODELS:
    result = test_model(model, TEST_BLOG)
    results.append(result)
    time.sleep(2)  # Wait between requests

# Summary
print("\n\n" + "="*80)
print("📊 RESULTS SUMMARY")
print("="*80)

successful_models = [r for r in results if r['success']]
failed_models = [r for r in results if not r['success']]

if successful_models:
    print("\n✅ WORKING MODELS:")
    for r in successful_models:
        print(f"\n  {r['model']}")
        print(f"    ⏱️  Speed: {r['time']:.2f}s")
        print(f"    💬 Dialogues: {r['dialogue_count']}")
        print(f"    📏 Length: {r['script_length']} chars")

if failed_models:
    print("\n\n❌ FAILED MODELS:")
    for r in failed_models:
        print(f"\n  {r['model']}")
        print(f"    Error: {r['error']}")

# Recommendation
print("\n\n" + "="*80)
print("🎯 RECOMMENDATION")
print("="*80)

if successful_models:
    # Sort by speed and quality
    best = min(successful_models, key=lambda x: x['time'])
    
    print(f"\n🏆 BEST MODEL: {best['model']}")
    print(f"\nReasons:")
    print(f"  • Fastest response: {best['time']:.2f} seconds")
    print(f"  • Generated {best['dialogue_count']} dialogues")
    print(f"  • Available and working")
    print(f"\n💡 Use this in your code:")
    print(f'   model="{best["model"]}"')
else:
    print("\n⚠️  All models failed. Possible reasons:")
    print("  • API quota exceeded")
    print("  • Rate limits hit")
    print("  • Models temporarily unavailable")
    print("\n💡 Solutions:")
    print("  1. Wait a few minutes and try again")
    print("  2. Add your own API key at openrouter.ai")
    print("  3. Use a paid model with credits")

print("\n" + "="*80 + "\n")
