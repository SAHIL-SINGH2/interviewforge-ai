from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
import json, sqlite3
from .extract import extract_file
from .analysis import full_analysis
from .ai_engine import next_question, llm_enabled
from .evaluation import evaluate_answer, final_report
from .config import DATA_DIR, APP_NAME, DB_PATH

app=FastAPI(title=APP_NAME)
BASE=Path(__file__).resolve().parents[1]
app.mount('/static', StaticFiles(directory=BASE/'static'), name='static')

class StartInterview(BaseModel):
    analysis: dict
    candidate_name: str='Candidate'
    levels: list=['screening','competency','deep-dive']
class AnswerRequest(BaseModel):
    state: dict
    answer: str

@app.get('/')
def home(): return FileResponse(BASE/'static'/'index.html')

@app.get('/api/health')
def health(): return {'ok':True,'app':APP_NAME,'ai_mode':'llm' if llm_enabled() else 'local-adaptive'}

@app.post('/api/analyze')
async def analyze(jd_text: str=Form(''), resume_text: str=Form(''), jd_file: UploadFile|None=File(None), resume_file: UploadFile|None=File(None)):
    if jd_file:
        jd_text=extract_file(jd_file.filename, await jd_file.read())
    if resume_file:
        resume_text=extract_file(resume_file.filename, await resume_file.read())
    if len(jd_text.strip())<80 or len(resume_text.strip())<80:
        raise HTTPException(400,'Please provide a JD and resume with enough content.')
    result=full_analysis(jd_text,resume_text)
    return {'ok':True,'analysis':result,'ai_mode':'llm' if llm_enabled() else 'local-adaptive'}

@app.post('/api/interview/start')
def start_interview(req: StartInterview):
    state={'session_id':str(uuid4()),'candidate_name':req.candidate_name or 'Candidate','analysis':req.analysis,'turns':[],'level_index':0,'level_order':req.levels,'current_level':'screening'}
    q=next_question(state,'screening')
    state['current_question']=q
    return {'state':state,'question':q}

@app.post('/api/interview/answer')
def answer(req: AnswerRequest):
    st=req.state; level=st.get('current_level','screening')
    q=st.get('current_question')
    if not q: raise HTTPException(400,'No active question.')
    ans=req.answer.strip()
    if not ans: raise HTTPException(400,'Answer cannot be empty.')
    ev=evaluate_answer(q,ans,st['analysis'])
    st['turns'].append({'level':level,'question':q,'answer':ans,'evaluation':ev})
    # progression: 3 questions per level, then advance
    count=sum(1 for t in st['turns'] if t['level']==level)
    advanced=False
    if count>=3 and st['level_index']<len(st['level_order'])-1:
        st['level_index']+=1; advanced=True
        st['current_level']=st['level_order'][st['level_index']]
    elif count>=3 and st['level_index']>=len(st['level_order'])-1:
        st['current_level']='complete'
    if st['current_level']=='complete':
        report=final_report(st['turns'],st['analysis'])
        return {'state':st,'evaluation':ev,'complete':True,'report':report,'next_question':None,'advanced':advanced}
    q2=next_question(st,st['current_level'])
    st['current_question']=q2
    return {'state':st,'evaluation':ev,'complete':False,'report':None,'next_question':q2,'advanced':advanced}

@app.get('/api/history')
def history():
    DATA_DIR.mkdir(exist_ok=True)
    if not DB_PATH.exists(): return {'sessions':[]}
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row
    rows=con.execute('SELECT id, candidate, role, overall_score, readiness, created_at FROM sessions ORDER BY id DESC LIMIT 20').fetchall(); con.close()
    return {'sessions':[dict(r) for r in rows]}

@app.post('/api/history/save')
def save_history(payload: dict):
    DATA_DIR.mkdir(exist_ok=True)
    con=sqlite3.connect(DB_PATH)
    con.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, role TEXT, overall_score INTEGER, readiness TEXT, created_at TEXT)')
    con.execute('INSERT INTO sessions(candidate,role,overall_score,readiness,created_at) VALUES(?,?,?,?,datetime("now"))',(payload.get('candidate','Candidate'),payload.get('role','Role'),payload.get('overall_score',0),payload.get('readiness','Unknown')))
    con.commit(); con.close(); return {'ok':True}
