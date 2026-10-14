import json, re, os, pathlib, datetime as dt
os.chdir(pathlib.Path(__file__).resolve().parent)
from urllib.parse import quote
from curriculum import WEEKS, CS
from roadmap import STAGES, RULES
import interview

START = dt.date(2026, 9, 28)
RESTART = dt.date(2026, 10, 14)   # days in [WORKED_UNTIL+1, RESTART) were missed; the plan resumes here
WORKED_UNTIL = dt.date(2026, 10, 1)
RESUME_TOPIC = 1
NAME = {i: t for s in CS for i, t in s['tasks']}
OUT = pathlib.Path(__file__).resolve().parents[2] / 'public' / 'cp' / 'index.html'

# ---- judge data ----
P = json.load(open('probs.json'))['result']
stats = {(s['contestId'], s['index']): s['solvedCount'] for s in P['problemStatistics']}
PROB = {(p['contestId'], p['index']): p for p in P['problems']}
tried = {(s['problem'].get('contestId'), s['problem']['index']) for s in json.load(open('status.json'))['result']}
AP = json.load(open('ac_problems.json')); AM = json.load(open('ac_models.json'))
APROB = {p['id']: p for p in AP}
LCD = json.load(open('lc_diff.json'))
CPALGO = json.load(open('cpalgo.json'))

def task(k, t, u=None, n=None, r=None):
    d = {'k': k, 't': t}
    if u: d['u'] = u
    if n: d['n'] = n
    if r is not None: d['r'] = r
    return d
GREEDY = 'Tagged greedy. Not sure it holds? Write the brute force and run stress/stress.sh before submitting.'

used, aused = set(), set()
def cf_item(p):
    return task(f"cf{p['contestId']}{p['index']}", f"CF {p['contestId']}{p['index']} · {p['name']}",
                f"https://codeforces.com/problemset/problem/{p['contestId']}/{p['index']}", GREEDY if 'greedy' in p['tags'] else None, p.get('rating'))
def cf_pick(lo, hi, tags):
    # older contests first, then a wider band, when a narrow tag runs dry
    for min_cid, pad in ((1700, 0), (1000, 0), (1000, 100), (1, 200)):
        c = [p for p in P['problems'] if p.get('rating') and lo - pad <= p['rating'] <= hi + pad and p['contestId'] >= min_cid
             and (p['contestId'], p['index']) not in tried and (p['contestId'], p['index']) not in used
             and '*special' not in p['tags'] and (not tags or set(tags) & set(p['tags']))]
        if c:
            p = max(c, key=lambda p: stats.get((p['contestId'], p['index']), 0))
            used.add((p['contestId'], p['index']))
            return cf_item(p)
    raise SystemExit(f'no codeforces problem near {lo}-{hi} {tags}')
def furl(tags, lo, hi): return 'https://codeforces.com/problemset?order=BY_SOLVED_DESC&tags=' + quote(','.join(tags + [f'{lo}-{hi}']))

apool = sorted([(p['contest_id'], p['id'], p['name'], AM[p['id']]['difficulty']) for p in AP
                if p['contest_id'].startswith('abc') and int(p['contest_id'][3:]) >= 100 and p['id'] in AM and AM[p['id']].get('difficulty') is not None
                and p['problem_index'] in 'CDEF'], reverse=True)
def ac_pick(lo, hi):
    # widen the band when a level runs dry; the pool of ABC C–F is small
    for pad in range(0, 1200, 200):
        for cid, pid, name, d in apool:
            if lo - pad <= d <= hi + pad and pid not in aused:
                aused.add(pid)
                return task('ac' + pid, f"AtCoder {pid.upper().replace('_', ' ')} · {name}", f'https://atcoder.jp/contests/{cid}/tasks/{pid}', None, f'diff {d}')
    raise SystemExit(f'no atcoder problem near {lo}-{hi}')

