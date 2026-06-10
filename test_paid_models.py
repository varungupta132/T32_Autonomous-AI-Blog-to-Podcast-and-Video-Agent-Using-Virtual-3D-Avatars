"""
Test paid OpenRouter models (uses your credits but more reliable)
"""

from openai import OpenAI
import time

OPENROUTER_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

TEST_BLOG = """
Artificial Intelligence is transforming our world. AI helps doctors diagnose diseases faster, 
helps students learn better, and makes our daily tasks easier. From voice assistants to 
self-driving cars, AI is everywhere. However, we must use AI responsibly and ethically.
"""

# Cheaper paid models (low cost per token)
MODELS = [
    ("meta-llama/llama-3.2-3b-instruct", "Llama 3.2 3B - Very cheap, fast"),
    ("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B - Cheap, good quality"),
    ("mistralai/mistral-7b-instruct", "Mistral 7B - Cheap, reliable"),
    ("google/gemini-flash-1.5", "Gemini Flash - Fast, cheap")
]

PROMPT = """Convert this blog into a podcast script with 2 hosts (Alex and Sam).

Blog: {blog}

Write 6-8 dialogue lines. Format: Speaker: Dialogue

Start:"""

print("="*80)
print("🧪 TESTING PAID MODELS (Uses your API credits)")
print("="*80)
print(f"\nYour current credits: Check at https://openrouter.ai/credits")
print(f"\nTest Blog:")
print("-" * 80)
print(TEST_BLOG)
print("-" * 80)

results = []

for model_name, description in MODELS:
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print(f"Description: {description}")
    print('='*80)
    
    try:
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{'role': 'user', 'content': PROMPT.format(blog=TEST_BLOG)}],
            max_tokens=400
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        script = response.choices[0].message.content
        dialogue_count = len([line for line in script.split('\n') if ':' in line and len(line) > 10])
        
        print(f"\n✅ SUCCESS")
        print(f"⏱️  Time: {duration:.2f}s")
        print(f"💬 Dialogues: {dialogue_count}")
        print(f"📝 Preview:")
        print("-" * 80)
        print(script[:300] + "..." if len(script) > 300 else script)
        
        results.append({
            'model': model_name,
            'description': description,
            'success': True,
            'time': duration,
            'dialogue_count': dialogue_count,
            'quality': 'Good' if dialogue_count >= 6 else 'Low'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ FAILED: {error_msg[:150]}")
        
        results.append({
            'model': model_name,
            'description': description,
            'success': False,
            'error': error_msg[:100]
        })
    
    time.sleep(1)

# Summary
print("\n\n" + "="*80)
print("📊 RESULTS")
print("="*80)

successful = [r for r in results if r['success']]

if successful:
    print("\n✅ WORKING MODELS:\n")
    for i, r in enumerate(successful, 1):
        print(f"{i}. {r['model']}")
        print(f"   {r['description']}")
        print(f"   Speed: {r['time']:.2f}s | Dialogues: {r['dialogue_count']} | Quality: {r['quality']}")
        print()
    
    best = min(successful, key=lambda x: (x['time'], -x['dialogue_count']))
    
    print("\n" + "="*80)
    print("🏆 RECOMMENDED MODEL")
    print("="*80)
    print(f"\nModel: {best['model']}")
    print(f"Why: {best['description']}")
    print(f"Performance: {best['time']:.2f}s, {best['dialogue_count']} dialogues")
    print(f"\n💡 Use in your code:")
    print(f'   model="{best["model"]}"')
else:
    print("\n❌ All models failed - API quota may be exhausted")
    print("\n💡 Solution: Add credits at https://openrouter.ai/credits")

print("\n" + "="*80 + "\n")
