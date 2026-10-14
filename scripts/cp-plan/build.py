import json, re, os, pathlib, datetime as dt, calendar
os.chdir(pathlib.Path(__file__).resolve().parent)
from urllib.parse import quote
from curriculum import WEEKS, CS
from roadmap import STAGES, RULES

START = dt.date(2026, 9, 28)
NAME = {i: t for s in CS for i, t in s['tasks']}

# ---- Codeforces picks: unsolved, not special, most-solved first, never reused ----
P = json.load(open('probs.json'))['result']
stats = {(s['contestId'], s['index']): s['solvedCount'] for s in P['problemStatistics']}
tried = {(s['problem'].get('contestId'), s['problem']['index']) for s in json.load(open('status.json'))['result']}
used = set()
def cf_pick(lo, hi, tags, min_cid=1700):
    c = [p for p in P['problems'] if p.get('rating') and lo <= p['rating'] <= hi and p['contestId'] >= min_cid
         and (p['contestId'], p['index']) not in tried and (p['contestId'], p['index']) not in used
         and '*special' not in p['tags'] and (not tags or set(tags) & set(p['tags']))]
    c.sort(key=lambda p: -stats.get((p['contestId'], p['index']), 0))
    p = c[0]; used.add((p['contestId'], p['index']))
    return {'k': f"cf{p['contestId']}{p['index']}", 't': f"CF {p['contestId']}{p['index']} · {p['name']}", 'r': p['rating'],
            'u': f"https://codeforces.com/problemset/problem/{p['contestId']}/{p['index']}"}
def furl(tags, lo, hi): return 'https://codeforces.com/problemset?order=BY_SOLVED_DESC&tags=' + quote(','.join(tags + [f'{lo}-{hi}']))

# ---- AtCoder picks: ABC 200+, by difficulty band, newest first ----
AP = json.load(open('ac_problems.json')); AM = json.load(open('ac_models.json'))
apool = sorted([(p['contest_id'], p['id'], p['name'], AM[p['id']]['difficulty']) for p in AP
                if p['contest_id'].startswith('abc') and int(p['contest_id'][3:]) >= 100 and p['id'] in AM and AM[p['id']].get('difficulty') is not None
                and p['problem_index'] in 'CDEF'], reverse=True)
aused = set()
def ac_pick(lo, hi):
    # widen the band when a level runs dry; the pool of ABC C–F is small
    for pad in range(0, 1200, 200):
        for cid, pid, name, d in apool:
            if lo - pad <= d <= hi + pad and pid not in aused:
                aused.add(pid)
                return {'k': 'ac' + pid, 't': f"AtCoder {pid.upper().replace('_', ' ')} · {name}", 'r': f'diff {d}', 'u': f'https://atcoder.jp/contests/{cid}/tasks/{pid}'}
    raise SystemExit(f'no atcoder problem near {lo}-{hi}')

def task(k, t, u=None, n=None):
    d = {'k': k, 't': t}
    if u: d['u'] = u
    if n: d['n'] = n
    return d
cses = lambda i: task(f'cses{i}', f'CSES · {NAME[i]}', f'https://cses.fi/problemset/task/{i}')
read = lambda t, u: task('read:' + u, 'Read: ' + t, u)
LOG = lambda d: task(f'log{d}', 'Log each idea you missed in one line (box below)')
LC = lambda d: task(f'lc{d}', 'LeetCode daily question', 'https://leetcode.com/problemset/')
UP = lambda d: task(f'up{d}', 'Upsolve: if you got stuck, read the editorial, close it, then code it yourself')

# Known contests (IST). Everything later: check the contest pages.
CF_LIVE = {dt.date(2026, 10, 7): ('CF Round 2275 (Div 3), live 20:05–22:35. Your first rated round back. Aim A–C', 'https://codeforces.com/contest/2275'),
           dt.date(2026, 10, 10): ('CF Round 2271 (Div 1 + 2), live 20:35–23:35. Combined round, aim A–B', 'https://codeforces.com/contest/2271'),
           dt.date(2026, 10, 17): ('CF Round 2261 (Div 1 + 2), live 20:05–23:05', 'https://codeforces.com/contest/2261')}
CF_LATE = {dt.date(2026, 10, 11): ('CF Round 2274 (Div 2), 00:05 tonight. Optional: only if you can sleep in', 'https://codeforces.com/contest/2274')}
ABC_LIVE = {dt.date(2026, 10, 3): ('ABC 478, live 17:30–19:10. Your first live contest back. Aim A–C', 'https://atcoder.jp/contests/abc478'),
            dt.date(2026, 10, 11): ('ABC 479, live 17:30–19:10 (Sunday this week)', 'https://atcoder.jp/contests/abc479'),
            dt.date(2026, 10, 17): ('ABC 480, live 17:30–19:10. CF round at 20:05 too: do both if you feel fresh', 'https://atcoder.jp/contests/abc480')}
