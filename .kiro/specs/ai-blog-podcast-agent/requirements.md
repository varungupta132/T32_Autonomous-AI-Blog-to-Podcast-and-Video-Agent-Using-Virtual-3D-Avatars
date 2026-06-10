# Requirements: AI Blog-to-Podcast Agent with Virtual 3D Avatar Influencers

## 1. Project Overview

### 1.1 Project Description
A production-ready full-stack application that converts blog text into podcast-style audio with support for single host, co-host, and multi-speaker formats. The system uses local LLM (Ollama) for script generation and modular TTS engines for audio synthesis.

### 1.2 Tech Stack
- **Frontend**: React (Vite) + TailwindCSS
- **Backend**: Python FastAPI
- **LLM**: Ollama (llama3 or mistral)
- **TTS**: ElevenLabs or Coqui TTS (modular)
- **Audio**: pydub
- **Database**: SQLite (dev), PostgreSQL-ready
- **Storage**: Local (cloud-ready)
- **Deployment**: Docker

### 1.3 User Flow
1. User inputs blog text
2. User selects podcast type, audience, and language style
3. Backend LLM converts blog to podcast script
4. Script parsed into speaker dialogues
5. Each dialogue converted to audio
6. Audio clips merged sequentially
7. Final podcast generated
8. User downloads podcast

## 2. Functional Requirements

### 2.1 Frontend - Blog Input Interface

**User Story**: As a user, I want to input blog text and configure podcast settings so that I can generate a custom podcast.

**Acceptance Criteria**:
- 2.1.1 Display a textarea for blog text input (minimum 100 characters, maximum 10,000 characters)
- 2.1.2 Provide dropdown for Podcast Type selection: single | cohost | multi
- 2.1.3 Provide dropdown for Audience selection: india | global
- 2.1.4 Provide dropdown for Language Style selection: english | hinglish
- 2.1.5 Display a "Generate Podcast" button
- 2.1.6 Show loading state with progress indicator during generation
- 2.1.7 Display error messages for validation failures
- 2.1.8 Show success message with download link upon completion

### 2.2 Frontend - Podcast History

**User Story**: As a user, I want to view my previously generated podcasts so that I can access them later.

**Acceptance Criteria**:
- 2.2.1 Display a list of all generated podcasts
- 2.2.2 Show metadata for each podcast (date, duration, speakers, type)
- 2.2.3 Provide download button for each podcast
- 2.2.4 Display script preview on click
- 2.2.5 Support pagination for large lists

### 2.3 Backend - Podcast Generation API

**User Story**: As a system, I need to process blog text and generate podcast audio through a RESTful API.

**Acceptance Criteria**:
- 2.3.1 Implement POST /api/generate endpoint
- 2.3.2 Accept request body: {blog, podcast_type, audience, language_style}
- 2.3.3 Validate input parameters
- 2.3.4 Return response: {script, audio_url, metadata: {speakers, duration}}
- 2.3.5 Generate script within 5 seconds
- 2.3.6 Generate complete podcast within 15 seconds
- 2.3.7 Handle errors gracefully with appropriate HTTP status codes

### 2.4 Backend - History API

**User Story**: As a system, I need to retrieve podcast generation history.

**Acceptance Criteria**:
- 2.4.1 Implement GET /api/history endpoint
- 2.4.2 Return list of podcasts with metadata
- 2.4.3 Support optional pagination parameters
- 2.4.4 Sort by creation date (newest first)

### 2.5 LLM Integration Module

**User Story**: As a system, I need to convert blog text into structured podcast scripts using Ollama.

**Acceptance Criteria**:
- 2.5.1 Integrate with local Ollama instance
- 2.5.2 Support llama3 and mistral models
- 2.5.3 Use structured prompt based on podcast type
- 2.5.4 Ensure output format: "SPEAKER: dialogue"
- 2.5.5 Generate single host script for podcast_type=single
- 2.5.6 Generate host + cohost dialogue for podcast_type=cohost
- 2.5.7 Generate 3-4 speaker panel for podcast_type=multi
- 2.5.8 Adapt tone based on audience (india/global)
- 2.5.9 Support language style (english/hinglish)
- 2.5.10 Include intro hook and outro in script
- 2.5.11 Keep dialogues short and realistic (max 3 sentences per turn)

### 2.6 Script Parser Module

**User Story**: As a system, I need to parse LLM-generated scripts into structured dialogue data.

**Acceptance Criteria**:
- 2.6.1 Parse script line by line
- 2.6.2 Extract speaker name from "SPEAKER:" prefix
- 2.6.3 Extract dialogue text
- 2.6.4 Map speaker to voice profile
- 2.6.5 Return array of {speaker, text} objects
- 2.6.6 Handle malformed lines gracefully
- 2.6.7 Validate speaker consistency

### 2.7 TTS Engine Module

**User Story**: As a system, I need to convert text dialogues into audio using modular TTS engines.

**Acceptance Criteria**:
- 2.7.1 Support ElevenLabs TTS integration
- 2.7.2 Support Coqui TTS integration
- 2.7.3 Allow TTS engine selection via configuration
- 2.7.4 Convert each dialogue to separate audio segment
- 2.7.5 Map speakers to voice profiles:
  - HOST → Male voice
  - COHOST → Female voice
  - EXPERT → Neutral voice
