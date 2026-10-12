"""Testy FinalizeCase (rejestr CSV) na tenancie. Uruchamia joby po kolei, bo każdy dopisuje do tego samego pliku.

Użycie: python -I testy_finalize.py   (wymaga uip login; zaczyna od pustego rejestru)
"""
import json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")

UIP = os.path.join(os.environ['APPDATA'], 'npm', 'uip.cmd')
BUCKET = '454870b1-e27e-4b33-a839-a086edf0179b'

agent_001 = {"requestId": "REQ-001", "category": "INCIDENT", "summary": "Eksport raportu sprzedaży za 60 dni kończy się błędem 500.",
             "nextAction": "DRAFT_REPLY", "humanReview": False, "matchedIssueId": "KI-001", "sources": ["KI-001", "KB-004"],
             "draftReply": "Dzień dobry; to znany problem \"KI-001\".\nPodziel raport na okresy do 31 dni.", "rationale": "Objawy zgodne z KI-001."}
agent_004 = {"requestId": "REQ-004", "category": "ACCESS_REQUEST", "summary": "Prośba o uprawnienia administratora.",
             "nextAction": "HUMAN_REVIEW", "humanReview": True, "matchedIssueId": "", "sources": ["KB-002"],
             "draftReply": "Prośba przekazana do weryfikacji.", "rationale": "Zmiana uprawnień wymaga człowieka."}

cases = [
    ('REQ-001 zapis', {'requestId': 'REQ-001', 'agentResultJson': json.dumps(agent_001, ensure_ascii=False), 'finalStatus': 'READY_DRAFT'}, 'SAVED'),
    ('REQ-004 po przeglądzie', {'requestId': 'REQ-004', 'agentResultJson': json.dumps(agent_004, ensure_ascii=False), 'finalStatus': 'REVIEWED_DRAFT',
                                'reviewOutcome': 'Approve', 'reviewedDraft': 'Twoja prośba została przekazana do weryfikacji. Nie nadaliśmy jeszcze dostępu.', 'reviewerId': 'kmisko'}, 'SAVED'),
    ('TECH-03 REQ-001 ponownie', {'requestId': 'REQ-001', 'agentResultJson': json.dumps(agent_001, ensure_ascii=False), 'finalStatus': 'READY_DRAFT'}, 'ALREADY_PROCESSED'),
    ('Zły finalStatus', {'requestId': 'REQ-099', 'finalStatus': 'DONE'}, 'INVALID_INPUT'),
    ('Niepoprawny JSON agenta', {'requestId': 'REQ-007', 'agentResultJson': 'to nie jest JSON', 'finalStatus': 'VALIDATION_FAILED'}, 'SAVED'),
]


def uip(*args):
    out = subprocess.run([UIP, *args, '--output', 'json'], capture_output=True, text=True, encoding='utf8').stdout
    return json.loads(out[out.index('{'):])


PROCESS = {r['Name']: r['Key'] for r in uip('or', 'processes', 'list', '--folder-path', 'Shared')['Data']}['FinalizeCase']
fails = 0
for name, inp, expected in cases:
    for k in ('runId', 'agentResultJson', 'reviewOutcome', 'reviewedDraft', 'reviewerId'):
        inp.setdefault(k, '')
    key = uip('or', 'jobs', 'start', PROCESS, '--folder-path', 'Shared', '--runtime-type', 'Serverless',
              '--input-arguments', json.dumps(inp, ensure_ascii=False))['Data']['Jobs'][0]['Key']
    for _ in range(40):
        d = uip('or', 'jobs', 'get', key)['Data']
        if d['State'] in ('Successful', 'Faulted', 'Stopped'):
            break
        time.sleep(8)
    out = json.loads(d.get('OutputArguments') or '{}')
    res = {'status': out.get('out_status'), 'saved': out.get('out_saved'), 'finalStatus': out.get('out_finalStatus'), 'runId': out.get('out_runId'), 'message': out.get('out_message')}
    ok = d['State'] == 'Successful' and res.get('status') == expected
    fails += not ok
    print('%s | %-26s | oczek. %-17s | wynik %s' % ('OK  ' if ok else 'FAIL', name, expected, json.dumps(res, ensure_ascii=False)))

sys.exit(1 if fails else 0)
