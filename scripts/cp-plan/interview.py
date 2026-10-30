import json, re
# Interview track: Striver's SDE sheet in its own order, with the 180 sheet's extra problems added after the matching section.
SDE = json.load(open('sde.json'))
S180 = json.load(open('striver.json'))
PAID = json.load(open('lc_paid.json'))
TUF = 'https://takeuforward.org'
SHEET_PAGE = TUF + '/prep-hub/strivers-sde-sheet?page=sheet'
# LeetCode renamed this slug; the judge sync only reports current slugs.
SLUG_FIX = {'implement-strstr': 'find-the-index-of-the-first-occurrence-in-a-string'}
TITLE_FIX = {'Implement strStr()': 'String to Integer (atoi)'}
MINS = {'basic': 10, 'core': 20, 'pro': 35, None: 20}
EXTRA_MINS = 25
# 180-sheet topic -> SDE section it follows.
AFTER = {'Arrays': 'Arrays Part-IV', 'Hashing': 'Arrays Part-IV', 'Sliding Window and Two Pointers': 'Arrays Part-IV',
         'Linked List': 'Linked List Part-II', 'Greedy Algorithms': 'Greedy Algorithm', 'Recursion and Backtracking': 'Recursion and Backtracking',
         'Binary Search': 'Binary Search', 'Heaps': 'Heaps', 'Stack and Queues': 'Stack and Queue Part-II', 'Strings': 'String Part-II',
         'Binary Trees': 'Binary Tree part-III', 'Binary Search Trees': 'Binary Search Tree Part-II', 'Graphs': 'Graph Part-II',
         'Dynamic Programming': 'Dynamic Programming Part-II', 'Tries': 'Trie', 'Bit Manipulation': 'Trie', 'Mathematics': 'Trie'}
TOPIC = {'Linked List and Arrays': 'Linked List', 'Binary Trees[Miscellaneous]': 'Binary Trees', 'Binary Tree': 'Binary Trees',
         'Greedy Algorithm': 'Greedy Algorithms', 'Recursion': 'Recursion and Backtracking', 'Stack and Queue': 'Stack and Queues',
         'String': 'Strings', 'Binary Search Tree': 'Binary Search Trees', 'Graph': 'Graphs', 'Trie': 'Tries'}
topic = lambda sec: (lambda s: TOPIC.get(s, s))(re.sub(r' (Part|part)-[IV]+$', '', sec))
# Evening CP follows the morning's topic: (CSES section, Codeforces tags).
CP = {'Arrays': ('Sorting and Searching', ['greedy', 'sortings', 'two pointers']), 'Hashing': ('Sorting and Searching', ['sortings', 'two pointers']),
      'Sliding Window and Two Pointers': ('Sliding Window Problems', ['two pointers']), 'Linked List': ('Sorting and Searching', ['two pointers']),
      'Greedy Algorithms': ('Sorting and Searching', ['greedy']), 'Recursion and Backtracking': ('Introductory Problems', ['brute force', 'bitmasks']),
      'Binary Search': ('Sorting and Searching', ['binary search']), 'Heaps': ('Sorting and Searching', ['data structures']),
      'Stack and Queues': ('Sliding Window Problems', ['data structures']), 'Strings': ('String Algorithms', ['strings', 'hashing']),
      'Binary Trees': ('Tree Algorithms', ['trees', 'dfs and similar']), 'Binary Search Trees': ('Tree Algorithms', ['trees', 'dfs and similar']),
      'Graphs': ('Graph Algorithms', ['graphs', 'dfs and similar', 'shortest paths', 'dsu']), 'Dynamic Programming': ('Dynamic Programming', ['dp']),
      'Tries': ('String Algorithms', ['strings', 'data structures']), 'Bit Manipulation': ('Bitwise Operations', ['bitmasks']),
      'Mathematics': ('Mathematics', ['math', 'number theory'])}
CP_FALLBACK = ['Sorting and Searching', 'Dynamic Programming', 'Graph Algorithms']

SHORT = {'Sliding Window and Two Pointers': 'Sliding window', 'Recursion and Backtracking': 'Backtracking', 'Stack and Queues': 'Stack + queue',
         'Binary Search Trees': 'BST', 'Dynamic Programming': 'DP', 'Bit Manipulation': 'Bits', 'Greedy Algorithms': 'Greedy'}
short = lambda top: SHORT.get(top, top)
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())

