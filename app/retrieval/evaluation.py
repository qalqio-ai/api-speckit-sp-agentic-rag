"""Full-candidate calibration arithmetic; never approval or live quality evidence."""
import math

from app.ingestion.types import IngestionError


def calibration_summary(case,candidates):
    if len(candidates)>2048:raise IngestionError('scope_too_large')
    if any(type(p['score']) not in (int,float) or not math.isfinite(p['score']) or not -1<=p['score']<=1 for p in candidates):
        raise IngestionError('invalid_search_result')
    candidates=sorted(candidates,key=lambda p:(-p['score'],p['chunk_id']))
    expected=case['expected'].get('source_ids',[])
    matching=[(rank,p['score']) for rank,p in enumerate(candidates,1) if p['source_id'] in expected]
    return {'case_id':case['case_id'],'candidate_count':len(candidates),
            'maximum_candidate_score':candidates[0]['score'] if candidates else None,
            'best_expected_source_score':matching[0][1] if matching else None,
            'best_expected_source_rank':matching[0][0] if matching else None}


def propose_threshold(cases,summaries):
    """Return a candidate for human review only, or None on failed calibration."""
    by_id={s['case_id']:s for s in summaries}
    if len(by_id)!=len(summaries) or len({c['case_id'] for c in cases})!=len(cases) or set(by_id)!={c['case_id'] for c in cases}:
        return None
    positive=[];negative=[]
    for case in cases:
        summary=by_id[case['case_id']]
        if case['expected']['status']=='matched':
            score=summary['best_expected_source_score'];rank=summary['best_expected_source_rank']
            if score is None or type(rank) is not int or not 1<=rank<=3:return None
            positive.append(score)
        else:
            score=summary['maximum_candidate_score']
            if summary['candidate_count']==0 or score is None:return None
            negative.append(score)
        if type(score) not in (int,float) or not math.isfinite(score) or not -1<=score<=1:return None
    if not positive or not negative or max(negative)>=min(positive):return None
    low,high=max(negative),min(positive)
    candidate=low+(high-low)/2
    if candidate<=low:candidate=math.nextafter(low,high)
    return candidate if low<candidate<=high else None
