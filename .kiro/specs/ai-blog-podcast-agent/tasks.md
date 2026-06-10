# Tasks: AI Blog-to-Podcast Agent with Virtual 3D Avatar Influencers

## 1. Project Setup

- [ ] 1.1 Initialize project structure
  - [ ] 1.1.1 Create root directory and subdirectories (backend/, frontend/)
  - [ ] 1.1.2 Create backend folder structure (routers/, services/, models/, outputs/, temp/)
  - [ ] 1.1.3 Create frontend folder structure (src/components/, src/pages/, src/services/)
  - [ ] 1.1.4 Initialize git repository with .gitignore

- [ ] 1.2 Setup backend environment
  - [ ] 1.2.1 Create requirements.txt with all dependencies
  - [ ] 1.2.2 Create .env.example file
  - [ ] 1.2.3 Create config.py with Settings class
  - [ ] 1.2.4 Setup virtual environment instructions in README

- [ ] 1.3 Setup frontend environment
  - [ ] 1.3.1 Initialize Vite React project
  - [ ] 1.3.2 Install and configure TailwindCSS
  - [ ] 1.3.3 Create package.json with dependencies
  - [ ] 1.3.4 Configure vite.config.js

## 2. Backend - Database Layer

- [ ] 2.1 Create database models
  - [ ] 2.1.1 Implement BlogPodcastOutput SQLAlchemy model in models/database.py
  - [ ] 2.1.2 Create database initialization function
  - [ ] 2.1.3 Setup SQLite connection with session management
  - [ ] 2.1.4 Create database migration script

- [ ] 2.2 Test database operations
  - [ ] 2.2.1 Write unit tests for model creation
  - [ ] 2.2.2 Test CRUD operations
  - [ ] 2.2.3 Verify PostgreSQL compatibility

## 3. Backend - LLM Service

- [ ] 3.1 Implement Ollama integration
  - [ ] 3.1.1 Create OllamaService class in services/llm_service.py
  - [ ] 3.1.2 Implement connection to Ollama API
  - [ ] 3.1.3 Build prompt template system
  - [ ] 3.1.4 Implement dynamic prompt generation based on podcast_type, audience, language_style
  - [ ] 3.1.5 Add timeout handling (5 seconds)
  - [ ] 3.1.6 Implement retry logic for Ollama failures

- [ ] 3.2 Test LLM service
  - [ ] 3.2.1 Write unit tests with mocked Ollama responses
  - [ ] 3.2.2 Test prompt generation for all parameter combinations
  - [ ] 3.2.3 Test timeout and retry mechanisms
  - [ ] 3.2.4 **Property Test 1.1**: Verify script format consistency (SPEAKER: dialogue)
  - [ ] 3.2.5 **Property Test 1.2**: Verify speaker count matches podcast type

## 4. Backend - Script Parser Service

- [ ] 4.1 Implement script parser
  - [ ] 4.1.1 Create ScriptParser class in services/script_parser.py
  - [ ] 4.1.2 Implement parse_script() method
  - [ ] 4.1.3 Implement validate_script() method
  - [ ] 4.1.4 Implement get_speakers() method
  - [ ] 4.1.5 Add error handling for malformed scripts

- [ ] 4.2 Test script parser
  - [ ] 4.2.1 Write unit tests for valid script formats
  - [ ] 4.2.2 Test edge cases (empty lines, special characters, multiple colons)
  - [ ] 4.2.3 Test speaker extraction
  - [ ] 4.2.4 **Property Test 1.3**: Verify script completeness (intro and outro)

## 5. Backend - TTS Service

- [ ] 5.1 Create TTS engine interface
  - [ ] 5.1.1 Define TTSEngine abstract base class in services/tts_service.py
  - [ ] 5.1.2 Define synthesize() and is_available() abstract methods

- [ ] 5.2 Implement ElevenLabs TTS
  - [ ] 5.2.1 Create ElevenLabsTTS class
  - [ ] 5.2.2 Implement API integration with authentication
  - [ ] 5.2.3 Implement synthesize() method
  - [ ] 5.2.4 Add retry logic with exponential backoff (max 3 attempts)
  - [ ] 5.2.5 Handle rate limiting

- [ ] 5.3 Implement Coqui TTS (alternative)
  - [ ] 5.3.1 Create CoquiTTS class
  - [ ] 5.3.2 Implement local TTS synthesis
  - [ ] 5.3.3 Implement synthesize() method

- [ ] 5.4 Create TTS service wrapper
  - [ ] 5.4.1 Create TTSService class
  - [ ] 5.4.2 Implement voice mapping (HOST→male, COHOST→female, EXPERT→neutral)
  - [ ] 5.4.3 Implement generate_audio_segments() method
  - [ ] 5.4.4 Add temporary file management