def abc_item(d):
    if d in ABC_LIVE: return task(f'abc{d}', *ABC_LIVE[d])
    return task(f'abc{d}', 'AtCoder ABC, live 17:30 if scheduled (check the page; some weeks it is Sunday)', 'https://atcoder.jp/contests/')

OCT6_LC = ['find-first-and-last-position-of-element-in-sorted-array', 'search-insert-position', 'first-bad-version', 'valid-perfect-square', 'find-peak-element']
PRE = {'cses1617', 'cses1618', 'cses1754', 'cses1072', 'cses1092'} | {'lcp:' + s for s in OCT6_LC}
# Extra blocks on a date: work done off-plan, and problems that fill a pattern gap (see pat in curriculum.py).
EXTRA = {'2026-10-06': (5, 'Off plan', 'Binary search practice, done', [task('lcp:' + s, 'LeetCode · ' + s.replace('-', ' ').capitalize(), f'https://leetcode.com/problems/{s}/') for s in OCT6_LC]),
         '2026-10-09': (5, 'Any free slot', 'Pattern gap: binary search on the answer', [cses(1620), cses(1085)]),
         '2026-10-16': (5, 'Any free slot', 'Pattern gap: DSU', [cses(1676)])}
GAP_KEYS = {i['k'] for _, _, _, items in EXTRA.values() for i in items}
STRIVER = json.load(open('striver.json'))
STRIVER_FROM, STRIVER_MIN = dt.date(2026, 11, 1), 180
# Days already worked keep their exact content; their problems are never picked again.
BASE_PIN = {'2026-09-28': json.load(open('pin_2026-09-28.json'))}
PINNED = dict(BASE_PIN)
# Freeze every day up to today from the last published page, so a rebuild never rewrites days already worked.
_prev = pathlib.Path(__file__).resolve().parents[2] / 'public' / 'cp' / 'index.html'
if _prev.exists():
    _m = re.search(r'const DATA = (\{.*?\});\n', _prev.read_text(), re.S)
    for _d in json.loads(_m.group(1))['days'] if _m else []:
        if _d['date'] <= dt.date.today().isoformat() and _d.get('content'):
            PINNED.setdefault(_d['date'], _d['content'])
# Generation only knows the base pin; later freezes override at the end, so picks for future days never move.
PINNED_KEYS = {i['k'] for p in BASE_PIN.values() for blk in p['blocks'] for i in blk['items']}
for k in PINNED_KEYS:
    if k.startswith('cf'): used.add((int(re.match(r'cf(\d+)', k).group(1)), re.match(r'cf\d+(\w+)', k).group(1)))
    if k.startswith('ac'): aused.add(k[2:])
CFP = {(p['contestId'], p['index']): p for p in P['problems']}
def gap_item(g):
    if g[0] == 'lc': return task('lcp:' + g[1], 'LeetCode · ' + g[2], f'https://leetcode.com/problems/{g[1]}/')
    p = CFP[(g[1], g[2])]
    return {'k': f'cf{g[1]}{g[2]}', 't': f"CF {g[1]}{g[2]} · {p['name']}", 'r': p.get('rating'), 'u': f'https://codeforces.com/problemset/problem/{g[1]}/{g[2]}'}
for w in WEEKS:
    for g in w['gap']:
        if g[0] == 'cf': used.add((g[1], g[2]))
