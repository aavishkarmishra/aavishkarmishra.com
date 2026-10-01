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
echo "data ready"