cses = lambda i: task(f'cses{i}', f'CSES · {NAME[i]}', f'https://cses.fi/problemset/task/{i}')
read = lambda t, u: task('read:' + u, 'Read: ' + t, u, 'Take the whole block. Write a 5-line summary and the template code in your own words.')
LOG = lambda d: task(f'log{d}', 'Log each idea you missed in one line (box below)')
LC = lambda d: task(f'lc{d}', 'LeetCode daily question', 'https://leetcode.com/problemset/')
UP = lambda d: task(f'up{d}', 'Upsolve: if you got stuck, read the editorial, close it, then code it yourself')

# ---- page problems: key, estimated rating, item ----
LC_EST = {'Easy': 900, 'Medium': 1400, 'Hard': 1900}
def page_problem(title, url, page_title):
    m = re.search(r'codeforces\.com/(?:problemset/problem|contest)/(\d+)/(?:problem/)?(\w+)', url)
    if m and (int(m.group(1)), m.group(2)) in PROB:
        p = PROB[(int(m.group(1)), m.group(2))]
        it = cf_item(p); return it['k'], p.get('rating') or 1800, it
    m = re.search(r'atcoder\.jp/contests/\w+/tasks/(\w+)', url)
    if m:
        d = AM.get(m.group(1), {}).get('difficulty')
        return 'ac' + m.group(1), d if d is not None else 1800, task('ac' + m.group(1), title, url, None, f'diff {d}' if d is not None else None)
    m = re.search(r'leetcode\.com/problems/([\w-]+)', url)
    if m:
        diff = LCD.get(m.group(1))
        return 'lcp:' + m.group(1), LC_EST.get(diff, 1400), task('lcp:' + m.group(1), title, url, None, diff)
    m = re.search(r'cses\.fi/problemset/task/(\d+)', url)
    if m and int(m.group(1)) in NAME:
        return f'cses{m.group(1)}', 1500, cses(int(m.group(1)))
    return 'x:' + url, 1800, task('x:' + url, title, url, 'Older judge, no rating. Read the statement and I/O format carefully.')

PRE = {'cses1617', 'cses1618', 'cses1754', 'cses1072', 'cses1092'}

# ---- history: worked days stay exactly as published; missed days carry no study content ----
prev = json.loads(re.search(r'const DATA = (\{.*?\});\n', OUT.read_text(), re.S).group(1))
prev_days = {d['date']: d for d in prev['days']}
seen_keys = set()
days = []
B = lambda o, time, label, items: {'o': o, 'time': time, 'label': label, 'items': items}

def fixed_for(d):
    iso = d.isoformat(); wd = d.weekday()
    f = [B(3.5, '13:30–14:00' if wd < 5 else 'After lunch', 'LeetCode', [LC(iso)])]
    if wd == 5: f.append(B(4, '17:30–19:10', 'AtCoder', [task(f'abc{iso}', 'AtCoder ABC, live 17:30 if scheduled', 'https://atcoder.jp/contests/')]))
    if wd == 6:
        f.append(B(6, 'Afternoon', 'Rest', [task(f'rest{iso}', 'Take the afternoon off. Rest is part of the plan')]))
        if d.month != (d + dt.timedelta(7)).month:
            f.append(B(5, 'Evening', 'Month retro', [
                task(f'retro{iso}', 'Compare rating and solved count to a month ago. Read the log. Name the 2 slip types you hit most'),
                task(f'retro2{iso}', 'Check both exit checklists on the Roadmap tab (stage and interview)')]))
    f.append(B(7, '22:00', 'Wind down', [LOG(iso)]))
    return f

d = START
while d < RESTART:
    iso = d.isoformat(); pd = prev_days[iso]
    if d <= WORKED_UNTIL:
        days.append(pd)
        for b in pd['content']['blocks']:
            for i in b['items']:
                seen_keys.add(i['k'])
    else:
        days.append({**pd, 'content': None, 'skip': True})
    d += dt.timedelta(1)
