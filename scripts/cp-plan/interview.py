import json

HI = 'https://www.hellointerview.com/learn/system-design/'
SDP = 'https://github.com/donnemartin/system-design-primer#'
RG = 'https://refactoring.guru/design-patterns/'
LLD = 'https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/'

def S(kind, title, url, note=''):
    return {'kind': kind, 't': title, 'u': url, 'n': note}

CFL = 'https://www.cloudflare.com/learning/'
HLD_FOUNDATIONS = [
    S('HLD', 'Foundations: how the web works', 'https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works'),
    S('HLD', 'Foundations: HTTP, requests, responses, status codes', 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview'),
    S('HLD', 'Foundations: DNS', CFL + 'dns/what-is-dns/'),
    S('HLD', 'Foundations: TCP/IP', CFL + 'ddos/glossary/tcp-ip/'),
    S('HLD', 'Foundations: REST APIs', 'https://restfulapi.net/'),
    S('HLD', 'Foundations: what a database index is', 'https://use-the-index-luke.com/sql/anatomy', 'Read the anatomy chapter. Draw a B-tree lookup on paper.'),
    S('HLD', 'Foundations: transactions and ACID', 'https://www.postgresql.org/docs/current/tutorial-transactions.html'),
    S('HLD', 'Foundations: caching', 'https://aws.amazon.com/caching/'),
    S('HLD', 'Foundations: load balancing', CFL + 'performance/what-is-load-balancing/'),
    S('HLD', 'Foundations: CDNs', CFL + 'cdn/what-is-a-cdn/'),
    S('HLD', 'Foundations: message queues', 'https://aws.amazon.com/message-queue/'),
]
HLD_STUDY = HLD_FOUNDATIONS + [
    S('HLD', 'System design in a hurry: introduction', HI + 'in-a-hurry/introduction'),
    S('HLD', 'The interview delivery framework', HI + 'in-a-hurry/delivery', 'Memorise the steps. Every practice design below follows them.'),
    S('HLD', 'Core concepts: scaling, CAP, consistency, indexing', HI + 'in-a-hurry/core-concepts'),
    S('HLD', 'Key technologies: databases, caches, queues, search', HI + 'in-a-hurry/key-technologies'),
    S('HLD', 'Common patterns', HI + 'in-a-hurry/patterns'),
    S('HLD', 'Primer: performance vs scalability, latency vs throughput', SDP + 'performance-vs-scalability'),
    S('HLD', 'Primer: availability vs consistency, CAP, consistency patterns', SDP + 'availability-vs-consistency'),
    S('HLD', 'Primer: DNS, CDN, load balancers, reverse proxies', SDP + 'domain-name-system'),
    S('HLD', 'Primer: databases: replication, federation, sharding, SQL vs NoSQL', SDP + 'database'),
    S('HLD', 'Primer: caching', SDP + 'cache'),
    S('HLD', 'Primer: asynchronism, queues, back pressure', SDP + 'asynchronism'),
    S('HLD', 'Primer: back-of-the-envelope numbers', SDP + 'appendix', 'Learn the latency numbers and powers of two by heart.'),
] + [S('HLD', f'DDIA chapter {i}: {t}', 'https://dataintensive.net/', 'Book: Designing Data-Intensive Applications. One chapter per session; write a 5-line summary.')
     for i, t in enumerate(['Reliable, scalable, maintainable', 'Data models and query languages', 'Storage and retrieval', 'Encoding and evolution',
                            'Replication', 'Partitioning', 'Transactions', 'Trouble with distributed systems', 'Consistency and consensus',
                            'Batch processing', 'Stream processing', 'The future of data systems'], 1)]

GUIDED_HLD, GUIDED_LLD = 5, 10
HLD_PRACTICE = [S('HLD', f'Design {t} (guided: read the breakdown, then redraw it from memory)' if n < GUIDED_HLD else f'Design {t} (45 min timed, then read the breakdown)',
                  HI + 'problem-breakdowns/' + s,
                  'Read it twice, close it, redraw the whole design and say why each box is there.' if n < GUIDED_HLD else
                  'On paper or a doc: requirements, API, data model, high-level design, deep dives. Then compare and note what you missed.')
                for n, (s, t) in enumerate( [('bitly', 'a URL shortener'), ('dropbox', 'Dropbox'), ('ticketmaster', 'Ticketmaster'), ('whatsapp', 'WhatsApp'),
                             ('uber', 'Uber'), ('youtube', 'YouTube'), ('top-k', 'top-K videos'), ('web-crawler', 'a web crawler'),
                             ('google-docs', 'Google Docs'), ('yelp', 'Yelp'), ('leetcode', 'LeetCode'), ('tinder', 'Tinder'),
                             ('instagram', 'Instagram'), ('fb-live-comments', 'live comments'), ('fb-post-search', 'post search'),
                             ('strava', 'Strava'), ('online-auction', 'an online auction'), ('ad-click-aggregator', 'an ad click aggregator'),
                             ('distributed-cache', 'a distributed cache'), ('job-scheduler', 'a job scheduler'), ('payment-system', 'a payment system'),
                             ('robinhood', 'Robinhood'), ('gopuff', 'Gopuff')])]

LCPP = 'https://www.learncpp.com/cpp-tutorial/'
LLD_FOUNDATIONS = [
    S('LLD', 'Foundations: classes and objects in C++', LCPP + 'introduction-to-object-oriented-programming/', 'Write a small class with a constructor, private state and two methods.'),
    S('LLD', 'Foundations: inheritance', LCPP + 'introduction-to-inheritance/'),
    S('LLD', 'Foundations: virtual functions and polymorphism', LCPP + 'virtual-functions/'),
    S('LLD', 'Foundations: abstract classes and interfaces', LCPP + 'pure-virtual-functions-abstract-base-classes-and-interface-classes/', 'This is how C++ does interfaces. Every LLD answer uses them.'),
    S('LLD', 'Foundations: smart pointers and ownership', LCPP + 'introduction-to-smart-pointers-move-semantics/'),
    S('LLD', 'Foundations: reading and drawing UML class diagrams', 'https://www.visual-paradigm.com/guide/uml-unified-modeling-language/uml-class-diagram-tutorial/'),
]
LLD_STUDY = LLD_FOUNDATIONS + [
    S('LLD', 'OOP and SOLID principles', 'https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design'),
    S('LLD', 'Creational patterns: factory, builder, singleton', RG + 'creational-patterns'),
    S('LLD', 'Structural patterns: adapter, decorator, facade, composite', RG + 'structural-patterns'),
    S('LLD', 'Behavioral patterns: overview', RG + 'behavioral-patterns'),
    S('LLD', 'Strategy, observer and state in depth', RG + 'strategy', 'Also read the observer and state pages. These three show up in most LLD rounds.'),
    S('LLD', 'How to approach an LLD round', 'https://github.com/ashishps1/awesome-low-level-design'),
]
LLD_PRACTICE = [S('LLD', f'LLD: {n.replace("-", " ")} (guided, C++)' if i < GUIDED_LLD else f'LLD: {n.replace("-", " ")} (45 min, C++)', LLD + n + '.md',
                  'Read the write-up first. Then close it and implement it from memory in C++.' if i < GUIDED_LLD else
                  'Requirements, then classes and interfaces, then code the core flow in C++. Then compare with the write-up.')
                for i, n in enumerate(['parking-lot', 'lru-cache', 'vending-machine', 'elevator-system', 'logging-framework', 'tic-tac-toe',
                          'snake-and-ladder', 'library-management-system', 'pub-sub-system', 'splitwise', 'movie-ticket-booking-system',
                          'atm', 'task-management-system', 'chess-game', 'traffic-signal', 'coffee-vending-machine', 'hotel-management-system',
                          'car-rental-system', 'ride-sharing-service', 'food-delivery-service', 'digital-wallet-service', 'online-auction-system',
                          'stack-overflow', 'course-registration-system', 'concert-ticket-booking-system', 'online-shopping-service',
                          'restaurant-management-system', 'music-streaming-service', 'airline-management-system', 'cricinfo',
                          'linkedin', 'social-networking-service', 'online-stock-brokerage-system'])]

def design_queue():
    # 3 HLD + 2 LLD a week, studies before practice in each stream
    h, l = HLD_STUDY + HLD_PRACTICE, LLD_STUDY + LLD_PRACTICE
    out, pattern, i = [], 'HHLHL', 0
    while h or l:
        src = h if (pattern[i % 5] == 'H' and h) or not l else l
        out.append(src.pop(0)); i += 1
    return out

STAR = ['a conflict with a teammate or stakeholder', 'a project with unclear requirements', 'a failure and what you changed after it',
        'leading without authority', 'helping a teammate grow', 'pushing back on a decision', 'your highest-impact project',
        'learning something new fast under pressure']
def saturday_queue():
    out = [S('BEH', "Read how Google hires: the process, and Googleyness & Leadership", 'https://www.google.com/about/careers/applications/how-we-hire/'),
           S('BEH', 'Behavioral interview guide', 'https://www.techinterviewhandbook.org/behavioral-interview/')]
    stories = [S('BEH', f'Write a STAR story: {t}', 'https://www.techinterviewhandbook.org/behavioral-interview-questions/',
                 'Situation, task, action, result, in under 2 minutes spoken. Say it aloud twice.') for t in STAR]
    mock = lambda: S('MOCK', 'Mock interview (45 min): one LeetCode medium or hard in a Google Doc, thinking aloud',
                     'https://www.techinterviewhandbook.org/mock-interviews/', 'With a friend or a peer platform. Ask for a hire / no-hire verdict and why.')
    while stories:
        out.append(stories.pop(0)); out.append(mock())
    return out

STRIVER = 'https://takeuforward.org/prep-hub/strivers-180-master-dsa-patterns?page=sheet&open=none'
# Curriculum topic index each sheet section belongs to, so evenings practise the morning's topic.
SECTION_TOPIC = {'Binary Search': 1, 'Sliding Window and Two Pointers': 1, 'Arrays': 5, 'Graphs': 2, 'Heaps': 2, 'Dynamic Programming': 3,
                 'Linked List': 4, 'Stack and Queues': 4, 'Hashing': 5, 'Greedy Algorithms': 5, 'Mathematics': 6, 'Recursion and Backtracking': 7,
                 'Bit Manipulation': 7, 'Binary Trees': 8, 'Binary Search Trees': 8, 'Tries': 12, 'Strings': 12}
PATTERN_TOPIC = {'Two Pointers': 1, 'Sequence DP': 9, 'Partition DP': 9, 'Monotonic Stack / Queue': 15}
TOP150_TOPIC = {'Binary Search': 1, 'Two Pointers': 1, 'Sliding Window': 1, 'Graph General': 2, 'Graph BFS': 2, 'Heap': 2, '1D DP': 3,
                "Kadane's Algorithm": 3, 'Multidimensional DP': 9, 'Linked List': 4, 'Stack': 4, 'Array / String': 5, 'Hashmap': 5, 'Intervals': 5,
                'Matrix': 5, 'Math': 6, 'Bit Manipulation': 7, 'Backtracking': 7, 'Divide & Conquer': 7, 'Binary Tree General': 8,
                'Binary Tree BFS': 8, 'Binary Search Tree': 8, 'Trie': 12}

def coding_by_topic():
    # Striver 180 first (the user's main sheet), then Top Interview 150 problems not already on it, both grouped by curriculum topic.
    out, seen = {}, set()
    for p in json.load(open('striver180.json')):
        ti = PATTERN_TOPIC.get(p['pattern'], SECTION_TOPIC[p['section']])
        if p['slug']:
            if p['slug'] in seen: continue
            seen.add(p['slug'])
            it = {'k': 'lcp:' + p['slug'], 't': f"{p['title']} ({p['pattern']})", 'u': f"https://leetcode.com/problems/{p['slug']}/", 'r': 'Striver ' + p['tier']}
        else:
            it = {'k': 'tuf:' + p['tuf'], 't': f"{p['title']} ({p['pattern']})", 'u': STRIVER, 'r': 'Striver ' + p['tier'], 'n': 'Not on LeetCode. Open it from the Striver sheet.'}
        out.setdefault(ti, []).append(it)
    for g in json.load(open('lc_top150.json'))['planSubGroups']:
        for q in g['questions']:
            if q['titleSlug'] in seen: continue
            seen.add(q['titleSlug'])
            out.setdefault(TOP150_TOPIC[g['name']], []).append({'k': 'lcp:' + q['titleSlug'], 't': f"{q['title']} ({g['name']})",
                                                              'u': f"https://leetcode.com/problems/{q['titleSlug']}/", 'r': 'Top 150 ' + q['difficulty'].lower()})
    return out

GATES = {
    'coding': ['Striver 180 and the rest of Top Interview 150 done, timed, in a plain doc', '3 weeks in a row: unseen mediums in 25 min or less, hards in 45 min or less, 7 of 10 solved',
               'First submission accepted on 8 of the last 10 (the four checks are a habit)', 'Codeforces 1600+ or solving Div 2 C live most rounds'],
    'design': ['HLD foundations, Hello Interview "in a hurry" and the primer sections done', '10 practice designs done in 45 minutes each, compared with the breakdown',
               'Can explain the trade-off behind every box you draw (why this DB, why this cache, what breaks first)', '15 LLD problems coded in C++'],
    'behavioral': ['8 STAR stories written and said aloud', 'Each story under 2 minutes, with a measurable result'],
    'mocks': ['6 mock interviews done', '4 of the last 5 mocks ended in a hire verdict'],
    'apply': ['Ask for a referral', 'Apply for Software Engineer III (L4)', 'Keep the plan running while the process runs: mocks every week until onsite'],
}
