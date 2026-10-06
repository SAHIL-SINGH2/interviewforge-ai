# Technical Note — InterviewForge AI

## Architecture
The prototype is a FastAPI application serving a single-page web client. Upload/paste inputs are parsed into normalized text, analyzed into role/candidate structures, and passed into an adaptive interview state machine. The session stores every prior answer. After each answer, the evaluator produces question-level feedback and the next-question generator chooses a follow-up based on the role, resume evidence, answer content and interview level.

## AI / LLM approach
The system has two modes. The default local adaptive engine performs deterministic NLP extraction with a skill taxonomy and uses answer-aware question rules so it can run with no API key. Optional Groq/OpenAI-compatible mode sends only the structured context needed for generation and keeps the same state machine/evaluation path.

## Dynamic questioning
Screening draws on resume projects/claims and motivation. Competency increases technical and decision-making depth. Deep-dive inspects the latest answer for weak detail or concepts such as accuracy, RAG, APIs, trade-offs and retrieval, then issues a targeted follow-up. The next question therefore depends on the previous answer and is not a fixed questionnaire.

## Evaluation methodology
Each answer receives a 0–100 assessment from evidence such as answer detail, role-specific terms, reasoning markers, metrics, debugging/validation language and concrete examples. Competency scores are averaged across turns. Readiness combines interview performance with job-fit alignment.

## Voice implementation
The client uses Web Speech API for speech recognition and `speechSynthesis` for TTS. The camera bonus uses `getUserMedia` for a local preview only. No facial-expression or emotion inference is performed.

## Data model
SQLite stores completed interview summaries. The live session object holds JD analysis, candidate analysis, current level, prior turns, and the current question.

## Limitations
Browser speech recognition support differs across browsers and permissions. Local mode is intentionally constrained compared with a frontier LLM. In production, add authentication, encrypted storage, rate limiting, and stronger document provenance.
