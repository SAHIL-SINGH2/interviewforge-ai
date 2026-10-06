from backend.analysis import full_analysis
from backend.evaluation import evaluate_answer, final_report
from backend.ai_engine import fallback_question
from backend.extract import extract_file

def fixtures():
    jd=open('demo/ai_engineer_jd.txt',encoding='utf-8').read(); resume=open('demo/candidate_resume.txt',encoding='utf-8').read(); return jd,resume

def test_analysis_extracts_role_and_skills():
    jd,res=fixtures(); a=full_analysis(jd,res); assert 'Python' not in []
    assert 'python' in a['candidate']['key_skills']; assert a['job']['role_title'].lower().startswith('ai engineer')

def test_job_fit_not_empty():
    jd,res=fixtures(); a=full_analysis(jd,res); assert 0<a['candidate']['job_fit']<=100

def test_personalized_question_uses_resume_or_role():
    jd,res=fixtures(); a=full_analysis(jd,res); s={'analysis':a,'candidate_name':'Aarav','turns':[]}; q=fallback_question(s,'screening'); assert any(k in q.lower() for k in ['fastapi','rag','api','project','resume','llm'])

def test_dynamic_followup_changes_with_answer():
    jd,res=fixtures(); a=full_analysis(jd,res); s={'analysis':a,'candidate_name':'Aarav','turns':[{'question':'x','answer':'We used RAG and retrieval quality was measured with accuracy.','level':'deep-dive'}]}; q=fallback_question(s,'deep-dive'); assert 'accuracy' in q.lower() or 'rag' in q.lower() or 'retrieval' in q.lower()

def test_evaluation_produces_competencies():
    jd,res=fixtures(); a=full_analysis(jd,res); e=evaluate_answer('Explain how you built the FastAPI service.', 'I built a FastAPI service with validation and measured malformed requests. We considered retries and testing.', a); assert e['score']>50 and e['technical_knowledge']>50

def test_report_readiness():
    jd,res=fixtures(); a=full_analysis(jd,res); turns=[]
    for i in range(6):
        ev=evaluate_answer('Explain Python APIs and trade-offs.', 'I built REST APIs in Python, tested validation, measured malformed requests and explained the trade-offs.', a)
        turns.append({'level':'screening','question':'Q','answer':'A'*50,'evaluation':ev})
    r=final_report(turns,a); assert 'readiness' in r and 'competencies' in r

def test_file_text_extraction():
    txt='hello resume'; assert extract_file('demo.txt',txt.encode())=='hello resume'
