"""
Quick test script - tests one example from each category
"""
import ollama
import re

BLOG_CONTENT = """AI is changing our daily life. Voice assistants like Siri help us. Netflix uses AI for recommendations. Doctors use AI to detect diseases early. Self-driving cars use AI. AI saves time and improves productivity."""

def generate_podcast(content, ptype, audience):
    """Generate podcast using Ollama"""
    try:
        if audience == "indian":
            aud = """Indian Hinglish - Mix Hindi words: acha, bahut, kya, matlab, bilkul, sahi.
Example: "Acha, so AI ka matlab hai machines bhi soch sakti hain!"
"""
        else:
            aud = "Global English - clear, professional."
        
        if ptype == "single":
            fmt = """SINGLE HOST ONLY - Use ONLY "Host:" label.
Example:
Host: Welcome everyone!
Host: Let me explain AI."""
        elif ptype == "co-host":
            fmt = """TWO HOSTS - Alex and Sam only.
Example:
Alex: This is interesting.
Sam: I agree!"""
        else:
            fmt = """THREE HOSTS - Alex, Jordan, Casey.
Example:
Alex: Let's discuss.
Jordan: Good point.
Casey: Can you explain?"""
        
        prompt = f"""Professional podcast script.

FORMAT: {fmt}
STYLE: {aud}

RULES:
- NO emojis
- NO stage directions
- ONLY dialogue
- 6-8 exchanges
- 200-300 words

CONTENT: {content}

Write dialogue now:"""
        
        print(f"\n{'='*60}")
        print(f"Testing: {ptype.upper()} | {audience.upper()}")
        print(f"{'='*60}")
        
        response = ollama.chat(
            model='llama2',
            messages=[
                {
                    'role': 'system',
                    'content': f'Podcast writer. Single=Host only. Co-host=Alex+Sam only. Multi=Alex+Jordan+Casey only.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.7,
                'num_predict': 400
            }
        )
        
        script = response['message']['content']
        
        # Clean up
        script = re.sub(r'[^\x00-\x7F]+', '', script)
        script = re.sub(r'\*[^*]+\*', '', script)
        script = re.sub(r'\([^)]+\)', '', script)
        script = re.sub(r'\[[^\]]+\]', '', script)
        
        # Fix labels
        if ptype == "single":
            script = re.sub(r'(Alex|Sam|Jordan|Casey):', 'Host:', script)
        elif ptype == "co-host":
            script = script.replace('Host:', 'Alex:')
            script = re.sub(r'(Jordan|Casey):', 'Sam:', script)
        else:
            script = script.replace('Host:', 'Alex:')
        
        # Clean lines
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line and ':' in line and len(line) > 10:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[1].strip()) > 5:
                    lines.append(line)
        
        script = '\n\n'.join(lines)
        
        # Validate
        issues = []
        
        if ptype == "single":
            if 'Alex:' in script or 'Sam:' in script:
                issues.append("❌ Should only have Host:")
            if 'Host:' not in script:
                issues.append("❌ Missing Host:")
        elif ptype == "co-host":
            if 'Host:' in script:
                issues.append("❌ Should not have Host:")
            if 'Alex:' not in script or 'Sam:' not in script:
                issues.append("❌ Should have Alex and Sam")
        else:
            if 'Host:' in script:
                issues.append("❌ Should not have Host:")
            if 'Alex:' not in script:
                issues.append("❌ Missing Alex")
        
        if audience == "indian":
            hindi_words = ['acha', 'bahut', 'kya', 'matlab', 'bilkul', 'sahi', 'hai', 'ka']
            has_hindi = any(word in script.lower() for word in hindi_words)
            if not has_hindi:
                issues.append("⚠️  Should use Hinglish")
        
        # Print
        print(f"\n📝 Script:")
        print(script[:400])
        
        if issues:
            print(f"\n⚠️  Issues:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print(f"\n✅ PASSED")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

# Run tests
if __name__ == '__main__':
    print("\n🧪 QUICK PODCAST TEST\n")
    
    tests = [
        ("single", "global"),
        ("single", "indian"),
        ("co-host", "global"),
        ("co-host", "indian"),
        ("multi-host", "global"),
        ("multi-host", "indian"),
    ]
    
    results = []
    for ptype, audience in tests:
        passed = generate_podcast(BLOG_CONTENT, ptype, audience)
        results.append((ptype, audience, passed))
    
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    for ptype, audience, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {ptype:12} | {audience:8}")
    
    passed_count = sum(1 for _, _, p in results if p)
    print(f"\n{passed_count}/{len(results)} tests passed")
