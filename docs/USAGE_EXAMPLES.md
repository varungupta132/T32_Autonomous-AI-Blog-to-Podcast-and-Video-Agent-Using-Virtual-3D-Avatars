# Usage Examples

## Example 1: Single Host Podcast (Global Audience)

```python
from podcast_generator_ollama import PodcastGeneratorOllama

generator = PodcastGeneratorOllama(model="llama2")

blog_content = """
Machine learning is revolutionizing healthcare. From early disease detection 
to personalized treatment plans, AI is helping doctors make better decisions 
and save lives.
"""

result = generator.generate_podcast(
    blog_content=blog_content,
    title="AI in Healthcare",
    podcast_type="single",
    audience="global"
)

print(result['script'])
```

## Example 2: Co-Host Podcast (Indian Audience)

```python
from podcast_generator_ollama import PodcastGeneratorOllama

generator = PodcastGeneratorOllama(model="llama2")

blog_content = """
India's startup ecosystem is booming. With unicorns emerging every few months,
the country is becoming a global hub for innovation and entrepreneurship.
"""

result = generator.generate_podcast(
    blog_content=blog_content,
    title="Indian Startup Boom",
    podcast_type="co-host",
    audience="indian"
)

print(result['script'])
```

## Example 3: Multi-Host Panel Discussion

```python
from podcast_generator_ollama import PodcastGeneratorOllama

generator = PodcastGeneratorOllama(model="mistral")

blog_content = """
Climate change is the defining challenge of our generation. Rising temperatures,
extreme weather events, and melting ice caps demand immediate action from 
governments, businesses, and individuals.
"""

result = generator.generate_podcast(
    blog_content=blog_content,
    title="Climate Crisis",
    podcast_type="multi-host",
    audience="global"
)

print(result['script'])
```

## Example 4: Generate Audio Podcast

```python
from podcast_to_voice import PodcastVoiceGenerator

voice_gen = PodcastVoiceGenerator()

blog_content = """
Cryptocurrency and blockchain technology are transforming finance.
Decentralized systems promise more transparency and accessibility.
"""

audio_file = voice_gen.create_podcast_audio(
    blog_content=blog_content,
    title="Crypto Revolution",
    podcast_type="co-host",
    audience="global"
)

print(f"Audio saved to: {audio_file}")
```

## Example 5: Using the Web Interface

1. Start the server:
```bash
python web_podcast_ollama.py
```

2. Open browser to `http://localhost:5000`

3. Paste your blog content

4. Select options:
   - Podcast Type: Co-Host
   - Audience: Global

5. Click "Generate Podcast"

6. Copy the generated script

## Example 6: Batch Processing Multiple Blogs

```python
from podcast_generator_ollama import PodcastGeneratorOllama
import os

generator = PodcastGeneratorOllama(model="llama2")

blogs = [
    {"title": "AI Ethics", "content": "..."},
    {"title": "Space Exploration", "content": "..."},
    {"title": "Quantum Computing", "content": "..."}
]

for blog in blogs:
    result = generator.generate_podcast(
        blog_content=blog['content'],
        title=blog['title'],
        podcast_type="single",
        audience="global"
    )
    
    if result['success']:
        filename = f"podcasts/{blog['title'].replace(' ', '_')}.txt"
        with open(filename, 'w') as f:
            f.write(result['script'])
        print(f"✓ Generated: {filename}")
```

## Example 7: Custom Model Selection

```python
from podcast_generator_ollama import PodcastGeneratorOllama

# Use faster, smaller model
generator = PodcastGeneratorOllama(model="gemma3:1b")

# Or use higher quality model
generator = PodcastGeneratorOllama(model="mistral")

result = generator.generate_podcast(
    blog_content="Your content...",
    title="Your Title",
    podcast_type="co-host",
    audience="global"
)
```

## Tips for Best Results

1. **Content Length**: 200-1000 words works best
2. **Clear Topics**: Well-structured blogs generate better podcasts
3. **Model Selection**: 
   - `gemma3:1b` - Fast, good for testing
   - `llama2` - Balanced quality and speed
   - `mistral` - Best quality, slower
4. **Audience Choice**: Match your target listeners
5. **Podcast Type**: 
   - Single host for educational content
   - Co-host for discussions
   - Multi-host for debates/panels