- [ ] 5.5 Test TTS service
  - [ ] 5.5.1 Write unit tests with mocked TTS APIs
  - [ ] 5.5.2 Test voice mapping
  - [ ] 5.5.3 Test retry mechanism
  - [ ] 5.5.4 **Property Test 2.1**: Verify audio segment count equals dialogue count

## 6. Backend - Audio Merger Service

- [ ] 6.1 Implement audio merger
  - [ ] 6.1.1 Create AudioMerger class in services/audio_merger.py
  - [ ] 6.1.2 Implement merge_segments() method using pydub
  - [ ] 6.1.3 Implement add_silence() method (300ms)
  - [ ] 6.1.4 Implement cleanup_temp_files() method
  - [ ] 6.1.5 Add duration calculation
  - [ ] 6.1.6 Implement unique filename generation

- [ ] 6.2 Test audio merger
  - [ ] 6.2.1 Write unit tests for audio merging
  - [ ] 6.2.2 Test silence insertion
  - [ ] 6.2.3 Test cleanup functionality
  - [ ] 6.2.4 **Property Test 2.2**: Verify 300ms silence between segments
  - [ ] 6.2.5 **Property Test 2.3**: Verify audio duration accuracy

## 7. Backend - API Endpoints

- [ ] 7.1 Setup FastAPI application
  - [ ] 7.1.1 Create main.py with FastAPI app initialization
  - [ ] 7.1.2 Configure CORS middleware
  - [ ] 7.1.3 Setup rate limiting with slowapi
  - [ ] 7.1.4 Add exception handlers
  - [ ] 7.1.5 Configure static file serving for outputs/

- [ ] 7.2 Implement POST /api/generate endpoint
  - [ ] 7.2.1 Create routers/podcast.py
  - [ ] 7.2.2 Define PodcastGenerateRequest Pydantic model
  - [ ] 7.2.3 Implement input validation
  - [ ] 7.2.4 Orchestrate LLM → Parser → TTS → Merger flow
  - [ ] 7.2.5 Save to database
  - [ ] 7.2.6 Return response with script, audio_url, metadata
  - [ ] 7.2.7 Add error handling

- [ ] 7.3 Implement GET /api/history endpoint
  - [ ] 7.3.1 Add pagination parameters
  - [ ] 7.3.2 Query database with ordering
  - [ ] 7.3.3 Return formatted response

- [ ] 7.4 Implement GET /api/download/{podcast_id} endpoint
  - [ ] 7.4.1 Validate podcast_id
  - [ ] 7.4.2 Return audio file with proper headers

- [ ] 7.5 Implement GET /api/health endpoint
  - [ ] 7.5.1 Check Ollama connection
  - [ ] 7.5.2 Check TTS availability
  - [ ] 7.5.3 Return health status

- [ ] 7.6 Test API endpoints
  - [ ] 7.6.1 Write integration tests for /api/generate
  - [ ] 7.6.2 Write integration tests for /api/history
  - [ ] 7.6.3 Test error responses (400, 404, 500)
  - [ ] 7.6.4 **Property Test 4.1**: Verify response time constraints
  - [ ] 7.6.5 **Property Test 4.2**: Verify input validation
  - [ ] 7.6.6 **Property Test 4.3**: Verify rate limiting enforcement

## 8. Frontend - API Service

- [ ] 8.1 Create API client
  - [ ] 8.1.1 Create services/api.js with axios configuration
  - [ ] 8.1.2 Implement generatePodcast() function
  - [ ] 8.1.3 Implement getHistory() function
  - [ ] 8.1.4 Implement downloadPodcast() function
  - [ ] 8.1.5 Add error handling and interceptors

## 9. Frontend - Components

- [ ] 9.1 Create LoadingSpinner component
  - [ ] 9.1.1 Implement spinner UI with TailwindCSS
  - [ ] 9.1.2 Add optional message prop

- [ ] 9.2 Create ErrorAlert component
  - [ ] 9.2.1 Implement error display UI
  - [ ] 9.2.2 Add close button functionality

- [ ] 9.3 Create PodcastGenerator component
  - [ ] 9.3.1 Create component structure
  - [ ] 9.3.2 Implement blog textarea with character count
  - [ ] 9.3.3 Implement podcast type dropdown
  - [ ] 9.3.4 Implement audience dropdown
  - [ ] 9.3.5 Implement language style dropdown
  - [ ] 9.3.6 Implement form validation
  - [ ] 9.3.7 Implement generate button with loading state
  - [ ] 9.3.8 Implement result display with download button
  - [ ] 9.3.9 Add error handling UI
  - [ ] 9.3.10 Style with TailwindCSS (responsive design)

- [ ] 9.4 Create PodcastHistory component
  - [ ] 9.4.1 Create component structure
  - [ ] 9.4.2 Implement podcast list display
  - [ ] 9.4.3 Implement pagination controls
  - [ ] 9.4.4 Implement download buttons
  - [ ] 9.4.5 Add loading and error states
  - [ ] 9.4.6 Style with TailwindCSS (responsive design)

## 10. Frontend - Pages and Routing

