import os, json, re, requests
from .config import AI_PROVIDER, GROQ_API_KEY, GROQ_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

SYSTEM="""You are an interview coach. Use only the supplied job description, resume and conversation. Never invent resume facts. Generate concise, role-specific interview questions and actionable evaluation. Always prefer probing a concrete claim or skill gap from the supplied evidence."""

def llm_enabled(): return (AI_PROVIDER=='groq' and bool(GROQ_API_KEY)) or (AI_PROVIDER=='openai' and bool(OPENAI_API_KEY))

def call_llm(prompt:str):
    if AI_PROVIDER=='groq' and GROQ_API_KEY:
        url='https://api.groq.com/openai/v1/chat/completions'; key=GROQ_API_KEY; model=GROQ_MODEL
    elif AI_PROVIDER=='openai' and OPENAI_API_KEY:
        url=OPENAI_BASE_URL.rstrip('/')+'/chat/completions'; key=OPENAI_API_KEY; model=OPENAI_MODEL
    else: return None
    payload={'model':model,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}], 'temperature':0.35}
    r=requests.post(url,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=payload,timeout=45)
    r.raise_for_status(); return r.json()['choices'][0]['message']['content']

def fallback_question(state, level):
    jd=state['analysis']['job']; c=state['analysis']['candidate']; turns=state.get('turns',[])
    asked={t['question'] for t in turns}
    name=state.get('candidate_name','Candidate')
    options=[]
    if level in ('screening',1):
        options=[]
        if c['relevant_projects']: options.append(f"Walk me through {c['relevant_projects'][0][:120]}. What problem did you solve and what did you personally own?")
        if c['claims_to_probe']: options.append(f"Your resume says: '{c['claims_to_probe'][0][:140]}'. How did you measure that result?")
        options.append(f"Why are you interested in the {jd['role_title']} role, and which part of your background best prepares you for it?")
        options.append(f"Which requirement for {jd['role_title']} do you think is your strongest match, and why?")
    elif level in ('competency',2):
        opts=[]
        skill=(jd['required_skills'] or c['key_skills'] or ['the core technical stack'])[0]
        opts.append(f"Explain how you would use {skill} in a production-quality solution for this role. What trade-offs would you consider?")
        if c['missing_skills']: opts.append(f"The role expects {c['missing_skills'][0]}. How would you close that gap quickly, and how would you prove you learned it?")
        if c['relevant_projects']: opts.append(f"In your project experience, what was the hardest technical decision you made and what alternatives did you reject?")
        opts.append("Describe a debugging or failure scenario you handled. What evidence did you use to isolate the root cause?")
        options=opts
    else:
        options=[]
        if turns:
            prev=turns[-1]
            ans=prev.get('answer','')
            # adaptive based on answer quality and specific content
            if re.search(r'\baccuracy\b',ans,re.I):
                options.append("You mentioned accuracy. If the classes were highly imbalanced, would accuracy still be appropriate? What would you use instead and why?")
            elif re.search(r'\bAPI\b|REST',ans,re.I):
                options.append("You mentioned the API. How would you handle authentication, timeouts, retries, and idempotency under failure?")
            elif re.search(r'\bRAG\b|retriev',ans,re.I):
                options.append("You mentioned RAG. How would you diagnose a case where retrieval is relevant but the final answer is still incorrect?")
            elif len(ans.split())<25:
                options.append("Your answer is quite high-level. Give me one concrete example, the metric you used, and the trade-off you faced.")
        if c['claims_to_probe']:
            options.append(f"Let's pressure-test this claim from your resume: '{c['claims_to_probe'][0][:130]}'. What would I see if I inspected the implementation?")
        options.append("What is the riskiest assumption in your approach, and how would you validate it before deployment?")
        options.append("Suppose production traffic doubles tomorrow. Which component would you expect to fail first, and how would you redesign it?")
    for q in options:
        if q not in asked:return q
    return options[0]

def next_question(state, level):
    context=json.dumps({'job':state['analysis']['job'],'candidate':state['analysis']['candidate'],'turns':state.get('turns',[])})
    if llm_enabled():
        prompt=f"Generate the next {level} interview question for this candidate. It must use the supplied resume/JD and previous answers. Do not ask an already-covered generic question. Return one question only. Context: {context}"
        try:
            out=call_llm(prompt)
            if out: return out.strip().strip('"')
        except Exception:
            pass
    return fallback_question(state,level)
