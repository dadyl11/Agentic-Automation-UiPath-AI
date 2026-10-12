"""Testy kontraktów narzędzi Northstar (v1.3: osobne argumenty Out) na tenancie, folder Shared, robot serverless.

Użycie: python -I testy_narzedzi.py <ścieżka do UiPath_AI_Warsztat> [GTS|GSS|FKI|FIN ...]   (wymaga uip login)
Procesy wyszukuje po nazwie, więc nie trzeba aktualizować kluczy po ponownym utworzeniu procesu.
Wymaga: sprawy.csv w buckecie Northstar_Rejestr (GetTicketStatus), połączenia GenAI (FindKnownIssue).
FIN zapisuje do rejestr_spraw.csv wiersz TEST-V13 (drugi przebieg daje ALREADY_PROCESSED); usuń go przed 6B.
"""
import json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ROOT = sys.argv[1]
ONLY = set(sys.argv[2:]) or {'GTS', 'GSS', 'FKI', 'FIN'}
UIP = os.path.join(os.environ['APPDATA'], 'npm', 'uip.cmd')
z = {r['requestId']: r for r in json.load(open(os.path.join(ROOT, 'dane/zgloszenia.json'), encoding='utf8'))}
demo = {r['requestId']: r for r in json.load(open(os.path.join(ROOT, 'dane/przyklady_cwiczeniowe.json'), encoding='utf8'))}
pairs = json.load(open(os.path.join(ROOT, 'testy/pary_podobienstwa.json'), encoding='utf8'))
q = lambda r: r['subject'] + '\n' + r['body']
agent = json.dumps({"requestId": "TEST-V13", "category": "INCIDENT", "summary": "Test v1.3.", "nextAction": "DRAFT_REPLY",
                    "humanReview": False, "matchedIssueId": "", "sources": [], "draftReply": "Szkic.", "rationale": "Test."}, ensure_ascii=False)

