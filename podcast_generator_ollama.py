"""
Podcast Generator using Ollama (Local AI - No API Limits!)
"""

import ollama
from typing import Literal
import os

class PodcastGeneratorOllama:
    def __init__(self, model: str = "llama2"):
        """
        Initialize with Ollama model
        
        Models:
        - llama2 (3.8GB) - Good quality
        - mistral (4.4GB) - Better quality
        - gemma3:1b (815MB) - Fast, smaller
        """
        self.model = model
        print(f"✅ Using Ollama model: {model}")
    
    def generate_podcast(
        self,
        blog_content: str,
        title: str = "",
        podcast_type: Literal["single", "co-host", "multi-host"] = "single",
        audience: Literal["global", "indian"] = "global"
    ) -> dict:
        """Generate podcast script using Ollama"""
        
        print(f"\n⏳ Generating {podcast_type} podcast for {audience} audience...")
        print(f"🦙 Using local Ollama (no API limits!)")
        
        try:
            # Create prompt
            prompt = self._create_prompt(blog_content, title, podcast_type, audience)
            
            # Generate with Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            script = response['message']['content']
            
            return {
                'success': True,
                'script': script,
                'podcast_type': podcast_type,
                'audience': audience,
                'title': title,
                'original_length': len(blog_content),
                'script_length': len(script),
                'model': self.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_prompt(self, content: str, title: str, ptype: str, audience: str) -> str:
        """Create enhanced prompt based on settings"""
        
        # Enhanced audience instructions
        if audience == "indian":
            aud_note = """
TARGET AUDIENCE: Indian listeners (Hinglish style)
LANGUAGE STYLE:
- Mix Hindi and English naturally (like "yaar", "basically", "actually", "matlab")
- Use Indian context: IIT, UPSC, cricket, Bollywood, chai, jugaad
- Conversational tone like popular Indian podcasts (The Ranveer Show, IVM Podcasts)
- Relatable scenarios from Indian daily life
- Natural code-switching between Hindi and English
AVOID: Forced Hindi, overly formal English, stereotypes
"""
        else:
            aud_note = """
TARGET AUDIENCE: Global English-speaking listeners
LANGUAGE STYLE:
- Clear, professional English with warmth
- Universal examples everyone can relate to
- International context and references
- Accessible to non-native English speakers
- Neutral accent-friendly vocabulary
AVOID: Regional slang, complex jargon, cultural assumptions
"""
        
        # Enhanced type instructions
        if ptype == "single":
            type_note = """
PODCAST FORMAT: Single Host Monologue
STRUCTURE:
- Warm welcome with hook: "Have you ever wondered...?"
- Personal connection: "I", "you", "we"
- Break into 3-4 clear segments with transitions
- Use rhetorical questions to engage
- Share insights like storytelling
- End with key takeaway and call-to-action

SPEAKER LABEL: Use "Host:" for all lines
TONE: Conversational yet authoritative, like a knowledgeable friend
PACING: Vary sentence length - short for impact, longer for explanation

EXAMPLE:
Host: Hey everyone, welcome back! Today we're diving into something that's been on my mind...
Host: You know what's fascinating? The way this completely changes how we think about...
Host: Let me break this down for you...
"""
        elif ptype == "co-host":
            type_note = """
PODCAST FORMAT: Co-Host Dialogue (2 people)
STRUCTURE:
- Alex introduces, Sam adds perspective
- Natural back-and-forth every 2-3 lines
- One explains, other asks clarifying questions
- Build on each other's points
- Occasional surprise or friendly disagreement
- Equal participation (50/50 split)

SPEAKER LABELS: Use "Alex:" and "Sam:" consistently
TONE: Like two friends having an engaging conversation over coffee
DYNAMICS: Questions, agreements, insights, occasional humor

EXAMPLE:
Alex: So I was reading about this, and it completely changed my perspective.
Sam: Really? What surprised you the most?
Alex: Well, the data shows something unexpected...
Sam: That's fascinating! It reminds me of when we discussed...
Alex: Exactly! And here's the interesting part...
"""
        else:
            type_note = """
PODCAST FORMAT: Multi-Host Panel (3 people)
STRUCTURE:
- Alex (moderator) guides and asks questions
- Jordan (expert) provides deep insights and analysis
- Casey (curious learner) asks questions listeners would ask
- Dynamic conversation with multiple viewpoints
- Occasional friendly debate or different opinions
- All three participate actively and equally

SPEAKER LABELS: Use "Alex:", "Jordan:", "Casey:" consistently
TONE: Professional panel with energy and engagement
DYNAMICS: Questions, expert answers, clarifications, different perspectives

EXAMPLE:
Alex: Let's break this down. Jordan, what's your expert take on this?
Jordan: From my experience, the key factor is...
Casey: Wait, can you explain that more simply? I think our listeners might wonder...
Alex: Great question, Casey. Jordan, can you elaborate?
Jordan: Absolutely. Think of it this way...
"""
        
        return f"""
You are an expert podcast script writer. Create an engaging, professional podcast script.

{type_note}

{aud_note}

CONTENT GUIDELINES:
1. HOOK listeners in first 15 seconds - intrigue, question, or bold statement
2. Break complex ideas into simple, relatable explanations
3. Use concrete examples and analogies people can visualize
4. Vary sentence length for natural rhythm and emphasis
5. Include moments of insight: "Here's what's interesting...", "The key thing is..."
6. Build momentum - start broad, go deeper, end with impact
7. Make it conversational - use contractions, natural speech patterns
8. Add personality - enthusiasm, curiosity, thoughtfulness

QUALITY STANDARDS (CRITICAL):
✓ ONLY speakable dialogue - no stage directions, no [MUSIC], no *actions*, no (parentheses)
✓ NO markdown formatting (no **, ##, __, etc.)
✓ NO emojis or special characters
✓ Clear speaker labels at start of each line (Host:, Alex:, Sam:)
✓ Natural pauses indicated by sentence breaks and punctuation
✓ Conversational language, NOT written essay style
✓ Each point made once - NO repetition of ideas
✓ Smooth transitions: "Speaking of...", "That reminds me...", "Here's the thing..."
✓ Engaging throughout - every line should add value
✓ End strong - memorable takeaway or call-to-action

SCRIPT LENGTH: 
- Single host: 10-15 segments (350-450 words)
- Co-host: 10-14 exchanges (300-400 words)
- Multi-host: 12-16 exchanges (350-450 words)

TOPIC: {title if title else "Untitled"}

SOURCE CONTENT TO TRANSFORM:
{content}

Now write the complete podcast script following ALL guidelines above. 
Start directly with the dialogue - no preamble, no "Here's the script", just begin:
"""


def main():
    """Main application"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "🦙 OLLAMA PODCAST GENERATOR (LOCAL AI)" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    print("✅ No API limits! Unlimited podcasts!")
    print("✅ Runs on your computer")
    print("✅ Completely free!")
    print("\n")
    
    # Check if Ollama is installed
    try:
        models = ollama.list()
        print(f"✅ Ollama is running!")
        print(f"📦 Available models: {len(models['models'])}")
    except Exception as e:
        print("❌ Ollama not found!")
        print("\n📥 Install Ollama:")
        print("   1. Download from: https://ollama.com/download")
        print("   2. Install it")
        print("   3. Run: ollama pull llama3.2")
        print("\n")
        return
    
    # Choose model
    print("\n🦙 Choose model:")
    print("  1. llama2 (3.8GB) - Good quality")
    print("  2. mistral (4.4GB) - Better quality")
    print("  3. gemma3:1b (815MB) - Fast, smaller")
    print("\nEnter choice (1/2/3) or press Enter for default:")
    
    model_choice = input().strip() or "1"
    
    model_map = {
        "1": "llama2",
        "2": "mistral",
        "3": "gemma3:1b"
    }
    
    model = model_map.get(model_choice, "llama2")
    
    generator = PodcastGeneratorOllama(model=model)
    
    # Get blog input
    print("\n📝 Enter your blog content:")
    print("(Type or paste, then press Enter twice)\n")
    
    lines = []
    while True:
        line = input()
        if line == "":
            if lines and lines[-1] == "":
                break
            lines.append(line)
        else:
            lines.append(line)
    
    blog_content = "\n".join(lines[:-1])
    
    if not blog_content.strip():
        print("❌ No content provided!")
        return
    
    # Get title
    print("\n📌 Enter blog title (optional):")
    title = input().strip()
    
    # Get podcast type
    print("\n🎙️ Choose podcast type:")
    print("  1. Single Host")
    print("  2. Co-Host")
    print("  3. Multi-Host")
    print("\nEnter choice (1/2/3):")
    
    type_choice = input().strip()
    type_map = {"1": "single", "2": "co-host", "3": "multi-host"}
    podcast_type = type_map.get(type_choice, "single")
    
    # Get audience
    print("\n🌍 Choose audience:")
    print("  1. Global")
    print("  2. Indian (Hinglish)")
    print("\nEnter choice (1/2):")
    
    aud_choice = input().strip()
    aud_map = {"1": "global", "2": "indian"}
    audience = aud_map.get(aud_choice, "global")
    
    # Generate
    result = generator.generate_podcast(blog_content, title, podcast_type, audience)
    
    if result['success']:
        print("\n")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 25 + "🎙️  PODCAST SCRIPT" + " " * 33 + "║")
        print("╚" + "═" * 78 + "╝")
        print("\n")
        
        print(result['script'])
        
        print("\n")
        print("─" * 80)
        print("📊 STATS")
        print("─" * 80)
        print(f"Model:            {result['model']}")
        print(f"Podcast Type:     {result['podcast_type'].upper()}")
        print(f"Audience:         {result['audience'].upper()}")
        print(f"Original Length:  {result['original_length']:,} chars")
        print(f"Script Length:    {result['script_length']:,} chars")
        print("─" * 80)
        
        # Save
        filename = f"podcast_{podcast_type}_{audience}_{title.replace(' ', '_') if title else 'script'}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result['script'])
        
        print(f"\n💾 Saved to: {filename}")
        print("\n✅ Done! Generate unlimited podcasts with Ollama! 🦙\n")
    else:
        print(f"\n❌ Error: {result['error']}\n")


if __name__ == "__main__":
    main()
