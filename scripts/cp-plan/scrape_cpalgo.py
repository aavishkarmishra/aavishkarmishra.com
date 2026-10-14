"""Fetch the practice-problem list of every CP-Algorithms page the curriculum links to -> cpalgo.json."""
import json, re, ssl, urllib.request, concurrent.futures as cf
from curriculum import WEEKS

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode()

def practice(url):
    h = get(url)
    i = h.find('id="practice-problems"')
    if i < 0: return []
    seg = h[i:]
    end = min([j for j in (seg.find('<h2', 10), seg.find('git-committers'), seg.find('md-source-file')) if j > 0] or [len(seg)])
    out = []
    for u, t in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', seg[:end], re.S):
        t = re.sub(r'<[^>]+>', '', t).strip()
        if u.startswith('http') and 'github.com' not in u and 'cp-algorithms.com' not in u and t:
            out.append([t, u.strip()])
    return out

pages = sorted({u.split('#')[0] for w in WEEKS for _, u in w['rd'] if 'cp-algorithms.com' in u})
with cf.ThreadPoolExecutor(6) as ex:
    res = dict(zip(pages, ex.map(practice, pages)))
json.dump(res, open('cpalgo.json', 'w'), indent=0)
print(len(pages), 'pages,', sum(map(len, res.values())), 'problems')

# LeetCode difficulty for every LeetCode link on those pages and in the Top Interview 150 list -> lc_diff.json
def lc_difficulty(slug):
    q = {'query': 'query($s:String!){question(titleSlug:$s){difficulty}}', 'variables': {'s': slug}}
    req = urllib.request.Request('https://leetcode.com/graphql', data=json.dumps(q).encode(),
                                 headers={'Content-Type': 'application/json', 'Referer': 'https://leetcode.com', 'User-Agent': 'Mozilla/5.0'})
    d = json.load(urllib.request.urlopen(req, timeout=30))['data']['question']
    return d and d['difficulty']
slugs = sorted({re.search(r'leetcode\.com/problems/([\w-]+)', u).group(1) for v in res.values() for _, u in v if re.search(r'leetcode\.com/problems/', u)})
with cf.ThreadPoolExecutor(4) as ex:
    json.dump(dict(zip(slugs, ex.map(lc_difficulty, slugs))), open('lc_diff.json', 'w'))
print(len(slugs), 'leetcode difficulties')
