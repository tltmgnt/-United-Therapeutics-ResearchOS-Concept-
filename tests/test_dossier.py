import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from therapeutics_research.dossier import evaluate,evidence_binding,assay_summary
from therapeutics_research.researchos import assess
from therapeutics_research.bundle import write,verify,contents
from therapeutics_research._tect.core import replay
from therapeutics_research._tect.io import load

ROOT=Path(__file__).resolve().parents[1]


def sample(): return json.loads((ROOT/'examples/dossier.json').read_text())


def add_review(data,cid='summary-claim'):
    claim=next(c for c in data['claims'] if c['id']==cid)
    artifacts={e['id']:e for e in data['artifacts']}
    data['reviews'].append({'id':'review:'+cid,'claim':cid,'claim_version':claim['version'],
        'evidence_binding':evidence_binding(claim,artifacts,{c['id']:c for c in data['claims']}),'reviewer_id':'fictional-test-reviewer',
        'decision':'accept','reason':'Synthetic test declaration, not real expert review',
        'reviewed_at':'2026-11-07T12:00:00Z'})


class DossierTests(unittest.TestCase):
    def test_assay_hand_computed_and_review_missing(self):
        report=evaluate(sample())
        summary=report['assay']['summary']
        self.assertEqual(summary['groups']['control'],{'n':2,'mean':2,'sample_variance':2})
        self.assertEqual(summary['groups']['test']['mean'],5)
        self.assertEqual(summary['treatment_minus_control_mean'],3)
        self.assertIn('HUMAN_REVIEW_MISSING',report['claims']['summary-claim']['blockers'])
        self.assertFalse(report['scientific_validity_established'])
        self.assertFalse(report['company_affiliation_established'])

    def test_review_bound_to_claim_and_evidence(self):
        data=sample();add_review(data)
        self.assertEqual(evaluate(data)['claims']['summary-claim']['disposition'],'supported_declared')
        for change in ('version','statement','artifact','reviewtime'):
            bad=copy.deepcopy(data)
            if change=='version':bad['claims'][0]['version']=2
            if change=='statement':bad['claims'][0]['statement']='Changed statement'
            if change=='artifact':bad['artifacts'][0]['source_id']='changed-source'
            if change=='reviewtime':bad['reviews'][0]['reviewed_at']='2026-11-06T00:00:00Z'
            with self.subTest(change=change),self.assertRaises(ValueError):evaluate(bad)

    def test_integrity_context_and_expiry_remain_visible(self):
        for change,blocker in [('hash','ARTIFACT_DIGEST_MISMATCH'),('context','CONTEXT_MISMATCH'),('expiry','EVIDENCE_NOT_CURRENT')]:
            data=sample()
            if change=='hash':data['artifacts'][0]['sha256']='0'*64
            if change=='context':data['artifacts'][0]['context']['unit']='different_unit'
            if change=='expiry':data['artifacts'][0]['expires_at']=data['as_of']
            add_review(data)
            report=evaluate(data)
            self.assertIn('assay-data:'+blocker,report['claims']['summary-claim']['blockers'])
            self.assertEqual(report['assay']['status'],'blocked')

    def test_empty_evidence_and_adverse_review(self):
        data=sample();data['claims'][0]['evidence_ids']=[];add_review(data)
        self.assertIn('EVIDENCE_MISSING',evaluate(data)['claims']['summary-claim']['blockers'])
        data=sample();add_review(data);data['reviews'][0]['decision']='revise'
        self.assertIn('REVIEW_REVISE',evaluate(data)['claims']['summary-claim']['blockers'])

    def test_dependencies_recompute_and_cycles_rejected(self):
        data=sample();data['claims'].append({**data['claims'][0],'id':'downstream','dependencies':['summary-claim']})
        add_review(data,'downstream')
        report=evaluate(data)
        self.assertIn('DEPENDENCY_NOT_READY:summary-claim',report['claims']['downstream']['blockers'])
        add_review(data);report=evaluate(data)
        self.assertEqual(report['claims']['downstream']['disposition'],'supported_declared')
        changed=copy.deepcopy(data)
        changed['claims'][0]['version']=2
        changed['reviews']=[r for r in changed['reviews'] if r['claim']!='summary-claim']
        add_review(changed)
        with self.assertRaises(ValueError):evaluate(changed)  # Downstream review binds old upstream version.
        scenario,_,_=assess(data,report);controller=replay(scenario)
        event=controller.apply({'op':'revise','actor':'author','data':{'claim':'summary-claim',
            'statement':'Changed dataset','provenance':['new-input'],'confidence':.5,'assurance_scope':'Research only'}})
        self.assertEqual(event['outcome'],'PASS')
        self.assertEqual(controller.snapshot()['claims']['downstream']['state'],'UNVERIFIED')
        data['claims'][0]['dependencies']=['downstream']
        with self.assertRaises(ValueError):evaluate(data)

    def test_assay_malformed_and_single_replicate(self):
        valid=b'replicate_id,group,value\nc,control,1\nt,test,2\n'
        self.assertIsNone(assay_summary(valid,'control','test')['groups']['control']['sample_variance'])
        for raw in (b'id,group,value\nx,control,1\n',b'replicate_id,group,value\nx,control,nan\ny,test,1\n',
                    b'replicate_id,group,value\nx,control,1\nx,test,2\n',
                    b'replicate_id,group,value\nx,control,1\n',
                    b'replicate_id,group,value\nx,other,1\ny,test,2\n'):
            with self.assertRaises(ValueError):assay_summary(raw,'control','test')

    def test_invalid_schema_dates_and_bytes(self):
        for change in ('base64','date','unknown','duplicate','version','assay'):
            data=sample()
            if change=='base64':data['artifacts'][0]['content_base64']='!'
            if change=='date':data['expires_at']=data['as_of']
            if change=='unknown':data['context']['unknown']='x'
            if change=='duplicate':data['artifacts'].append(copy.deepcopy(data['artifacts'][0]))
            if change=='version':data['claims'][0]['version']=True
            if change=='assay':data['assay']['artifact_id']='missing'
            with self.subTest(change=change),self.assertRaises(ValueError):evaluate(data)

    def test_researchos_blocks_reproduction_and_rejects_poisoning(self):
        data=sample();add_review(data);scenario,ledger,report=assess(data,evaluate(data))
        self.assertEqual(ledger[-1]['outcome'],'UNCERTAIN')
        self.assertIn('SEPARATE_REPRODUCTION_MISSING',ledger[-1]['reasons'])
        self.assertFalse(report['clinical_use_authorized'])
        for change in ('hash','actor','expiry'):
            bad=copy.deepcopy(scenario);op=next(o for o in bad['operations'] if o['op']=='evidence')
            if change=='hash':op['data']['sha256']='0'*64
            if change=='actor':op['actor']='author'
            if change=='expiry':op['data']['expires_at']=data['as_of']
            self.assertTrue(any(e['outcome']=='FAIL' for e in replay(bad).ledger))

    def test_bundle_tamper_and_html_escape(self):
        data=sample();data['label']='<script>fictional</script>'
        self.assertNotIn('<script>',contents(data)['review.html'])
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run';write(data,output);verify(output)
            with self.assertRaises(FileExistsError):write(data,output)
            (output/'dossier.json').write_text('{}')
            with self.assertRaises(ValueError):verify(output)
            path=Path(tmp)/'bad.json';path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):load(path)

    def test_canonical_core_hashes(self):
        lock=json.loads((ROOT/'researchos-lock.json').read_text())
        for name,expected in lock['release']['modules'].items():
            self.assertEqual(hashlib.sha256((ROOT/'therapeutics_research/_tect'/name).read_bytes()).hexdigest(),expected)


if __name__=='__main__':unittest.main()
