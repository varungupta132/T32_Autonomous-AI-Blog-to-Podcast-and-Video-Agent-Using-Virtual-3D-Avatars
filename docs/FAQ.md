# Frequently Asked Questions (FAQ)

## General Questions

### What is this project?

An AI-powered tool that converts blog posts into professional podcast scripts and audio using local AI models (Ollama). No API costs, completely free and private.

### Do I need an internet connection?

Only for initial setup to download Ollama and AI models. After that, everything runs locally offline.

### Is it really free?

Yes! No API costs, no subscriptions, no hidden fees. Everything runs on your computer.

### What languages are supported?

- English (Global audience)
- Hinglish (Hindi-English mix for Indian audience)

More languages can be added in future versions.

## Technical Questions

### What are the system requirements?

**Minimum:**
- Python 3.8+
- 8GB RAM
- 5GB free disk space

**Recommended:**
- Python 3.10+
- 16GB RAM
- 10GB free disk space
- SSD storage

### Which AI model should I use?

- **gemma3:1b** (815MB) - Fast, good for testing
- **llama2** (3.8GB) - Balanced quality and speed (recommended)
- **mistral** (4.4GB) - Best quality, slower

### How long does generation take?

- Script generation: 30-90 seconds
- Audio generation: 10-30 seconds
- Total: 1-2 minutes per podcast

### Can I use GPU acceleration?

Currently CPU-only. GPU support may be added in future versions.

## Usage Questions

### What's the ideal blog length?

300-800 words works best. Too short lacks content, too long takes longer to process.

### Can I generate multiple podcasts at once?

Yes! Use the batch processing script in `examples/batch_process.py`.

### Can I customize the voices?

Currently uses gTTS voices. Premium voices (ElevenLabs) can be configured optionally.

### How do I change the podcast style?

Choose from:
- **Single Host** - One narrator
- **Co-Host** - Two-person dialogue
- **Multi-Host** - Three-person panel

### Can I edit the generated script?

Yes! Scripts are saved as text files. Edit them before converting to audio.

## Troubleshooting Questions

### Why is generation slow?

- Use faster model (gemma3:1b)
- Reduce content length
- Close other applications
- Check system resources

### Why does audio sound robotic?

gTTS has limitations. Consider:
- Using ElevenLabs for premium voices
- Adjusting speech rate
- Post-processing audio

### Ollama connection fails?

```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Port 5000 already in use?

Change port in code or kill the process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

## Feature Questions

### Can I add background music?

Basic intro/outro music is generated. Custom music can be added with audio editing tools.

### Can I export to video?

Not yet. 3D avatar video integration is in progress.

### Can I use my own AI model?

Yes, if it's compatible with Ollama. Pull any model:
```bash
ollama pull <model-name>
```

### Can I customize prompts?

Yes! Edit the prompt templates in `podcast_generator_ollama.py`.

### Does it support multiple speakers in audio?

Yes! Different speakers get slightly different voice characteristics.

## Privacy & Security

### Is my data sent anywhere?

No! Everything runs locally. No data leaves your computer.

### Are the generated podcasts copyrighted?

You own the output. The AI-generated content is yours to use.

### Can I use this commercially?

Yes! MIT License allows commercial use.

### Is it safe to use?

Yes, but follow security best practices:
- Keep software updated
- Don't run as admin/root
- Validate untrusted input

## Contribution Questions

### How can I contribute?

See `CONTRIBUTING.md` for guidelines. Contributions welcome!

### I found a bug. What should I do?

Open a GitHub issue with:
- Description
- Steps to reproduce
- Expected vs actual behavior
- System information

### Can I request features?

Yes! Open a GitHub issue with the "enhancement" label.

### How do I submit a pull request?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit PR with description

## Comparison Questions

### How is this different from paid services?

**Advantages:**
- Free (no API costs)
- Private (local processing)
- Unlimited usage
- Customizable

**Trade-offs:**
- Requires local setup
- Uses your computer resources
- Voice quality depends on TTS engine

### Why use this instead of ChatGPT?

- No API costs
- No rate limits
- Complete privacy
- Offline capability
- Specialized for podcasts

### Can it replace professional podcast production?

It's a great starting point, but professional production may need:
- Professional voice actors
- Advanced audio editing
- Custom music/sound effects
- Post-production polish

## Future Plans

### What features are planned?

- 3D avatar video generation
- More language support
- GPU acceleration
- Advanced voice customization
- Real-time generation
- Cloud deployment option

### When will video support be ready?

Currently in development. Follow the repository for updates.

### Will there be a mobile app?

Not currently planned, but the web interface works on mobile browsers.

### Can I sponsor development?

Not set up yet, but contributions and stars on GitHub are appreciated!

## Getting Help

### Where can I get support?

- Read documentation in `/docs`
- Check this FAQ
- Search GitHub issues
- Open a new issue
- Join discussions

### How do I report security issues?

See `SECURITY.md` for responsible disclosure process.

### Is there a community?

GitHub Discussions and Issues are the main community spaces.

---

**Still have questions?** Open a GitHub issue or discussion!

**Last Updated**: March 2026
