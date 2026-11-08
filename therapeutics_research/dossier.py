"""Bounded evidence integrity and declared-context checks, not biomedical validation."""
import base64
import csv
import hashlib
import io
import math
from statistics import mean, variance
from ._tect.core import fields, text, date, digest


def context(value):
    fields(value, ('species','model','endpoint','unit'))
    for item in value.values(): text(item)


def identifiers(values, maximum):
    if type(values) is not list or len(values)>maximum: raise ValueError('Bounded identifier list required')
    for value in values: text(value)
    if len(set(values))!=len(values): raise ValueError('Duplicate identifier')


def records(values, maximum):
    if type(values) is not list or not 1<=len(values)<=maximum: raise ValueError('Nonempty bounded records required')
    result={}
    for value in values:
        if type(value) is not dict: raise ValueError('Object records required')
        identifier=text(value.get('id'))
        if identifier in result: raise ValueError('Duplicate record ID')
        result[identifier]=value
    return result


def evidence_binding(claim, artifacts, claims):
    """Bind reviews to the complete referenced artifact declarations and case version."""
    upstream={}
    pending=list(claim['dependencies'])
    while pending:
        cid=pending.pop()
        if cid in upstream:continue
        dependency=claims[cid]
        upstream[cid]={'claim':dependency,'artifacts':[artifacts[e] for e in sorted(dependency['evidence_ids'])]}
        pending.extend(dependency['dependencies'])
    return digest({'claim':claim,'artifacts':[artifacts[e] for e in sorted(claim['evidence_ids'])],
                   'upstream':upstream})


def assay_summary(content, control, treatment):
    text(control);text(treatment)
    if control==treatment: raise ValueError('Two distinct assay groups required')
    reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig'),newline=''))
    if reader.fieldnames!=['replicate_id','group','value']: raise ValueError('Exact assay CSV columns required')
    groups={control:[],treatment:[]};seen=set()
    for row in reader:
        if len(seen)>=10000 or None in row or any(v is None for v in row.values()): raise ValueError('Malformed or oversized assay')
        identifier=text(row['replicate_id']);group=text(row['group'])
        if identifier in seen or group not in groups: raise ValueError('Duplicate replicate or unexpected group')
        try: value=float(row['value'])
        except (TypeError,ValueError) as exc: raise ValueError('Numeric assay value required') from exc
        if not math.isfinite(value) or abs(value)>1e12: raise ValueError('Bounded finite assay value required')
        seen.add(identifier);groups[group].append(value)
    if any(not v for v in groups.values()): raise ValueError('Both assay groups require observations')
    summary={k:{'n':len(v),'mean':mean(v),'sample_variance':variance(v) if len(v)>1 else None} for k,v in groups.items()}
    return {'groups':summary,'treatment_minus_control_mean':summary[treatment]['mean']-summary[control]['mean'],
            'scope':'Descriptive supplied replicate table only; no independence, causal effect, efficacy or safety established'}