- [ ] 10.1 Create pages
  - [ ] 10.1.1 Create pages/Home.jsx with PodcastGenerator
  - [ ] 10.1.2 Create pages/History.jsx with PodcastHistory

- [ ] 10.2 Setup routing
  - [ ] 10.2.1 Configure React Router in App.jsx
  - [ ] 10.2.2 Add navigation menu
  - [ ] 10.2.3 Style navigation with TailwindCSS

- [ ] 10.3 Test frontend
  - [ ] 10.3.1 Write component tests for PodcastGenerator
  - [ ] 10.3.2 Write component tests for PodcastHistory
  - [ ] 10.3.3 Test form validation
  - [ ] 10.3.4 Test API integration

## 11. Docker Configuration

- [ ] 11.1 Create backend Dockerfile
  - [ ] 11.1.1 Write Dockerfile with Python base image
  - [ ] 11.1.2 Install ffmpeg and dependencies
  - [ ] 11.1.3 Configure working directory and volumes
  - [ ] 11.1.4 Set CMD to run uvicorn

- [ ] 11.2 Create frontend Dockerfile
  - [ ] 11.2.1 Write multi-stage Dockerfile (build + nginx)
  - [ ] 11.2.2 Configure nginx for SPA routing
  - [ ] 11.2.3 Copy build artifacts

- [ ] 11.3 Create docker-compose.yml
  - [ ] 11.3.1 Define backend service
  - [ ] 11.3.2 Define frontend service
  - [ ] 11.3.3 Configure volumes and networks
  - [ ] 11.3.4 Set environment variables

- [ ] 11.4 Test Docker deployment
  - [ ] 11.4.1 Build and run containers
  - [ ] 11.4.2 Test inter-service communication
  - [ ] 11.4.3 Verify volume persistence

## 12. Documentation

- [ ] 12.1 Create comprehensive README.md
  - [ ] 12.1.1 Write project overview
  - [ ] 12.1.2 Document tech stack
  - [ ] 12.1.3 Write setup instructions (local development)
  - [ ] 12.1.4 Document Ollama installation steps
  - [ ] 12.1.5 Write Docker deployment instructions
  - [ ] 12.1.6 Document environment variables
  - [ ] 12.1.7 Add API documentation with examples
  - [ ] 12.1.8 Add troubleshooting section
  - [ ] 12.1.9 Add screenshots/demo

- [ ] 12.2 Add code comments
  - [ ] 12.2.1 Review and add comments to backend services
  - [ ] 12.2.2 Review and add comments to frontend components
  - [ ] 12.2.3 Add docstrings to all Python functions

## 13. Testing and Quality Assurance

- [ ] 13.1 Backend testing
  - [ ] 13.1.1 Run all unit tests
  - [ ] 13.1.2 Run all integration tests
  - [ ] 13.1.3 Run all property-based tests
  - [ ] 13.1.4 Verify test coverage (>80%)

- [ ] 13.2 Frontend testing
  - [ ] 13.2.1 Run all component tests
  - [ ] 13.2.2 Test responsive design on multiple devices
  - [ ] 13.2.3 Test browser compatibility

- [ ] 13.3 End-to-end testing
  - [ ] 13.3.1 Test complete podcast generation flow
  - [ ] 13.3.2 Test error scenarios
  - [ ] 13.3.3 Test performance (response times)
  - [ ] 13.3.4 **Property Test 3.1**: Verify database record completeness
  - [ ] 13.3.5 **Property Test 3.2**: Verify file system consistency

## 14. Security and Performance

- [ ] 14.1 Security review
  - [ ] 14.1.1 Verify input sanitization
  - [ ] 14.1.2 Test rate limiting
  - [ ] 14.1.3 Verify .env files are not committed
  - [ ] 14.1.4 Review CORS configuration

- [ ] 14.2 Performance optimization
  - [ ] 14.2.1 Verify script generation < 5 seconds
  - [ ] 14.2.2 Verify podcast generation < 15 seconds
  - [ ] 14.2.3 Optimize bundle size
  - [ ] 14.2.4 Test concurrent request handling

## 15. Optional Enhancements

- [ ]* 15.1 Implement avatar-ready JSON output
  - [ ]* 15.1.1 Add timing information to dialogues
  - [ ]* 15.1.2 Generate JSON file alongside audio
  - [ ]* 15.1.3 Include avatar configuration metadata

- [ ]* 15.2 Add background music
  - [ ]* 15.2.1 Integrate background music library
  - [ ]* 15.2.2 Mix music with dialogue audio

- [ ]* 15.3 Implement caching
  - [ ]* 15.3.1 Cache Ollama responses
  - [ ]* 15.3.2 Cache TTS audio segments

---

**Total Tasks**: 150+ (including sub-tasks)  
**Estimated Timeline**: 2-3 weeks for full implementation  
**Priority**: Complete tasks 1-14 for MVP, task 15 is optional
