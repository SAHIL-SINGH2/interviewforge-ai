import re
from collections import Counter

SKILL_TAXONOMY={
 'python':'technical','java':'technical','javascript':'technical','typescript':'technical','c++':'technical','sql':'technical',
 'fastapi':'technical','flask':'technical','django':'technical','react':'technical','next.js':'technical','node.js':'technical',
 'rest apis':'technical','apis':'technical','git':'technical','docker':'technical','kubernetes':'technical','aws':'technical','gcp':'technical','azure':'technical',
 'machine learning':'technical','deep learning':'technical','llm':'technical','llms':'technical','rag':'technical','embeddings':'technical','vector database':'technical',
 'pytorch':'technical','tensorflow':'technical','scikit-learn':'technical','pandas':'technical','numpy':'technical','nlp':'technical','computer vision':'technical',
 'data structures':'technical','algorithms':'technical','system design':'technical','database':'technical','mongodb':'technical','postgresql':'technical','mysql':'technical',
 'communication':'behavioral','problem solving':'behavioral','leadership':'behavioral','teamwork':'behavioral','collaboration':'behavioral','adaptability':'behavioral','learning ability':'behavioral','ownership':'behavioral','decision making':'behavioral',
}

BEHAVIORAL={'communication','problem solving','leadership','teamwork','collaboration','adaptability','learning ability','ownership','decision making','stakeholder management'}

def normalize(s:str)->str:
    s=re.sub(r'\s+',' ',s or '').strip()
    return s

def sentences(text:str):
    return [normalize(x) for x in re.split(r'(?<=[.!?])\s+|\n+',text) if normalize(x)]

def extract_skills(text:str):
    low=text.lower(); found=[]
    for s in SKILL_TAXONOMY:
        if s in low:
            found.append(s)
    return sorted(set(found))

def section(text, names):
    lines=[normalize(x) for x in text.splitlines() if normalize(x)]
    starts=[]
    for i,l in enumerate(lines):
        if any(re.search(rf'\b{re.escape(n)}\b',l,re.I) for n in names): starts.append(i)
    if not starts:return []
    i=starts[0]; out=[]
    for l in lines[i+1:i+16]:
        if re.match(r'^(education|experience|projects|skills|certifications|achievements|summary|objective|responsibilities|requirements|qualifications)\s*$',l,re.I): break
        out.append(l)
    return out

def analyze_jd(text:str):
    low=text.lower(); skills=extract_skills(text)
    role=''
    m=re.search(r'(?:position|role|job title|title)\s*[:\-]\s*([^\n]+)',text,re.I)
    if m: role=normalize(m.group(1))
    if not role:
        for pat in [r'((?:senior|junior|entry[- ]level|intern|associate)?\s*(?:ai|ml|machine learning|software|backend|frontend|full[- ]stack|data|product|devops|cloud|python)[\w /&-]*(?:engineer|developer|analyst|manager|intern))']:
            m=re.search(pat,text,re.I)
            if m: role=normalize(m.group(1)); break
    if not role: role='Target Role'
    req=section(text,['requirements','required qualifications','must have','required skills'])
    pref=section(text,['preferred qualifications','preferred skills','nice to have'])
    resp=section(text,['responsibilities','what you\'ll do','key responsibilities'])
    tech=[s for s in skills if SKILL_TAXONOMY.get(s)=='technical']
    beh=[s for s in skills if SKILL_TAXONOMY.get(s)=='behavioral']
    experience=[]
    for x in sentences(text):
        if re.search(r'\b(?:years?|experience|internship|internships)\b',x,re.I): experience.append(x)
    quals=[]
    for x in sentences(text):
        if re.search(r'\b(?:degree|bachelor|master|b\.tech|bsc|mtech|cgpa|qualification|eligible)\b',x,re.I): quals.append(x)
    keywords=sorted(set(re.findall(r'\b[A-Za-z][A-Za-z0-9+.#-]{3,}\b',text)))
    important=skills[:]
    for k in re.findall(r'\b(?:RAG|LLM|API|SQL|Python|Machine Learning|System Design|AWS|Docker)\b',text,re.I):
        if k.lower() not in [x.lower() for x in important]: important.append(k)
    return {
      'role_title':role,'key_responsibilities':resp[:10] or sentences(text)[:6],'required_skills':tech[:12],
      'preferred_skills':[s for s in [*extract_skills('\n'.join(pref))] if s not in tech][:10],
      'technical_competencies':tech[:12],'behavioral_competencies':beh[:8],
      'experience_expectations':experience[:6],'important_keywords':important[:18],
      'important_concepts':sorted(set([x for x in ['retrieval','embeddings','model evaluation','apis','data pipelines','deployment','testing','system design','cloud'] if x in low])),
      'key_qualifications':quals[:8]
    }

def extract_candidate_bullets(text:str):
    lines=[normalize(x) for x in text.splitlines() if normalize(x)]
    return [x.lstrip('•-*').strip() for x in lines if x.startswith(('-', '*', '•')) or len(x)>35]

def analyze_candidate(resume:str,jd:dict):
    skills=extract_skills(resume)
    low=resume.lower()
    jdskills=jd['required_skills']+jd['preferred_skills']
    matched=[s for s in jdskills if s in skills]
    missing=[s for s in jd['required_skills'] if s not in skills]
    weak=[]
    for s in matched:
        if len(re.findall(re.escape(s),low))==1: weak.append(s)
    strengths=[]
    for s in matched[:8]: strengths.append(f'{s.title()} is evidenced in the resume.')
    bullets=extract_candidate_bullets(resume)
    exp=[x for x in sentences(resume) if re.search(r'\b(?:intern|developer|engineer|worked|built|developed|implemented)\b',x,re.I)][:8]
    projects=[x for x in bullets if re.search(r'\b(?:built|developed|implemented|designed|created|deployed)\b',x,re.I) and not re.search(r'\b(?:b\.tech|bachelor|master)\b',x,re.I)][:8]
    achievements=[x for x in bullets if re.search(r'\b(?:award|winner|achievement|rank|percent|%|improved|reduced|increased|selected)\b',x,re.I)][:6]
    claims=[]
    for x in bullets:
        if re.search(r'\b(?:%|improved|reduced|increased|optimized|led|designed|deployed|built)\b',x,re.I): claims.append(x)
    base=45
    if jdskills:
        base += round(50*len(matched)/max(1,len(jdskills)))
    exp_bonus=min(5,len(exp))
    fit=min(98,base+exp_bonus)
    return {
      'key_skills':skills[:18],'relevant_experience':exp,'relevant_projects':projects,'relevant_achievements':achievements,
      'strengths':strengths or ['Resume contains role-relevant evidence that can be explored in the interview.'],
      'missing_skills':missing[:10],'weak_areas':weak[:8],
      'claims_to_probe':claims[:8],
      'prep_areas':missing[:6] + weak[:4],
      'job_fit':fit,
      'fit_buckets':{
          'strong_match':matched[:8],
          'partial_match':weak[:5],
          'missing_or_weak':missing[:8]
      }
    }

def full_analysis(jd_text,resume_text):
    jd=analyze_jd(jd_text); cand=analyze_candidate(resume_text,jd)
    return {'job':jd,'candidate':cand}