def evaluate(data):
    fields(data, ('schema_version','label','as_of','expires_at','context','claims','artifacts','reviews','assay'))
    if type(data['schema_version']) is not int or data['schema_version']!=1: raise ValueError('Unsupported schema')
    text(data['label']);context(data['context'])
    as_of=date(data['as_of'])
    if date(data['expires_at'])<=as_of: raise ValueError('Expiry must follow assessment time')
    claims,artifacts=records(data['claims'],32),records(data['artifacts'],64)
    checked,decoded={},{}
    total=0
    for eid,item in artifacts.items():
        fields(item, ('id','kind','source_id','context','observed_at','expires_at','content_base64','sha256'))
        if item['kind'] not in ('protocol','raw_data','analysis','literature','replication'): raise ValueError('Unknown artifact kind')
        text(item['source_id']);context(item['context'])
        if type(item['content_base64']) is not str or len(item['content_base64'])>90000: raise ValueError('Bounded base64 artifact required')
        try: content=base64.b64decode(item['content_base64'],validate=True)
        except Exception as exc: raise ValueError('Invalid base64 evidence') from exc
        if not content or len(content)>65536: raise ValueError('Evidence must contain 1 to 65536 bytes')
        total+=len(content)
        if total>1024*1024: raise ValueError('Total evidence exceeds 1 MiB')
        if type(item['sha256']) is not str or len(item['sha256'])!=64 or any(c not in '0123456789abcdef' for c in item['sha256']):
            raise ValueError('SHA-256 reference required')
        observed,expiry=date(item['observed_at']),date(item['expires_at'])
        if expiry<=observed: raise ValueError('Invalid evidence validity interval')
        blockers=[]
        if hashlib.sha256(content).hexdigest()!=item['sha256']: blockers.append('ARTIFACT_DIGEST_MISMATCH')
        if item['context']!=data['context']: blockers.append('CONTEXT_MISMATCH')
        if not observed<=as_of<expiry: blockers.append('EVIDENCE_NOT_CURRENT')
        checked[eid]={'blockers':blockers,'byte_count':len(content),'kind':item['kind']}
        decoded[eid]=content
    for cid,claim in claims.items():
        fields(claim, ('id','version','statement','dependencies','evidence_ids'))
        text(claim['statement']);identifiers(claim['dependencies'],32);identifiers(claim['evidence_ids'],64)
        if type(claim['version']) is not int or claim['version']<1: raise ValueError('Positive claim version required')
        if any(d not in claims or d==cid for d in claim['dependencies']): raise ValueError('Unknown/self dependency')
        if any(e not in artifacts for e in claim['evidence_ids']): raise ValueError('Unknown evidence reference')
    order,visiting,visited=[],set(),set()
    def visit(cid):
        if cid in visiting: raise ValueError('Cyclic claim dependencies')
        if cid in visited:return
        visiting.add(cid)
        for dep in claims[cid]['dependencies']:visit(dep)
        visiting.remove(cid);visited.add(cid);order.append(cid)
    for cid in claims:visit(cid)
    if type(data['reviews']) is not list or len(data['reviews'])>128: raise ValueError('Bounded reviews required')
    reviews,review_ids={},set()
    for item in data['reviews']:
        fields(item, ('id','claim','claim_version','evidence_binding','reviewer_id','decision','reason','reviewed_at'))
        rid=text(item['id']);text(item['reviewer_id']);text(item['reason'])
        cid=item['claim']
        if rid in review_ids or cid not in claims or cid in reviews: raise ValueError('Duplicate/unknown claim review')
        if type(item['claim_version']) is not int or item['claim_version']!=claims[cid]['version'] or item['evidence_binding']!=evidence_binding(claims[cid],artifacts,claims):
            raise ValueError('Stale claim or evidence-bound review')
        if item['decision'] not in ('accept','revise','reject'): raise ValueError('Unknown review decision')
        reviewed=date(item['reviewed_at'])
        if reviewed>as_of or any(date(artifacts[e]['observed_at'])>reviewed for e in claims[cid]['evidence_ids']):
            raise ValueError('Review must follow referenced observations and not be future dated')
        review_ids.add(rid);reviews[cid]=item
    results={}
    for cid in order:
        claim=claims[cid];blockers=[]
        if not claim['evidence_ids']:blockers.append('EVIDENCE_MISSING')
        for eid in claim['evidence_ids']:blockers.extend(eid+':'+b for b in checked[eid]['blockers'])
        if cid not in reviews:blockers.append('HUMAN_REVIEW_MISSING')
        elif reviews[cid]['decision']!='accept':blockers.append('REVIEW_'+reviews[cid]['decision'].upper())
        for dep in claim['dependencies']:
            if results[dep]['disposition']!='supported_declared':blockers.append('DEPENDENCY_NOT_READY:'+dep)
        results[cid]={'claim_version':claim['version'],'evidence_binding':evidence_binding(claim,artifacts,claims),
                      'disposition':'supported_declared' if not blockers else 'review_required','blockers':blockers}
    assay=None
    if data['assay'] is not None:
        fields(data['assay'], ('artifact_id','control_group','treatment_group'))
        eid=data['assay']['artifact_id']
        if eid not in artifacts or artifacts[eid]['kind']!='raw_data': raise ValueError('Assay requires captured raw_data artifact')
        assay=({'status':'blocked','blockers':checked[eid]['blockers']} if checked[eid]['blockers'] else
               {'status':'computed','summary':assay_summary(decoded[eid],data['assay']['control_group'],data['assay']['treatment_group'])})
    return {'schema_version':1,'input_sha256':digest(data),'claim_order':order,'claims':results,
            'artifacts':checked,'assay':assay,'scientific_validity_established':False,
            'company_affiliation_established':False,'clinical_use_authorized':False,
            'limits':['Integrity and context checks do not verify evidence relevance or scientific validity',
                      'Source, model, organism, reviewer identity and independence are supplied declarations',
                      'Descriptive assay differences are not efficacy, safety or causal estimates',
                      'No clinical, dosing, transplant-allocation or equipment decision is authorized']}
