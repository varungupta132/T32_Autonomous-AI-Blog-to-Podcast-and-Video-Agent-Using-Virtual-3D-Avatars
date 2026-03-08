# API Documentation

## Web Interface API

### Generate Podcast Endpoint

**URL:** `/generate`

**Method:** `POST`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "title": "Optional podcast title",
  "content": "Blog content to convert",
  "podcast_type": "single|co-host|multi-host",
  "audience": "global|indian"
}
```

**Response:**
```json
{
  "success": true,
  "script": "Generated podcast script..."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "suggestion": "How to fix the error"
}
```

### Example Usage

```javascript
fetch('/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'AI in Education',
    content: 'Your blog content here...',
    podcast_type: 'co-host',
    audience: 'global'
  })
})
.then(response => response.json())
.then(data => console.log(data.script));
```

## Python API

### PodcastGeneratorOllama Class

```python
from podcast_generator_ollama import PodcastGeneratorOllama

# Initialize
generator = PodcastGeneratorOllama(model="llama2")

# Generate podcast
result = generator.generate_podcast(
    blog_content="Your content...",
    title="Podcast Title",
    podcast_type="co-host",
    audience="global"
)

if result['success']:
    print(result['script'])
```

### PodcastVoiceGenerator Class

```python
from podcast_to_voice import PodcastVoiceGenerator

# Initialize
voice_gen = PodcastVoiceGenerator()

# Create audio podcast
audio_file = voice_gen.create_podcast_audio(
    blog_content="Your content...",
    title="Podcast Title",
    podcast_type="co-host",
    audience="indian"
)
```

## Configuration Options

See `config.py` for all available configuration options:

- `DEFAULT_MODEL`: Ollama model to use
- `FLASK_PORT`: Web server port
- `AUDIO_BITRATE`: Audio quality setting
- `TEMPERATURE`: AI creativity level
- `GENERATION_TIMEOUT`: Maximum generation time