days = []
filters = []
striver_q = list(STRIVER)
refreshed = set()
def refresh(wi, iso):
    # Re-solve problems from 2 and 3 weeks back, so older patterns come round again. CSES first; speed weeks only have CF.
    def pool(w):
        items = [i for x in days if x['content'] and x['content']['week'] == w for b in x['content']['blocks'] for i in b['items']] if w >= 0 else []
        cses_ = [i for i in items if i['k'].startswith('cses') and i['k'] not in refreshed]
        return cses_ or [i for i in items if re.match(r'cf\d', i['k']) and i['k'] not in refreshed]
    a, b = pool(wi - 2), pool(wi - 3)
    picks = list({x['k']: x for x in [*a[len(a) // 2:len(a) // 2 + 1], *a[-1:], *b[-1:]]}.values())
    refreshed.update(x['k'] for x in picks)
    return [task(f'rv{iso}:{x["k"]}', 'Re-solve from a blank file · ' + x['t'], x.get('u'), 'Skip it if you never solved it. Under 15 minutes means the pattern stuck.') for x in picks]
def striver_block():
    # Pack the sheet in order into ~3 hour Sundays by its own time estimates.
    items, mins = [], 0
    while striver_q and (not items or mins + striver_q[0]['min'] <= STRIVER_MIN):
        x = striver_q.pop(0); mins += x['min']; items.append(task(x['k'], f"{x['topic']} · {x['t']}", x['u']))
    if items: items[0]['n'] = 'Solved it before? Re-solve in 10 minutes, code only. Done early? Start next Sunday\'s list.'
    return B(1, '09:00–12:00', 'Striver sheet, interview style: 25 min timer, say the approach first', items)
B = lambda o, time, label, items: {'o': o, 'time': time, 'label': label, 'items': items}
for wi, w in enumerate(WEEKS):
    lo, hi, tags = w['cf']
    ft, ftags, flo, fhi, ftarget = w['flt']
    fkey = f'w{wi}'
    filters.append({'key': fkey, 'week': wi, 'title': ft, 'lo': flo, 'hi': fhi, 'tags': ftags, 'target': ftarget, 'url': furl(ftags, flo, fhi)})
    speed = w['name'].startswith('Speed week')
    cs = [i for i in w['cses'] if f'cses{i}' not in PRE | PINNED_KEYS | GAP_KEYS]; rd = w['rd']
    # Spread the week's CSES over its weekdays that aren't pinned, at most 3 a day.
    free = [wd for wd in range(5) if (START + dt.timedelta(wi * 7 + wd)).isoformat() not in BASE_PIN]
    per = -(-len(cs) // len(free)) if cs else 0
    chunk = {wd: cs[j * per:(j + 1) * per][:3] for j, wd in enumerate(free)}
    for wd in range(7):
        d = START + dt.timedelta(wi * 7 + wd); iso = d.isoformat()
        # content: shifts forward over off days. fixed: stays on its date.
        if wd < 5:
            today_cs = chunk.get(wd, [])
            today_rd = rd[wd::5] if rd else []
            if speed:
                a = B(1, '09:00–10:30', 'Virtual contest', [task(f'virt{iso}', 'Virtual Div 2 you have not seen (2h). Start at 09:00 sharp', 'https://codeforces.com/contests')])
                bb = B(2, '10:45–12:00', 'Upsolve', [task(f'upv{iso}', 'Upsolve the first two problems you missed')])
            else:
                a = B(1, '09:00–10:30', 'Learn + CSES' if today_cs else 'Codeforces', [read(t, u) for t, u in today_rd] + [cses(i) for i in today_cs] + ([] if today_cs else [cf_pick(lo, hi, tags)]))
                bb = B(2, '10:45–12:00', 'Codeforces', [cf_pick(lo, hi, tags), UP(iso)])
            if wd == 2 and w['gap'] and not speed: gap_blk = B(5, 'Any free slot', 'Pattern gap', [gap_item(g) for g in w['gap']])
            else: gap_blk = None
            ev = B(4, '20:00–22:00', 'Evening block', [task(f'flt{fkey}_{iso}', f'Filter · {ft} {flo}–{fhi}, one problem', furl(ftags, flo, fhi), 'Sorted by most solved. Skip green ones.'), ac_pick(*w['ac'])])
            content = [a, bb, ev] + ([gap_blk] if gap_blk else [])
            fixed = [B(3, '13:30–14:00', 'LeetCode', [LC(iso)])]
            if d in CF_LIVE: fixed.append(B(4, '20:00–22:00', 'Live round tonight. This replaces the evening block', [task(f'cf{d}', *CF_LIVE[d])]))
            fixed.append(B(6, '22:00', 'Wind down', [LOG(iso)]))
        elif wd == 5:
            upv = [task(f'upv{iso}', 'Upsolve the first problem you missed in the virtual')]
            if d + dt.timedelta(1) >= STRIVER_FROM and striver_q:
                upv += refresh(wi, iso) + [task(f'plan{iso}', 'Read next week in this tracker')]
            content = [B(1, '09:00–11:00', 'Virtual contest', [task(f'virt{iso}', 'Virtual Div 2 you have not seen (2h)', 'https://codeforces.com/contests')]),
                       B(2, '11:15–12:45', 'Upsolve + re-solve older weeks' if len(upv) > 1 else 'Upsolve', upv)]
            fixed = [B(3, 'After lunch', 'LeetCode', [LC(iso)]), B(4, '17:30–19:10', 'AtCoder', [abc_item(d)])]
            if d in CF_LIVE: fixed.append(B(5, 'Evening', 'Codeforces live', [task(f'cf{d}', *CF_LIVE[d])]))
            fixed.append(B(6, '22:00', 'Wind down', [LOG(iso)]))
        else:
            review = refresh(wi, iso) + [task(f'plan{iso}', 'Read next week in this tracker')]
            if w['stage'] >= 2: review.append(task(f'div1{iso}', 'This week\'s Codeforces: register for Div 1 if you are 1900+, otherwise Div 2 or Edu. Div 1 + 2 combined rounds count either way', 'https://codeforces.com/contests'))
            if d >= STRIVER_FROM and striver_q:
                # Weekly review moved to Saturday; Sunday morning is Striver's sheet.
                content = [striver_block(), B(2, '12:00–12:45', 'Upsolve', [task(f'ups{iso}', 'Upsolve ABC D and E, and the Codeforces round if you did one')] + [x for x in review if x['k'].startswith('div1')])]
            else:
                content = [B(1, '09:30–11:30', 'Upsolve', [task(f'ups{iso}', 'Upsolve ABC D and E, and the Codeforces round if you did one')]),
                           B(2, '11:30–12:30', 'Re-solve older weeks', review)]
            if w['stage'] >= 2: content.append(B(4, '17:30–19:30', 'AtCoder ARC', [task(f'arc{iso}', 'ARC, live if scheduled (usually Sunday 17:30 IST). Aim A–B', 'https://atcoder.jp/contests/')]))
            fixed = [B(3, 'After lunch', 'LeetCode', [LC(iso)])]
            if d in ABC_LIVE: fixed.append(B(4, '17:30–19:10', 'AtCoder', [abc_item(d)]))
            if d in CF_LATE: fixed.append(B(5, 'Late night', 'Codeforces (optional)', [task(f'cf{d}', *CF_LATE[d])]))
            if d.month != (d + dt.timedelta(7)).month:
                fixed.append(B(5, 'Evening', 'Month retro', [
                    task(f'retro{iso}', 'Compare rating and solved count to a month ago. Read the log. Name the 2 topics you missed most'),
                    task(f'retro2{iso}', 'Check the stage exit checklist on the Roadmap tab. If the plan and your rating disagree, ask for a regenerated plan')]))
            fixed.append(B(6, 'Afternoon', 'Rest', [task(f'rest{iso}', 'Take the afternoon off. Rest is part of the plan')]))
            fixed.append(B(7, '22:00', 'Wind down', [LOG(iso)]))
        if iso in PINNED:
            content = PINNED[iso]['blocks']
        if iso in EXTRA and not any(b['label'] == EXTRA[iso][2] for b in content):
            content = content + [B(*EXTRA[iso])]
        days.append({'date': iso, 'dow': d.strftime('%a'), 'label': d.strftime('%b %-d'), 'cls': 'wd' if wd < 5 else 'we',
                     'fixed': fixed, 'content': {'week': wi, 'blocks': content}})
# Buffer dates with only fixed blocks, so content pushed back by off days still has somewhere to land.
for i in range(60):
    d = START + dt.timedelta(len(WEEKS) * 7 + i); iso = d.isoformat(); wd = d.weekday()
    fixed = [B(3, '13:30–14:00' if wd < 5 else 'After lunch', 'LeetCode', [LC(iso)])]
    if wd == 5: fixed.append(B(4, '17:30–19:10', 'AtCoder', [abc_item(d)]))
    fixed.append(B(6, '22:00', 'Wind down', [LOG(iso)]))
    days.append({'date': iso, 'dow': d.strftime('%a'), 'label': d.strftime('%b %-d'), 'cls': 'wd' if wd < 5 else 'we', 'fixed': fixed, 'content': None})

weeks = [{'name': w['name'], 'stage': w['stage'], 'note': w['note'], 'ac': w['ac'], 'pat': w['pat']} for w in WEEKS]
data = {'stages': STAGES, 'rules': RULES, 'weeks': weeks, 'days': days, 'filters': filters, 'cses': CS,
        'preDone': sorted(PRE)}
html = open('template.html').read().replace('/*DATA*/null', json.dumps(data, ensure_ascii=False))
open(pathlib.Path(__file__).resolve().parents[2] / 'public' / 'cp' / 'index.html', 'w').write(html)
print(len(WEEKS), 'weeks,', days[-1]['date'], 'last day,', sum(len(x['items']) for d in days for x in d['fixed'] + (d['content']['blocks'] if d['content'] else [])), 'items,', len(html) // 1024, 'KB')
