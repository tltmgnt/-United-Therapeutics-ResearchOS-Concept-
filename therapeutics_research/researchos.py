"""Translate research dossier declarations into the canonical controller."""
import base64
import hashlib
from ._tect.core import Controller, canonical, policy_default


def assess(data, dossier):
    policy = policy_default()
    policy['minimum_density'] = .001  # Explicit local policy, not calibrated confidence.
    controller = Controller(policy, data['as_of'])
    operations = []
    def apply(op, actor, payload):
        operation = {'op': op, 'actor': actor, 'data': payload}
        operations.append(operation)
        return controller.apply(operation)
    cases = {c['id']: c for c in data['claims']}
    for cid in dossier['claim_order']:
        case = cases[cid]
        apply('register', 'author', {'id': cid, 'statement': case['statement'],
              'provenance': ['local:input.json', 'evidence-binding:'+dossier['claims'][cid]['evidence_binding']],
              'confidence': .5, 'assurance_scope': 'Declared research dossier checks only'})
    for cid in dossier['claim_order']:
        for dep in cases[cid]['dependencies']:
            apply('relation', 'validator', {'source': dep, 'target': cid, 'relation': 'depends_on'})
    for cid in dossier['claim_order']:
        if controller.snapshot()['claims'][cid]['state'] == 'GENERATED':
            apply('transition', 'validator', {'claim': cid, 'target': 'UNVERIFIED'})
        result = dossier['claims'][cid]
        content = canonical({'input_sha256': dossier['input_sha256'], 'case': cid,
                             'declared_claim_version': cases[cid]['version'], 'review_result': result,
                             'scope': 'Supplied dossier and review declarations, not independent scientific validation'}).encode()
        apply('evidence', 'validator', {'id': 'review:'+cid, 'claim': cid, 'claim_version': 1,
              'kind': 'validation', 'result': 'PASS' if result['disposition'] == 'supported_declared' else 'UNCERTAIN',
              'source': 'local:dossier-snapshot', 'method': 'domain-adapter-v1',
              'run_id': 'local-dossier-check', 'group': 'same-declared-study',
              'weight': 1, 'quality': 1, 'reliability': 1, 'independence': .5,
              'observed_at': data['as_of'], 'expires_at': data['expires_at'],
              'content_base64': base64.b64encode(content).decode(),
              'sha256': hashlib.sha256(content).hexdigest()})
        if apply('transition', 'validator', {'claim': cid, 'target': 'SUPPORTED'})['outcome'] == 'PASS':
            apply('transition', 'validator', {'claim': cid, 'target': 'ADVERSARIAL_TEST'})
            apply('transition', 'validator', {'claim': cid, 'target': 'REPRODUCED'})
    if any(e['outcome'] == 'FAIL' for e in controller.ledger):
        raise ValueError('Unexpected ResearchOS translation failure')
    scenario = {'schema_version': 1, 'as_of': data['as_of'], 'policy': policy, 'operations': operations}
    return scenario, controller.ledger, controller.report()
