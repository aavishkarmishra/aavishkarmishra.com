"""Pull solved problems from Codeforces, AtCoder and LeetCode into public/cp/progress.json.

Keys match the checkbox keys in public/cp/index.html. CSES has no public per-user
API, so it stays manual on the page.
"""
import json, sys, datetime as dt, urllib.request, pathlib

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
    out['lcTotal'] = next(x['count'] for x in d['matchedUser']['submitStatsGlobal']['acSubmissionNum'] if x['difficulty'] == 'All')
except Exception as e:
    print('leetcode failed:', e, file=sys.stderr); ok = False; out['lcDays'] = prev.get('lcDays', []); out['lcTotal'] = prev.get('lcTotal')

OUT.write_text(json.dumps(out, indent=0) + '\n')
print(f"cf {len(out['cf'])}, atcoder {len(out['ac'])}, leetcode days {len(out['lcDays'])}, total {out.get('lcTotal')}")
sys.exit(0 if ok else 1)
