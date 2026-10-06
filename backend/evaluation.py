import re

def evaluate_answer(question, answer, analysis):
    jd=analysis['job']; cand=analysis['candidate']; words=answer.split(); low=answer.lower()
    score=45
    if len(words)>=25: score+=10
    if len(words)>=60: score+=8
    if any(k in low for k in jd['required_skills'][:8]): score+=12
    if re.search(r'\b(?:because|therefore|trade-off|tradeoff|decision|metric|measure|test|validate|debug|monitor|result|impact)\b',low): score+=12
    if re.search(r'\b(?:example|project|internship|experience|built|implemented)\b',low): score+=8
    if re.search(r'\b(?:I|we)\b',answer): score+=3
    score=min(97,score)
    communication=min(95,45 + (15 if len(words)>=25 else 5) + (15 if len(words)>=60 else 0) + (10 if len(words)>15 and not answer.count('...') else 0))
    technical=min(95,45 + (20 if any(k in low for k in jd['required_skills'][:10]) else 0) + (15 if re.search(r'\b(?:metric|trade-off|tradeoff|architecture|latency|scaling|testing|validation)\b',low) else 0))
    role_fit=min(95,50 + (20 if any(k in low for k in jd['required_skills'][:10]) else 0) + (10 if re.search(r'\b(?:project|experience|role|team|user|impact)\b',low) else 0))
    problem=min(95,48 + (22 if re.search(r'\b(?:root cause|debug|trade-off|decision|because|why|how)\b',low) else 0) + (10 if len(words)>40 else 0))
    depth=min(95,45 + (15 if len(words)>=40 else 0) + (15 if re.search(r'\b(?:edge case|failure|limitation|alternative|trade-off|metric|evaluation)\b',low) else 0))
    behavioral=min(95,50 + (15 if re.search(r'\b(?:team|conflict|learned|mistake|feedback|ownership|lead)\b',low) else 0))
    confidence=min(95,50 + (15 if len(words)>=30 else 0) + (10 if answer.count('I ')>=1 else 0))
    strengths=[]; improve=[]
    if len(words)>=40: strengths.append('You gave enough detail to show reasoning rather than a one-line claim.')
    else: improve.append('Add a concrete example, decision and outcome instead of staying at summary level.')
    if re.search(r'\b(?:metric|impact|result|%|seconds|ms|users)\b',low): strengths.append('You included measurable or evaluation-oriented evidence.')
    else: improve.append('Quantify impact or name the evaluation signal you used.')
    if re.search(r'\b(?:because|trade-off|alternative|why)\b',low): strengths.append('You explained reasoning and trade-offs.')
    else: improve.append('Explain why you chose this approach and what alternative you rejected.')
    ideal='A stronger answer would connect the claim to a specific action, technical reasoning, evidence/metric, trade-off, and outcome.'
    return {'score':score,'role_fit':role_fit,'technical_knowledge':technical,'problem_solving':problem,'communication':communication,'confidence':confidence,'depth_of_understanding':depth,'behavioral_fit':behavioral,'what_was_good':strengths,'what_could_be_better':improve,'ideal_direction':ideal}

def final_report(turns, analysis):
    if not turns:
        return {'overall_score':0,'competencies':{},'strengths':[],'weaknesses':['No interview answers yet.'],'prep_gaps':analysis['candidate']['prep_areas'],'readiness':'Not Ready','question_feedback':[]}
    keys=['score','role_fit','technical_knowledge','problem_solving','communication','confidence','depth_of_understanding','behavioral_fit']
    avg=sum(t['evaluation']['score'] for t in turns)/len(turns)
    comps={k:round(sum(t['evaluation'][k] for t in turns)/len(turns)) for k in keys[1:]}
    strengths=[]; weaknesses=[]
    for t in turns:
        strengths.extend(t['evaluation']['what_was_good']); weaknesses.extend(t['evaluation']['what_could_be_better'])
    strengths=list(dict.fromkeys(strengths))[:5] or ['Completed the interview and demonstrated role-relevant evidence.']
    weaknesses=list(dict.fromkeys(weaknesses))[:5]
    prep=list(dict.fromkeys(analysis['candidate']['prep_areas'] + (['quantifying impact','technical trade-offs','structured behavioral examples'] if weaknesses else [])))[:8]
    if avg>=85 and analysis['candidate']['job_fit']>=75: readiness='Strong Candidate'
    elif avg>=75: readiness='Interview Ready'
    elif avg>=60: readiness='Needs Preparation'
    else: readiness='Not Ready'
    return {'overall_score':round(avg),'competencies':comps,'strengths':strengths,'weaknesses':weaknesses,'prep_gaps':prep,'readiness':readiness,
            'question_feedback':[{'question':t['question'],'answer':t['answer'],'assessment':t['evaluation']['score'],'what_was_good':t['evaluation']['what_was_good'],'what_could_be_better':t['evaluation']['what_could_be_better'],'ideal_direction':t['evaluation']['ideal_direction']} for t in turns]}