for k in seen_keys | PRE:
    m = re.match(r'cf(\d+)(\w+)$', k)
    if m: used.add((int(m.group(1)), m.group(2)))
    if k.startswith('ac'): aused.add(k[2:])

# ---- page problem pools per topic; harder ones park until a later topic's band reaches them ----
parked = []
page_seen = set()
def page_items(page_url, page_title, band_hi):
    now = []
    for t, u in CPALGO.get(page_url, []):
        if 'squidfunk' in u: continue
        k, est, it = page_problem(t, u, page_title)
        if k in seen_keys or k in PRE: continue
        seen_keys.add(k)
        if est <= band_hi + 300: now.append((est, it))
        else: parked.append((est, page_title, page_url, it))
    return [it for _, it in sorted(now, key=lambda x: x[0])]

# ---- interview queues ----
design = interview.design_queue()
saturdays = interview.saturday_queue()
coding = interview.coding_queue()

# ---- generation ----
filters, topics_meta = [], []
concepts = []   # (read_date, label, first problems scheduled after the read, filter url)
d = RESTART
for ti in range(RESUME_TOPIC, len(WEEKS)):
    w = WEEKS[ti]
    lo, hi, tags = w['cf']
    ft, ftags, flo, fhi, ftarget = w['flt']
    fk = f'w{ti}'
    filters.append({'key': fk, 'week': ti, 'title': ft, 'lo': flo, 'hi': fhi, 'tags': ftags, 'target': ftarget, 'url': furl(ftags, flo, fhi)})
    speed = w['name'].startswith('Speed week')
    cs_q = [i for i in w['cses'] if f'cses{i}' not in PRE and f'cses{i}' not in seen_keys]
    seen_keys.update(f'cses{i}' for i in cs_q)
    reads = []
    for t, u in w['rd']:
        pu = u.split('#')[0]
        probs = page_items(pu, t, hi) if 'cp-algorithms.com' in pu and pu not in page_seen else []
        page_seen.add(pu)
        reads.append((t, u, probs))
    revisit = []
    for p in sorted([p for p in parked if p[0] <= hi + 300], key=lambda x: x[0])[:8]:
        parked.remove(p)
        revisit.append({**p[3], 'n': f'Page revisit from "{p[1]}". Re-skim the page first.'})
    page_q = []
    def take(n):
        global page_q
        out = []
        while len(out) < n and (page_q or revisit):
            out.append((page_q or revisit).pop(0))
        return out
    weekdays_in_topic = 0
    while True:
        work_left = reads or page_q or revisit or cs_q
        if weekdays_in_topic >= 5 and not work_left: break
        iso = d.isoformat(); wd = d.weekday()
        content = []
        if wd < 5:
            weekdays_in_topic += 1
            if speed:
                content.append(B(1, '09:00–10:30', 'Virtual contest', [task(f'virt{iso}', 'Virtual Div 2 you have not seen (2h). Start at 09:00 sharp', 'https://codeforces.com/contests')]))
                content.append(B(2, '10:45–12:00', 'Upsolve', [task(f'upv{iso}', 'Upsolve the first two problems you missed')]))
            else:
                if reads and not page_q:
                    t, u, probs = reads.pop(0)
                    content.append(B(1, '09:00–10:30', 'Read', [read(t, u)]))
                    page_q = probs or [cf_pick(lo, hi, tags) for _ in range(4)]
                    concepts.append({'date': d, 'label': t, 'items': [], 'filter': furl(ftags or tags, lo, hi), 'topic': ti})
                elif cs_q:
                    content.append(B(1, '09:00–10:30', 'CSES', [cses(i) for i in cs_q[:3]])); cs_q = cs_q[3:]
                elif page_q or revisit:
                    content.append(B(1, '09:00–10:30', 'Problems', take(2)))
                else:
                    content.append(B(1, '09:00–10:30', 'Problems', [cf_pick(lo, hi, tags)]))
                content.append(B(2, '10:45–12:00', 'Problems', (take(2) or [cf_pick(lo, hi, tags)]) + [UP(iso)]))
            if design:
                s = design.pop(0)
                content.append(B(3, '12:30–13:30', {'HLD': 'System design (HLD)', 'LLD': 'Low-level design (LLD)'}[s['kind']], [task(f'ds:{s["u"]}:{s["t"]}', s['t'], s['u'], s['n'] or None)]))
            if wd in (1, 2, 3) and coding:
                qs = [coding.pop(0) for _ in range(min(3, len(coding)))]
                content.append(B(4, '20:00–22:00', 'Interview coding', [
                    task('lcp:' + q['titleSlug'], f"{q['title']} ({q['g']})", f"https://leetcode.com/problems/{q['titleSlug']}/",
                         'Timed in a plain doc, no IDE, talking aloud. Medium 25 min, hard 40 min. Dry-run, state complexity, then submit.', q['difficulty'])
                    for q in qs]))
            else:
                ev = take(1) or [task(f'flt{fk}_{iso}', f'Filter · {ft} {flo}–{fhi}, one problem', furl(ftags, flo, fhi), 'Sorted by most solved. Skip green ones.')]
                content.append(B(4, '20:00–22:00', 'Evening block', ev + [ac_pick(*w['ac'])]))
        elif wd == 5:
            content.append(B(1, '09:00–11:00', 'Virtual contest', [task(f'virt{iso}', 'Virtual Div 2 you have not seen (2h)', 'https://codeforces.com/contests')]))
            content.append(B(2, '11:15–12:30', 'Upsolve', [task(f'upv{iso}', 'Upsolve the first problem you missed in the virtual')]))
            if saturdays:
                s = saturdays.pop(0)
                content.append(B(3, '14:00–15:30', 'Mock interview' if s['kind'] == 'MOCK' else 'Behavioral', [task(f'sat:{iso}', s['t'], s['u'], s['n'] or None)]))
        else:
            review = [task(f'wa{iso}', 'Re-submit 2 problems you got WA on this week. Run the four checks first'),
                      task(f'plan{iso}', 'Read next week in this tracker')]
            if w['stage'] >= 2: review.append(task(f'div1{iso}', 'This week\'s Codeforces: register for Div 1 if you are 1900+, otherwise Div 2 or Edu', 'https://codeforces.com/contests'))
            content.append(B(1, '09:30–11:30', 'Upsolve', [task(f'ups{iso}', 'Upsolve ABC D and E, and the Codeforces round if you did one')]))
            content.append(B(2, '11:30–12:30', 'Weekly review', review))
            if w['stage'] >= 2: content.append(B(4.5, '17:30–19:30', 'AtCoder ARC', [task(f'arc{iso}', 'ARC, live if scheduled. Aim A–B', 'https://atcoder.jp/contests/')]))
        for c in concepts:
            if len(c['items']) < 3 and c['date'] <= d:
                c['items'] += [i for b in content if b['label'] in ('Problems', 'CSES', 'Evening block') for i in b['items']
                               if re.match(r'(cf\d|ac|cses|lcp:|x:)', i['k']) and i['k'] not in {x['k'] for x in c['items']}][:3 - len(c['items'])]
        days.append({'date': iso, 'dow': d.strftime('%a'), 'label': d.strftime('%b %-d'), 'cls': 'wd' if wd < 5 else 'we',
                     'fixed': fixed_for(d), 'content': {'week': ti, 'blocks': content}})
        d += dt.timedelta(1)
    topics_meta.append(ti)

