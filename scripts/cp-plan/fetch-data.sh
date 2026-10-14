#!/usr/bin/env bash
# Downloads the judge data build.py reads; the files are gitignored.
# Re-fetching changes which problems future days get. Days up to today stay frozen.
set -e
cd "$(dirname "$0")"
curl -s https://codeforces.com/api/problemset.problems -o probs.json
curl -s "https://codeforces.com/api/user.status?handle=aavishkar" -o status.json
curl -s -A "Mozilla/5.0" https://kenkoooo.com/atcoder/resources/problems.json -o ac_problems.json
curl -s -A "Mozilla/5.0" https://kenkoooo.com/atcoder/resources/problem-models.json -o ac_models.json
curl -sL -A "Mozilla/5.0" https://cses.fi/problemset/ -o cses.html
python3 -c "
import re, json
h = open('cses.html').read()
out = [{'name': s.split('</h2>')[0], 'tasks': [[int(i), t] for i, t in re.findall(r'href=\"/problemset/task/(\d+)/?\">([^<]+)</a>', s)]} for s in re.split(r'<h2>', h)[1:]]
json.dump([o for o in out if o['tasks']], open('cses.json', 'w'))
"
rm cses.html
python3 - <<'PY'
import json, urllib.request
q = {"query": "query($s:String!){studyPlanV2Detail(planSlug:$s){planSubGroups{name questions{titleSlug title difficulty}}}}", "variables": {"s": "top-interview-150"}}
req = urllib.request.Request("https://leetcode.com/graphql", data=json.dumps(q).encode(), headers={"Content-Type": "application/json", "Referer": "https://leetcode.com", "User-Agent": "Mozilla/5.0"})
json.dump(json.load(urllib.request.urlopen(req, timeout=30))["data"]["studyPlanV2Detail"], open("lc_top150.json", "w"))
PY
python3 scrape_cpalgo.py
echo "data ready"
