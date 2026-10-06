# Test Report

## Automated
- 7 tests pass.
- JD and resume analysis extracts role and skills.
- Job Fit produces a bounded score.
- Personalized question references role/resume context.
- Deep-dive follow-up reacts to an answer containing RAG/accuracy/retrieval.
- Evaluation produces technical/communication/problem-solving scores.
- Final report produces readiness and competency results.
- TXT upload extraction works.

## Manual test cases
1. Paste the demo JD and resume → Analyze → verify Role and Job Fit.
2. Upload `demo/ai_engineer_jd.txt` and `demo/candidate_resume.txt` → same analysis.
3. Start screening → question references resume/project.
4. Answer by typing → next question appears.
5. Click Speak question → browser TTS speaks.
6. Click Start speaking → transcript appears in answer box (Chrome/Edge).
7. Complete 3 screening questions → level changes to COMPETENCY.
8. Give a short answer in deep-dive → AI asks for a concrete metric/example.
9. Complete all 9 questions → Results screen shows overall score, competencies, feedback, strengths, weaknesses and readiness.
10. Click Camera → local preview appears; confirm no emotion score is shown.
11. Refresh History → completed interview summary appears in SQLite history.
12. Run with no API keys → local adaptive mode still works.