# Remaining interview work after the CP topics run out keeps going on its own days.
while design or coding or saturdays:
    iso = d.isoformat(); wd = d.weekday(); content = []
    if wd < 5 and design:
        s = design.pop(0); content.append(B(3, '12:30–13:30', s['kind'], [task(f'ds:{s["u"]}:{s["t"]}', s['t'], s['u'], s['n'] or None)]))
    if wd in (1, 2, 3) and coding:
        q = coding.pop(0); content.append(B(4, '20:00–22:00', 'Interview coding', [task('lcp:' + q['titleSlug'], q['title'], f"https://leetcode.com/problems/{q['titleSlug']}/", None, q['difficulty'])]))
    if wd == 5 and saturdays:
        s = saturdays.pop(0); content.append(B(3, '14:00–15:30', 'Interview', [task(f'sat:{iso}', s['t'], s['u'], s['n'] or None)]))
    days.append({'date': iso, 'dow': d.strftime('%a'), 'label': d.strftime('%b %-d'), 'cls': 'wd' if wd < 5 else 'we',
                 'fixed': fixed_for(d), 'content': {'week': len(WEEKS) - 1, 'blocks': content}})
    d += dt.timedelta(1)

# Days already lived through keep their published content, so re-fetched data never rewrites worked days.
for x in days:
    if RESTART.isoformat() <= x['date'] < dt.date.today().isoformat() and prev_days.get(x['date'], {}).get('content'):
        x['content'] = prev_days[x['date']]['content']

