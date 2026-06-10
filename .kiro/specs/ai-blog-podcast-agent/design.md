# Design Document: AI Blog-to-Podcast Agent

## Overview

The AI Blog-to-Podcast Agent is a full-stack application that transforms blog text into podcast-style audio with support for single host, co-host, and multi-speaker formats. The system leverages local LLM (Ollama) for intelligent script generation and modular TTS engines for high-quality audio synthesis.

### Core Capabilities
- Blog text to podcast script conversion using Ollama (llama3/mistral)
- Multi-speaker support (single, cohost, multi-panel)
- Modular TTS integration (ElevenLabs, Coqui TTS)
- Audio merging with natural silence gaps
- Podcast history tracking with metadata
- Avatar-ready JSON output for future video integration

### Technology Stack
- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: Python 3.9+ FastAPI
- **LLM**: Ollama (local inference)
- **TTS**: ElevenLabs API / Coqui TTS (modular)
- **Audio Processing**: pydub + FFmpeg
- **Database**: SQLite (dev) / PostgreSQL (prod-ready)
- **Deployment**: Docker + docker-compose

## Architecture

### System Architecture

The application follows a clean, layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  React + Vite + TailwindCSS (Port 5173)                     │
│  - Input Form Component                                      │
│  - History List Component                                    │
│  - API Service Layer                                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      Backend Layer                           │
│  FastAPI (Port 8000)                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Routers (API Endpoints)                             │  │
│  │  - POST /api/generate                                │  │
│  │  - GET /api/history                                  │  │
│  │  - GET /api/download/{filename}                      │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
