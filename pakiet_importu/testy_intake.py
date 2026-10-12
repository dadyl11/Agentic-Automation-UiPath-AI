"""Testy zapasu Intake_AI_Zapas (ćw. 1A/1B) na tenancie, folder Shared, robot serverless.

Użycie: python -I testy_intake.py <ścieżka do UiPath_AI_Warsztat>   (wymaga uip login)
Wynik czyta z logu joba: "requestId | category | team | summary" albo "requestId | NEEDS_DETAILS | ...".
Streszczenia (1A) oceń wzrokiem według tabeli kroku 5 w instrukcji.
"""
import json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ROOT = sys.argv[1]
UIP = os.path.join(os.environ['APPDATA'], 'npm', 'uip.cmd')
rows = json.load(open(os.path.join(ROOT, 'dane/zgloszenia.json'), encoding='utf8'))
rows += json.load(open(os.path.join(ROOT, 'dane/przyklady_cwiczeniowe.json'), encoding='utf8'))
z = {r['requestId']: r for r in rows}

# requestId, oczekiwana kategoria, zespół (1B krok 5); TEST-EMPTY to pusty body z 1A
CASES = [('REQ-001', 'INCIDENT', 'APPLICATION_SUPPORT'), ('REQ-003', 'STATUS_REQUEST', 'SERVICE_DESK'),
         ('REQ-004', 'ACCESS_REQUEST', 'ACCESS_TEAM'), ('REQ-005', 'HOW_TO', 'SERVICE_DESK'),
         ('REQ-006', 'FEATURE_REQUEST', 'PRODUCT'), ('REQ-007', 'OTHER', 'MANUAL_TRIAGE'),
         ('DEMO-01', 'ACCESS_REQUEST', 'ACCESS_TEAM'), ('TEST-EMPTY', 'NEEDS_DETAILS', 'Brak treści zgłoszenia')]


def uip(*args):
    out = subprocess.run([UIP, *args, '--output', 'json'], capture_output=True, text=True, encoding='utf8').stdout
    return json.loads(out[out.index('{'):])


proc = [p['Key'] for p in uip('or', 'processes', 'list', '--folder-path', 'Shared')['Data'] if p['Name'] == 'Intake_AI_Zapas'][0]
keys = []
for rid, _, _ in CASES:
    r = z.get(rid, {'requestId': rid, 'requesterEmail': 'test@example.com', 'subject': 'Test', 'body': '', 'service': 'portal'})
    inp = {k: r[k] for k in ('requestId', 'requesterEmail', 'subject', 'body', 'service')}
    keys.append(uip('or', 'jobs', 'start', proc, '--folder-path', 'Shared', '--runtime-type', 'Serverless',
                    '--input-arguments', json.dumps(inp, ensure_ascii=False))['Data']['Jobs'][0]['Key'])

fails = 0
for (rid, cat, team), key in zip(CASES, keys):
    for _ in range(45):
        d = uip('or', 'jobs', 'get', key)['Data']
        if d['State'] in ('Successful', 'Faulted', 'Stopped'):
            break
        time.sleep(10)
    logs = uip('or', 'jobs', 'logs', key).get('Data') or []
    line = next((l['Message'] for l in logs if str(l.get('Message', '')).startswith(rid + ' | ')), '')
    parts = [p.strip() for p in line.split(' | ')]
    ok = d['State'] == 'Successful' and parts[1:3] == [cat, team]
    fails += not ok
    print('%s | %-10s | %s' % ('OK  ' if ok else 'FAIL', rid, line or d.get('Info')))
sys.exit(1 if fails else 0)