# ---- spaced review: 2 items at +1, +7, +30 days; at most 4 review items a day, overflow rolls forward ----
by_date = {x['date']: x for x in days}
load = {}
for c in concepts:
    for step, gap in enumerate((1, 7, 30)):
        target = c['date'] + dt.timedelta(gap)
        base = c['items'][step % len(c['items'])] if c['items'] else None
        items = []
        if base: items.append({**base, 'k': f're{gap}:{base["k"]}', 't': f'Re-solve from a blank file · {base["t"]}', 'n': f'+{gap} day review of "{c["label"]}".'})
        items.append(task(f'rn{gap}:{c["label"]}', f'One new problem on "{c["label"]}" (+{gap} day review)', c['filter'], 'From the filter, one you have not seen. Spot the technique without the tag.'))
        if target < dt.date.today(): continue
        while load.get(target, 0) + len(items) > 4 or target.isoformat() not in by_date or by_date[target.isoformat()].get('skip'):
            target += dt.timedelta(1)
            if target.isoformat() not in by_date: break
        day = by_date.get(target.isoformat())
        if not day or not day.get('content'): continue
        load[target] = load.get(target, 0) + len(items)
        blk = next((b for b in day['content']['blocks'] if b['label'] == 'Spaced review'), None)
        if not blk:
            blk = B(0, '09:00, first', 'Spaced review', []); day['content']['blocks'].insert(0, blk)
        blk['items'] += items

# Buffer dates so content pushed back by off days still has somewhere to land.
for i in range(60):
    x = d + dt.timedelta(i)
    days.append({'date': x.isoformat(), 'dow': x.strftime('%a'), 'label': x.strftime('%b %-d'), 'cls': 'wd' if x.weekday() < 5 else 'we', 'fixed': fixed_for(x), 'content': None})

# keep the worked weeks' filters so their rows still show
filters = [f for f in prev['filters'] if f['week'] < RESUME_TOPIC] + filters
weeks = [{'name': w['name'], 'stage': w['stage'], 'note': w['note'], 'ac': w['ac']} for w in WEEKS]
data = {'stages': STAGES, 'rules': RULES, 'weeks': weeks, 'days': days, 'filters': filters, 'cses': CS, 'preDone': sorted(PRE),
        'interview': interview.GATES}
html = open('template.html').read().replace('/*DATA*/null', json.dumps(data, ensure_ascii=False))
OUT.write_text(html)
end_cp = max(x['date'] for x in days if x.get('content') and x['content']['week'] == len(WEEKS) - 1)
print(f"plan to {end_cp}, {len(days)} days, {len(concepts)} concepts, {len(parked)} still parked, {len(html) // 1024} KB")
print('design ends', max(x['date'] for x in days if x.get('content') and any(b['o'] == 3 and b['label'] != 'Behavioral' for b in x['content']['blocks'])))
