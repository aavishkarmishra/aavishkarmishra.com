"""Pull solved problems from Codeforces, AtCoder and LeetCode into public/cp/progress.json.

Keys match the checkbox keys in public/cp/index.html. CSES has no public per-user
API, so it stays manual on the page.
"""
import json, re, sys, datetime as dt, urllib.request, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / 'public' / 'cp' / 'progress.json'
CF, AC, LC = 'aavishkar', 'aavishkarmishra', 'aavishkarmishra'
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

def get(url, data=None, headers={}):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', **headers})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

prev = json.loads(OUT.read_text()) if OUT.exists() else {}
out = {'updated': dt.datetime.now(IST).strftime('%Y-%m-%d %H:%M IST')}
ok = True

try:
    subs = get(f'https://codeforces.com/api/user.status?handle={CF}')['result']
    out['cf'] = sorted({f"cf{s['problem']['contestId']}{s['problem']['index']}" for s in subs if s['verdict'] == 'OK' and 'contestId' in s['problem']})
    hist = get(f'https://codeforces.com/api/user.rating?handle={CF}')['result']
    out['cfRating'] = {'rating': hist[-1]['newRating'] if hist else 0, 'peak': max([0] + [h['newRating'] for h in hist]), 'contests': len(hist)}
except Exception as e:
    print('codeforces failed:', e, file=sys.stderr); ok = False; out['cf'] = prev.get('cf', []); out['cfRating'] = prev.get('cfRating')

try:
    subs, since = [], 0
    while True:  # the API returns at most 500 per call
        page = get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={AC}&from_second={since}')
        subs += page
        if len(page) < 500: break
        since = page[-1]['epoch_second'] + 1
    out['ac'] = sorted({'ac' + s['problem_id'] for s in subs if s['result'] == 'AC'})
except Exception as e:
    print('atcoder failed:', e, file=sys.stderr); ok = False; out['ac'] = prev.get('ac', [])

try:
    q = {'query': 'query($u:String!){matchedUser(username:$u){submitStatsGlobal{acSubmissionNum{difficulty count}}} recentAcSubmissionList(username:$u,limit:20){titleSlug timestamp}}', 'variables': {'u': LC}}
    d = get('https://leetcode.com/graphql', json.dumps(q).encode(), {'Content-Type': 'application/json', 'Referer': 'https://leetcode.com'})['data']
    # The API only returns the last 20 ACs, so days accumulate across runs.
    days = set(prev.get('lcDays', []))
    days |= {dt.datetime.fromtimestamp(int(s['timestamp']), IST).strftime('%Y-%m-%d') for s in d['recentAcSubmissionList']}
    out['lcDays'] = sorted(days)
    out['lcSlugs'] = sorted(set(prev.get('lcSlugs', [])) | {s['titleSlug'] for s in d['recentAcSubmissionList']})
    out['lcTotal'] = next(x['count'] for x in d['matchedUser']['submitStatsGlobal']['acSubmissionNum'] if x['difficulty'] == 'All')
except Exception as e:
    print('leetcode failed:', e, file=sys.stderr); ok = False
    out['lcDays'] = prev.get('lcDays', []); out['lcTotal'] = prev.get('lcTotal'); out['lcSlugs'] = prev.get('lcSlugs', [])

# Upcoming contests, IST. Rounds already shown stay, so the page keeps its history.
def ist(ts): return dt.datetime.fromtimestamp(ts, IST)
contests = {c['id']: c for c in prev.get('contests', [])}
try:
    for c in get('https://codeforces.com/api/contest.list?gym=false')['result']:
        if c['phase'] != 'BEFORE' or not re.search(r'Div\. [1-4]|Educational', c['name']): continue
        a, b = ist(c['startTimeSeconds']), ist(c['startTimeSeconds'] + c['durationSeconds'])
        contests[f"cf{c['id']}"] = {'id': f"cf{c['id']}", 'judge': 'cf', 'name': c['name'], 'date': a.strftime('%Y-%m-%d'),
                                    'time': a.strftime('%H:%M'), 'end': b.strftime('%H:%M'), 'url': f"https://codeforces.com/contest/{c['id']}"}
except Exception as e:
    print('codeforces contests failed:', e, file=sys.stderr); ok = False
try:
    req = urllib.request.Request('https://atcoder.jp/contests/?lang=en', headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req, timeout=30).read().decode()
    up = page.split('Upcoming Contests')[1].split('Recent Contests')[0]
    for row in up.split('<tr')[1:]:
        m = re.search(r'iso=(\d{8}T\d{4}).*?/contests/(abc\d+|arc\d+)">([^<]+)</a>.*?<td class="text-center">(\d+):(\d+)</td>', row, re.S)
        if not m: continue
        a = dt.datetime.strptime(m.group(1), '%Y%m%dT%H%M').replace(tzinfo=dt.timezone(dt.timedelta(hours=9))).astimezone(IST)
        b = a + dt.timedelta(hours=int(m.group(4)), minutes=int(m.group(5)))
        contests[m.group(2)] = {'id': m.group(2), 'judge': 'ac', 'name': m.group(3).strip(), 'date': a.strftime('%Y-%m-%d'),
                                'time': a.strftime('%H:%M'), 'end': b.strftime('%H:%M'), 'url': f'https://atcoder.jp/contests/{m.group(2)}'}
except Exception as e:
    print('atcoder contests failed:', e, file=sys.stderr); ok = False
out['contests'] = sorted(contests.values(), key=lambda c: (c['date'], c['time']))

OUT.write_text(json.dumps(out, indent=0) + '\n')
print(f"cf {len(out['cf'])}, atcoder {len(out['ac'])}, leetcode days {len(out['lcDays'])}, total {out.get('lcTotal')}, contests {len(out['contests'])}")
sys.exit(0 if ok else 1)