- 2.7.6 Save audio segments temporarily
- 2.7.7 Implement retry mechanism (max 3 attempts) for TTS failures
- 2.7.8 Handle TTS API rate limits

### 2.8 Audio Merger Module

**User Story**: As a system, I need to merge individual audio segments into a final podcast file.

**Acceptance Criteria**:
- 2.8.1 Use pydub for audio processing
- 2.8.2 Maintain dialogue order from script
- 2.8.3 Add 300ms silence between clips
- 2.8.4 Merge all segments into single MP3 file
- 2.8.5 Save final file to /outputs folder
- 2.8.6 Generate unique filename with timestamp
- 2.8.7 Calculate total duration
- 2.8.8 Clean up temporary audio segments after merge

### 2.9 Database Models

**User Story**: As a system, I need to persist podcast data for history and retrieval.

**Acceptance Criteria**:
- 2.9.1 Create BlogPodcastOutput model with fields:
  - id (primary key)
  - blog_text (text)
  - script (text)
  - audio_path (string)
  - podcast_type (string)
  - audience (string)
  - language_style (string)
  - duration (integer, seconds)
  - speaker_count (integer)
  - word_count (integer)
  - created_at (timestamp)
- 2.9.2 Support SQLite for development
- 2.9.3 Structure code for PostgreSQL compatibility
- 2.9.4 Implement database migrations
- 2.9.5 Create User model (optional, for future authentication)

### 2.10 Avatar-Ready Output (Optional)

**User Story**: As a system, I should generate avatar-ready JSON for future video integration.

**Acceptance Criteria**:
- 2.10.1 Generate JSON with dialogue timing information
- 2.10.2 Include speaker metadata for avatar mapping
- 2.10.3 Provide audio segment timestamps
- 2.10.4 Save JSON alongside audio file

## 3. Non-Functional Requirements

### 3.1 Performance

**Acceptance Criteria**:
- 3.1.1 Script generation completes within 5 seconds
- 3.1.2 Complete podcast generation within 15 seconds
- 3.1.3 API response time < 500ms for history endpoint
- 3.1.4 Support concurrent requests (minimum 5 simultaneous users)

### 3.2 Security

**Acceptance Criteria**:
- 3.2.1 Store API keys in .env file
- 3.2.2 Implement rate limiting (10 requests per minute per IP)
- 3.2.3 Sanitize all user inputs
- 3.2.4 Validate file uploads and text length
- 3.2.5 Use CORS configuration for frontend-backend communication
- 3.2.6 Implement request timeout (30 seconds)

### 3.3 Architecture

**Acceptance Criteria**:
- 3.3.1 Follow clean architecture principles
- 3.3.2 Separate concerns: routers, services, models
- 3.3.3 Use dependency injection where appropriate
- 3.3.4 Implement modular TTS engine interface
- 3.3.5 Make storage layer cloud-ready (abstraction for S3/Azure)
- 3.3.6 Support easy extension to video avatar generation

### 3.4 Code Quality

**Acceptance Criteria**:
- 3.4.1 Include comprehensive inline comments
- 3.4.2 Follow PEP 8 for Python code
- 3.4.3 Follow ESLint standards for JavaScript
- 3.4.4 Use type hints in Python
- 3.4.5 Implement error handling for all external calls
- 3.4.6 Log errors and important events
- 3.4.7 No placeholder or pseudo-code

### 3.5 User Experience

**Acceptance Criteria**:
- 3.5.1 Responsive design (mobile, tablet, desktop)
- 3.5.2 Clean and intuitive UI
- 3.5.3 Clear error messages
- 3.5.4 Loading indicators for async operations
- 3.5.5 Accessible design (WCAG 2.1 Level AA considerations)

### 3.6 Deployment

**Acceptance Criteria**:
- 3.6.1 Provide Dockerfile for backend
- 3.6.2 Provide Dockerfile for frontend
- 3.6.3 Provide docker-compose.yml for orchestration
- 3.6.4 Include environment variable templates
- 3.6.5 Document deployment steps in README

### 3.7 Documentation

**Acceptance Criteria**:
- 3.7.1 Comprehensive README.md with:
  - Project overview
  - Setup instructions
  - Ollama installation guide
  - How to run locally
  - API documentation
  - Environment variables
  - Troubleshooting guide
- 3.7.2 API documentation with request/response examples
- 3.7.3 Code comments for complex logic
- 3.7.4 Architecture diagram (optional)

## 4. Technical Constraints

### 4.1 Dependencies
- Python 3.9+
- Node.js 18+
- Ollama installed locally
- FFmpeg for audio processing

### 4.2 File Structure
```
project-root/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── podcast.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── script_parser.py
│   │   ├── tts_service.py
│   │   └── audio_merger.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── outputs/
│   ├── temp/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 5. Future Enhancements (Out of Scope)

- User authentication and authorization
- Cloud storage integration (S3, Azure Blob)
- 3D avatar video generation
- Multi-language support beyond English/Hinglish
- Advanced voice cloning
- Background music integration
- Podcast editing interface
- Social media sharing
- Analytics dashboard