def _lc(slug, t, top, mins, blog=None):
    slug = SLUG_FIX.get(slug, slug)
    it = {'k': 'lcp:' + slug, 't': f'{short(top)} · {t}', 'u': f'https://leetcode.com/problems/{slug}/', 'topic': top, 'min': mins}
    if PAID.get(slug):
        it['n'] = 'LeetCode Premium. No Premium? Solve it from the article link: ' + (TUF + blog if blog else SHEET_PAGE)
    return it

def sheet_items():
    by = {}
    for x in S180:
        by.setdefault(norm(x['k'][4:]), x)
    used, out, taken = set(), [], set()
    def add(it):
        if it['k'] in used:
            return
        used.add(it['k']); out.append(it)
    def from180(x, mins, top=None):
        top = top or x['topic']
        if x['k'].startswith('lcp:'):
            return _lc(x['k'][4:], x['t'], top, mins)
        return {'k': x['k'], 't': f"{short(top)} · {x['t']}", 'u': x['u'], 'topic': top, 'min': mins}
    # 180 items an SDE item will match later stay out of the extras, so they keep the SDE position.
    later = {norm(m['k'][4:]) for x in SDE for m in [by.get(norm(x.get('lc', ''))) if x.get('lc') else None, by.get(norm(x['t']))] if m}
    secs = []
    for x in SDE:
        if not secs or secs[-1][0] != x['s']:
            secs.append((x['s'], []))
        secs[-1][1].append(x)
    for sec, xs in secs:
        top = topic(sec)
        for x in xs:
            t = TITLE_FIX.get(x['t'], x['t'])
            m = by.get(norm(x.get('lc', ''))) if x.get('lc') else None
            m = m or by.get(norm(x['t']))
            mins = MINS[x.get('d')]
            if m and norm(m['k'][4:]) not in taken:
                taken.add(norm(m['k'][4:])); add(from180(m, mins, top)); continue
            k = 'lcp:' + SLUG_FIX.get(x['lc'], x['lc']) if x.get('lc') else None
            if k and k not in used:
                add(_lc(x['lc'], t, top, mins, x.get('blog')))
            else:
                # Same LeetCode link as an earlier item (Morris traversal, Merge K arrays): tick it by hand.
                add({'k': 'tuf:' + re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-'), 't': f'{short(top)} · {t}',
                     'u': TUF + x['blog'] if x.get('blog') else SHEET_PAGE, 'topic': top, 'min': mins})
        for x in S180:
            if AFTER.get(x['topic']) == sec and norm(x['k'][4:]) not in taken | later:
                taken.add(norm(x['k'][4:])); add(from180(x, EXTRA_MINS))
    return out