# grupa, proces, nazwa, wejście, oczekiwane wyjścia (podzbiór)
CASES = [
    ('GTS', 'GetTicketStatus_Zapas', 'INC-104 właściciel', {'ticketId': 'INC-104', 'requesterEmail': 'celina@example.com'},
     {'out_status': 'FOUND', 'out_ticketStatus': 'IN_PROGRESS', 'out_sourceId': 'TICKET:INC-104'}),
    ('GTS', 'GetTicketStatus_Zapas', 'normalizacja', {'ticketId': ' inc-104 ', 'requesterEmail': 'Celina@Example.com'}, {'out_status': 'FOUND'}),
    ('GTS', 'GetTicketStatus_Zapas', 'INC-105', {'ticketId': 'INC-105', 'requesterEmail': 'anna@example.com'},
     {'out_status': 'FOUND', 'out_ticketStatus': 'RESOLVED', 'out_sourceId': 'TICKET:INC-105'}),
    ('GTS', 'GetTicketStatus_Zapas', 'INC-106 eta', {'ticketId': 'INC-106', 'requesterEmail': 'bartek@example.com'},
     {'out_status': 'FOUND', 'out_eta': '2026-11-20', 'out_sourceId': 'TICKET:INC-106'}),
    ('GTS', 'GetTicketStatus_Zapas', 'INC-999', {'ticketId': 'INC-999', 'requesterEmail': 'celina@example.com'}, {'out_status': 'NOT_FOUND', 'out_sourceId': ''}),
    ('GTS', 'GetTicketStatus_Zapas', 'cudza sprawa', {'ticketId': 'INC-104', 'requesterEmail': 'piotr@example.com'},
     {'out_status': 'FORBIDDEN', 'out_ticketStatus': '', 'out_lastUpdate': '', 'out_sourceId': ''}),
    ('GTS', 'GetTicketStatus_Zapas', 'awaria', {'ticketId': 'INC-104', 'requesterEmail': 'celina@example.com', 'simulateFailure': True},
     {'out_status': 'ERROR', 'out_message': 'Simulated timeout'}),
    ('GSS', 'GetServiceStatus_Zapas', 'portal', {'service': 'portal'}, {'out_status': 'FOUND', 'out_serviceStatus': 'DEGRADED', 'out_eta': '', 'out_sourceId': 'SERVICE:portal'}),
    ('GSS', 'GetServiceStatus_Zapas', 'sales', {'service': 'Sales '}, {'out_status': 'FOUND', 'out_serviceStatus': 'OPERATIONAL', 'out_sourceId': 'SERVICE:sales'}),
    ('GSS', 'GetServiceStatus_Zapas', 'unknown', {'service': 'unknown'}, {'out_status': 'NOT_FOUND', 'out_sourceId': ''}),
    ('GSS', 'GetServiceStatus_Zapas', 'awaria', {'service': 'portal', 'simulateFailure': True}, {'out_status': 'ERROR'}),
]
CASES += [('FKI', 'FindKnownIssue_Zapas', p['id'], {'query': p['left'], 'service': 'unknown'}, {'out_status': p['expected']}) for p in pairs]
CASES += [
    ('FKI', 'FindKnownIssue_Zapas', 'REQ-001', {'query': q(z['REQ-001']), 'service': 'sales'}, {'out_status': 'MATCH', 'out_issueId': 'KI-001', 'out_sourceId': 'KI-001'}),
    ('FKI', 'FindKnownIssue_Zapas', 'REQ-009', {'query': q(z['REQ-009']), 'service': 'billing'}, {'out_status': 'MATCH', 'out_issueId': 'KI-002'}),
    ('FKI', 'FindKnownIssue_Zapas', 'REQ-006', {'query': q(z['REQ-006']), 'service': 'portal'}, {'out_status': 'NO_MATCH', 'out_issueId': ''}),
    ('FKI', 'FindKnownIssue_Zapas', 'DEMO-02', {'query': q(demo['DEMO-02']), 'service': 'sales'}, {'out_status': 'NO_MATCH'}),
    ('FKI', 'FindKnownIssue_Zapas', 'pusty query', {'query': '  ', 'service': 'sales'}, {'out_status': 'ERROR', 'out_message': 'Missing query'}),
    ('FIN', 'FinalizeCase', 'zły finalStatus', {'requestId': 'TEST-V13-BAD', 'finalStatus': 'DONE'}, {'out_status': 'INVALID_INPUT', 'out_saved': False}),
    ('FIN', 'FinalizeCase', 'zapis', {'requestId': 'TEST-V13', 'finalStatus': 'READY_DRAFT', 'agentResultJson': agent}, {'out_saved': None}),
]


def uip(*args):
    out = subprocess.run([UIP, *args, '--output', 'json'], capture_output=True, text=True, encoding='utf8').stdout
    return json.loads(out[out.index('{'):])


procs = {p['Name']: p['Key'] for p in uip('or', 'processes', 'list', '--folder-path', 'Shared')['Data']}
run = [c for c in CASES if c[0] in ONLY]
keys = []
for grp, proc, name, inp, _ in run:
    for k, v in (('simulateFailure', False), ('runId', ''), ('agentResultJson', ''), ('reviewOutcome', ''), ('reviewedDraft', ''), ('reviewerId', '')):
        if proc == 'FinalizeCase' or k == 'simulateFailure':
            inp.setdefault(k, v)
    if proc == 'FinalizeCase':
        inp.pop('simulateFailure', None)
    r = uip('or', 'jobs', 'start', procs[proc], '--folder-path', 'Shared', '--runtime-type', 'Serverless',
            '--input-arguments', json.dumps(inp, ensure_ascii=False))
    keys.append(r['Data']['Jobs'][0]['Key'])

fails = 0
for (grp, proc, name, inp, exp), key in zip(run, keys):
    for _ in range(45):
        d = uip('or', 'jobs', 'get', key)['Data']
        if d['State'] in ('Successful', 'Faulted', 'Stopped'):
            break
        time.sleep(10)
    out = json.loads(d.get('OutputArguments') or '{}')
    ok = d['State'] == 'Successful' and all(v is None and k in out or out.get(k, '') == v for k, v in exp.items())
    fails += not ok
    shown = {k: v for k, v in out.items() if v not in ('', None)}
    print('%s | %-3s | %-20s | %s' % ('OK  ' if ok else 'FAIL', grp, name, json.dumps(shown, ensure_ascii=False) if d['State'] == 'Successful' else d.get('Info')))
sys.exit(1 if fails else 0)
