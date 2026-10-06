# InterviewForge AI — EDXSO AI Product Engineer Intern Assignment 3

A working AI-powered interview accelerator that turns a Job Description + Resume into a personalized, adaptive, voice-first mock interview and a detailed readiness report.

## Assignment coverage
- JD paste/upload: PDF, DOCX, TXT
- Resume paste/upload: PDF, DOCX, TXT
- Role understanding dashboard
- Candidate-vs-JD analysis and Job Fit score
- Screening → Competency → Deep-Dive interview levels
- Dynamic follow-up questions based on prior answers
- Browser speech-to-text using Web Speech API
- Browser text-to-speech for the AI interviewer
- Optional camera preview (video bonus); camera is NOT used for emotion scoring
- Question-level evaluation and actionable feedback
- Overall + competency scores
- Strengths, weaknesses, preparation gaps, readiness assessment
- Interview history stored in SQLite
- Optional real LLM integration with Groq or any OpenAI-compatible endpoint
- Local adaptive AI engine works with zero API keys; optional LLM mode provides free-form generation

## Why local mode exists
The assignment asks for a working product, and a reviewer should be able to run it without a paid dependency. The default local adaptive engine performs resume/JD extraction, role-specific question selection, evidence-based follow-ups, and structured evaluation. Optional LLM mode can be enabled with a Groq or OpenAI-compatible key for more free-form generation.

## Run on Windows
```powershell
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000

## Run tests
```powershell
python -m pytest -q
```
Expected: **7 passed**.

## Optional LLM mode
Copy `.env.example` to `.env` and set:
```text
AI_PROVIDER=groq
GROQ_API_KEY=your_key
```
Or use an OpenAI-compatible endpoint:
```text
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

## Voice
The browser implements speech-to-text with Web Speech API where supported and text-to-speech with `speechSynthesis`. Chrome/Edge on desktop are recommended. If browser speech recognition is unavailable, typing remains available and the AI interviewer still speaks questions.

## Demo assets
See `demo/ai_engineer_jd.txt` and `demo/candidate_resume.txt` for a reproducible end-to-end test.

## Architecture
```text
Browser UI
   ↓
FastAPI
   ├── document extraction
   ├── JD/resume analysis
   ├── adaptive interview engine
   ├── answer evaluation
   └── SQLite history
   ↓
Optional LLM provider (Groq/OpenAI-compatible)
```

## Key technical decisions
1. **Context-first prompting:** every question is generated from the analyzed JD + resume + previous turns rather than a fixed list.
2. **Evidence-aware analysis:** resume claims are surfaced as explicit probe points.
3. **Progressive difficulty:** screening emphasizes fit/motivation, competency focuses on technical/problem-solving depth, deep-dive challenges claims and adapts to the previous answer.
4. **Voice-first UX:** native browser STT/TTS avoids a paid voice dependency.
5. **No emotion scoring:** the camera is optional and not used to infer emotion, following the assignment's guidance.
6. **Fallback:** local adaptive mode ensures the product remains runnable without an API key.

## Deployment
The included `Dockerfile` and `render.yaml` are ready for a standard Render-style deployment. Use HTTPS in production so browser microphone/camera permissions work reliably.
## Screenshots
<img width="1897" height="902" alt="Screenshot 2026-10-06 222745" src="https://github.com/user-attachments/assets/b8aed2fd-4771-41a4-ab05-b35cd75c3936" />
<img width="1897" height="901" alt="Screenshot 2026-10-06 222951" src="https://github.com/user-attachments/assets/fba5a5d5-363a-4fb2-ae6c-1e73696a91d9" />
<img width="1175" height="882" alt="Screenshot 2026-10-06 223050" src="https://github.com/user-attachments/assets/d0d8fc4d-55ab-4ad9-8895-5952f8bc9f37" />
<img width="1896" height="812" alt="Screenshot 2026-10-06 223130" src="https://github.com/user-attachments/assets/fd9c6568-bed3-46b1-b2bd-660d4e7965a1" />