XU1, XU2, DDIA = 'System Design Interview Vol 1 (Alex Xu)', 'System Design Interview Vol 2 (Alex Xu)', 'Designing Data-Intensive Applications'
PRIMER = 'https://github.com/donnemartin/system-design-primer'
CASE = 'First 30 minutes on paper: requirements, estimates, API, data model, diagram, one deep dive. Then read the chapter and write down what you missed.'
D = lambda slug, t, u=None, n=None: {'k': 'dz:' + slug, 't': t, **({'u': u} if u else {}), **({'n': n} if n else {})}
# HLD: Mon–Thu. Core CS (DBMS, OS, CN) only where design needs it.
HLD = [
    D('scale', f'Scale from zero to millions of users · {XU1} ch 1', n='Learn the words: load balancer, replica, cache, CDN, stateless tier, shard, queue.'),
    D('framework', f'The interview framework + back-of-envelope estimates · {XU1} ch 2–3', 'https://gist.github.com/jboner/2841832', 'Memorise the latency numbers and powers of two. Estimate QPS and storage for Twitter by hand.'),
    D('url', 'CN: what happens when you type a URL (DNS, TCP handshake, TLS, HTTP)', 'https://github.com/alex/what-happens-when'),
    D('protocols', 'CN: TCP vs UDP, HTTP/1.1 vs 2 vs 3, REST vs gRPC, WebSockets vs long polling vs SSE', PRIMER),
    D('lb', 'Load balancers: L4 vs L7, algorithms, health checks, reverse proxy, API gateway', PRIMER),
    D('cache', 'Caching: cache-aside, write-through, write-back, eviction, TTL, thundering herd, CDN', PRIMER),
    D('db-models', f'DBMS: SQL vs NoSQL, data models, when to pick which · {DDIA} ch 2'),
    D('db-index', f'DBMS: indexes, B+ tree vs LSM tree, composite indexes · {DDIA} ch 3', n='Then do 5 problems from LeetCode SQL 50 (joins, GROUP BY).'),
    D('db-txn', f'DBMS: transactions, ACID, isolation levels and their anomalies, locking vs MVCC · {DDIA} ch 7'),
    D('db-repl', f'Replication: leader-follower, multi-leader, leaderless, replication lag · {DDIA} ch 5'),
    D('db-shard', f'Sharding: range vs hash, hot keys, rebalancing · {DDIA} ch 6, then consistent hashing · {XU1} ch 5'),
    D('cap', f'CAP, PACELC, consistency models (strong, eventual, read-your-writes), quorums · {DDIA} ch 9, first half'),
    D('queues', f'Message queues and streams: Kafka model, at-least-once, idempotent consumers, dead-letter queues · {DDIA} ch 11, skim'),
    D('ids', f'Blob storage, CDN, unique ID generation (Snowflake) · {XU1} ch 7'),
    D('rate-limiter', f'Case: rate limiter · {XU1} ch 4', n=CASE),
    D('kv', f'Case: key-value store · {XU1} ch 6', n=CASE),
    D('tinyurl', f'Case: URL shortener · {XU1} ch 8', n=CASE),
    D('crawler', f'Case: web crawler · {XU1} ch 9', n=CASE),
    D('notify', f'Case: notification system · {XU1} ch 10', n=CASE),
    D('feed', f'Case: news feed · {XU1} ch 11', n=CASE),
    D('chat', f'Case: chat system · {XU1} ch 12', n=CASE),
    D('typeahead', f'Case: search autocomplete · {XU1} ch 13', n=CASE),
    D('youtube', f'Case: YouTube · {XU1} ch 14', n=CASE),
    D('drive', f'Case: Google Drive · {XU1} ch 15', n=CASE),
    D('proximity', f'Case: proximity service · {XU2} ch 1', n=CASE),
    D('maps', f'Case: Google Maps · {XU2} ch 3', n=CASE),
    D('mq', f'Case: distributed message queue · {XU2} ch 4', n=CASE),
    D('metrics', f'Case: metrics monitoring and alerting · {XU2} ch 5', n=CASE),
    D('ads', f'Case: ad click aggregation · {XU2} ch 6', n=CASE),
    D('hotel', f'Case: hotel reservation (transactions, double booking) · {XU2} ch 7', n=CASE),
    D('payments', f'Case: payment system (idempotency, exactly-once) · {XU2} ch 11', n=CASE),
    D('leaderboard', f'Case: real-time leaderboard · {XU2} ch 10', n=CASE),
]
RG = 'https://refactoring.guru/design-patterns/'
# LLD: Fridays. Google rarely has an LLD round; this covers class design inside coding rounds and OS concurrency.
LLD = [
    D('oop', 'LLD: OOP in C++ (abstract classes, composition over inheritance) and SOLID', RG + 'what-is-pattern'),
    D('patterns-1', 'LLD patterns: Strategy, Observer, Factory Method. Write each in C++', RG + 'strategy'),
    D('patterns-2', 'LLD patterns: State, Singleton, Decorator, Builder. Write each in C++', RG + 'state'),
    D('concurrency', 'OS: process vs thread, mutex, condition variable, semaphore, deadlock (4 conditions), virtual memory basics', 'https://en.cppreference.com/w/cpp/thread'),
    D('lru-mt', 'LLD: thread-safe LRU cache and a bounded producer-consumer queue in C++ (std::mutex, std::condition_variable)'),
    D('parking', 'LLD: parking lot and elevator. Classes, interactions, where it extends'),
]
BEHAVIOURAL = [
    D('bh-stories', 'Behavioural: write 6–8 stories from work (situation, what you did, result with a number)', n='Cover: a conflict, a mistake, a hard bug, leading without authority, an ambiguous task, helping a teammate.'),
    D('bh-google', 'Behavioural: Googleyness. Map each story to the questions it answers; practise each out loud in 2 minutes'),
    D('bh-mock', 'Behavioural mock with a friend, or record yourself and watch it back'),
]
PHASE2_TOPICS = ['Array', 'String', 'Hash Table', 'Two Pointers', 'Sliding Window', 'Binary Search', 'Stack', 'Heap (Priority Queue)', 'Tree',
                 'Graph', 'Dynamic Programming', 'Backtracking', 'Greedy', 'Trie', 'Union Find']
GATES = ['Unseen LeetCode mediums solved in about 25 minutes, with no bounds, edge-case or code-vs-idea slips, 5 in a row',
         'Passed 2 of the last 3 coding mocks',
         'One design mock where you drove requirements, estimates and the deep dive without prompting',
         'Behavioural stories written and practised out loud']
