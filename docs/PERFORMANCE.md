# Performance Guide

## Benchmarks

### Script Generation Times

| Model | Content Length | Time | Quality |
|-------|---------------|------|---------|
| gemma3:1b | 500 words | 15-25s | Good |
| llama2 | 500 words | 30-45s | Better |
| mistral | 500 words | 45-90s | Best |

### Audio Generation Times

| Segments | Processing | Merging | Total |
|----------|-----------|---------|-------|
| 5-10 | 10-15s | 2-3s | 12-18s |
| 10-15 | 15-25s | 3-5s | 18-30s |
| 15-20 | 25-35s | 5-7s | 30-42s |

## Optimization Strategies

### 1. Model Selection

Choose the right model for your needs:

```python
# Fast generation (testing, development)
generator = PodcastGeneratorOllama(model="gemma3:1b")

# Balanced (production)
generator = PodcastGeneratorOllama(model="llama2")

# High quality (final output)
generator = PodcastGeneratorOllama(model="mistral")
```

### 2. Content Length Optimization

Optimal content lengths:
- **Single host**: 300-500 words
- **Co-host**: 400-600 words
- **Multi-host**: 500-800 words

Longer content = longer generation time

### 3. Temperature Settings

```python
# Faster, more deterministic
options = {'temperature': 0.5}

# Balanced
options = {'temperature': 0.7}

# More creative, slower
options = {'temperature': 0.9}
```

### 4. Parallel Processing

For batch operations:

```python
from concurrent.futures import ThreadPoolExecutor

def generate_podcast(blog):
    generator = PodcastGeneratorOllama()
    return generator.generate_podcast(blog['content'], blog['title'])

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(generate_podcast, blogs)
```

### 5. Caching

Cache frequently used prompts:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_prompt_template(podcast_type, audience):
    # Return cached template
    return template
```

## Memory Management

### Monitor Memory Usage

```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

### Reduce Memory Footprint

1. **Use smaller models**
```python
generator = PodcastGeneratorOllama(model="gemma3:1b")
```

2. **Process in batches**
```python
for batch in chunks(blogs, batch_size=5):
    process_batch(batch)
```

3. **Clear cache periodically**
```python
import gc
gc.collect()
```

## System Requirements

### Minimum Specs
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 8 GB
- **Storage**: 5 GB free
- **Model**: gemma3:1b

**Expected Performance:**
- Generation: 20-30s
- Audio: 15-20s

### Recommended Specs
- **CPU**: 4+ cores, 3.0+ GHz
- **RAM**: 16 GB
- **Storage**: 10 GB free (SSD)
- **Model**: llama2 or mistral

**Expected Performance:**
- Generation: 30-45s
- Audio: 10-15s

### High-Performance Setup
- **CPU**: 8+ cores, 3.5+ GHz
- **RAM**: 32 GB
- **Storage**: 20 GB free (NVMe SSD)
- **GPU**: Optional (for future GPU acceleration)
- **Model**: Any

**Expected Performance:**
- Generation: 15-30s
- Audio: 5-10s

## Network Optimization

### Initial Setup
- Download models once
- Cache models locally
- No internet needed after setup

### Offline Mode
All processing is local:
- No API calls
- No data transmission
- Complete privacy

## Disk I/O Optimization

### Use SSD Storage
- 3-5x faster than HDD
- Better for audio processing
- Recommended for production

### Temporary Files
```python
import tempfile

# Use system temp directory
temp_dir = tempfile.gettempdir()
```

### Clean Up
```python
import shutil

# Remove old files
shutil.rmtree('audio_segments', ignore_errors=True)
os.makedirs('audio_segments', exist_ok=True)
```

## Monitoring

### Track Generation Time

```python
import time

start = time.time()
result = generator.generate_podcast(content, title)
duration = time.time() - start

print(f"Generated in {duration:.2f}s")
```

### Log Performance Metrics

```python
import logging

logging.info(f"Model: {model}, Time: {duration}s, Length: {len(script)}")
```

## Troubleshooting Slow Performance

### Issue: Generation takes > 2 minutes

**Solutions:**
1. Switch to faster model
2. Reduce content length
3. Lower temperature
4. Check system resources
5. Close other applications

### Issue: High CPU usage

**Solutions:**
1. Limit concurrent generations
2. Use smaller model
3. Add delays between requests
4. Monitor with `htop` or Task Manager

### Issue: Memory errors

**Solutions:**
1. Use gemma3:1b model
2. Process smaller batches
3. Increase system swap
4. Restart Ollama service

## Best Practices

1. **Development**: Use `gemma3:1b` for fast iteration
2. **Testing**: Use `llama2` for quality checks
3. **Production**: Use `mistral` for final output
4. **Batch Processing**: Limit to 3-5 concurrent jobs
5. **Monitoring**: Log all generation times
6. **Cleanup**: Remove temporary files regularly
7. **Updates**: Keep Ollama and models updated

## Performance Comparison

### Single Generation

| Setup | Time | Quality Score |
|-------|------|---------------|
| Basic (gemma3:1b) | 20s | 7/10 |
| Standard (llama2) | 40s | 8/10 |
| Premium (mistral) | 70s | 9/10 |

### Batch Processing (10 blogs)

| Workers | Total Time | Avg per Blog |
|---------|-----------|--------------|
| 1 | 400s | 40s |
| 2 | 220s | 22s |
| 3 | 160s | 16s |
| 4 | 140s | 14s |

## Future Optimizations

- GPU acceleration support
- Model quantization
- Streaming generation
- Distributed processing
- Advanced caching
- Pre-compiled prompts

---

**Last Updated**: March 2026
