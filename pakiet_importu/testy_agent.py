"""Uruchamia SupportAgent (uip agent debug) dla wybranych zgłoszeń i porównuje wynik z testy/oczekiwane_wyniki.json.

Użycie (z katalogu pakiet_importu): python -I testy_agent.py REQ-001 REQ-003 ...
Wynik bierze z trace (span agentOutput), bo debug może zakończyć się stanem Suspended, gdy agent czeka na job narzędzia.
"""
import json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.join(HERE, '..', 'UiPath_AI_Warsztat')
SOL = os.path.join(HERE, 'Northstar_Agent')
UIP = os.path.join(os.environ['APPDATA'], 'npm', 'uip.cmd')
tickets = {r['requestId']: r for r in json.load(open(os.path.join(WS, 'dane/zgloszenia.json'), encoding='utf8'))}
expected = {r['requestId']: r for r in json.load(open(os.path.join(WS, 'testy/oczekiwane_wyniki.json'), encoding='utf8'))}


def run(args):
    p = subprocess.run([UIP, *args, '--output', 'json'], capture_output=True, text=True, encoding='utf8', cwd=SOL)
    out = p.stdout
    return json.loads(out[out.index('{'):]) if '{' in out else {}


def spans(trace_id):
    for _ in range(18):
        d = run(['traces', 'spans', 'get', trace_id]).get('Data') or []
        d = d if isinstance(d, list) else d.get('Spans', d.get('spans', []))
        parsed = []
        for s in d:
            a = s.get('Attributes') or s.get('attributes') or {}
            parsed.append(json.loads(a) if isinstance(a, str) else a)
        if any(a.get('type') == 'agentOutput' for a in parsed):
            return parsed
        time.sleep(10)
    return parsed


fails = 0
for rid in sys.argv[1:]:
    t = tickets[rid]
    inp = {k: t[k] for k in ('requestId', 'requesterEmail', 'subject', 'body', 'service')}
    res = run(['agent', 'debug', 'SupportAgent', '--inputs', json.dumps(inp, ensure_ascii=False), '--timeout', '400'])
    trace = (res.get('Data') or {}).get('TraceId')
    sp = spans(trace) if trace else []
    tools = [a.get('toolName') for a in sp if a.get('type') in ('toolCall', 'contextGroundingTool')]
    types = sorted({a.get('type') for a in sp if a.get('type')})
    out = next((a.get('output') for a in sp if a.get('type') == 'agentOutput'), None) or {}
    e = expected[rid]
    checks = {
        'category': out.get('category') == e['expectedCategory'],
        'nextAction': out.get('nextAction') == e['expectedNextAction'],
        'humanReview': out.get('humanReview') == e['expectedHumanReview'],
        'matchedIssueId': out.get('matchedIssueId', '') == (e.get('expectedMatchedIssueId') or ''),
        'tools': set(e.get('requiredTools') or []) <= set(tools),
    }
    ok = all(checks.values())
    fails += not ok
    print('%s | %s | %s/%s (oczek. %s/%s) | narzędzia %s (wymagane %s) | sources %s | trace %s' % (
        'OK  ' if ok else 'FAIL', rid, out.get('category'), out.get('nextAction'), e['expectedCategory'], e['expectedNextAction'],
        tools, e.get('requiredTools'), out.get('sources'), trace))
    print('      spany:', types)
    if not ok:
        print('      nie zgadza się:', [k for k, v in checks.items() if not v], '| rationale:', (out.get('rationale') or '')[:250])
    json.dump({'input': inp, 'tools': tools, 'output': out, 'trace': trace},
              open(os.path.join(HERE, 'dist', 'agent_%s.json' % rid), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.exit(1 if fails else 0)
