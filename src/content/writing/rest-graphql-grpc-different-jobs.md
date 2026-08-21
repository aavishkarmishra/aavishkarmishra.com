---
title: REST, GraphQL and gRPC do different jobs
description: Where REST still wins, what GraphQL charges you at the door, and why gRPC breaks your L4 load balancer.
date: 2026-08-21
featured: false
draft: false
---

Every few months somebody declares one of these dead, and the thread runs to
four hundred replies without anyone changing their mind.

The framing is wrong. These aren't three candidates for one slot. They solve
different problems, and most systems that work end up using more than one of
them.

So here is what each one is good at, and — more usefully — the bill each one
hands you eighteen months later.

## REST wins by inheriting HTTP

REST's advantage isn't elegance. It's that HTTP got there first and already
solved the boring problems.

Caches you didn't write, retries you didn't implement, idempotency you get for
free on `GET` and `PUT`, and a debugging story that starts and ends with `curl`.
Every proxy, CDN, browser and corporate middlebox already speaks it.

```http
GET /articles/42 HTTP/1.1
If-None-Match: "a1b2c3"

HTTP/1.1 304 Not Modified
ETag: "a1b2c3"
Cache-Control: public, max-age=60
```

That `304` is the whole pitch. No application code ran, no database was
touched, and a machine you have never logged into decided your response was
still good and served it for you.<span class="sn"></span><span class="sidenote">This
is also why "we'll add caching later" is such an expensive sentence for the
other two. With REST, caching is the default you opt out of.</span>

### The bill: endpoints multiply

REST models resources. Screens don't want resources — they want *a screen*. Your
client needs a user, their last five orders, the items in those orders and the
review score on each item, and it needs all of that before it can render
anything.

<figure class="diagram">
<svg viewBox="0 0 400 132" role="img" aria-label="Four REST requests shown as bars staggered one after another, ending at four times the latency, compared with a single GraphQL request that finishes in one.">
  <text class="d-label" x="0" y="28">/user</text>
  <rect class="d-node-fill" x="90" y="18" width="58" height="12" rx="2"/>
  <text class="d-label" x="0" y="46">/orders</text>
  <rect class="d-node-fill" x="148" y="36" width="58" height="12" rx="2"/>
  <text class="d-label" x="0" y="64">/items</text>
  <rect class="d-node-fill" x="206" y="54" width="58" height="12" rx="2"/>
  <text class="d-label" x="0" y="82">/reviews</text>
  <rect class="d-node-fill" x="264" y="72" width="58" height="12" rx="2"/>
  <path class="d-edge-fail" d="M324 14 V90"/>
  <text class="d-label-fail" x="330" y="56">4× RTT</text>
  <text class="d-label" x="0" y="114">/graphql</text>
  <rect class="d-node-fill" x="90" y="104" width="76" height="12" rx="2"/>
  <path class="d-edge" d="M170 100 V120"/>
  <text class="d-label-sm" x="176" y="114">1× RTT</text>
</svg>
<figcaption>Each request has to finish before the next one knows what to ask
for. On a train, on 4G, this is the entire perceived performance of your app.</figcaption>
</figure>

The natural fix is a purpose-built endpoint. Then you need a second one:

```text
GET /users/42
GET /users/42/orders
GET /users/42/dashboard             ← invented for the web app
GET /users/42/dashboard-mobile      ← invented for iOS
GET /users/42/dashboard-mobile-v2   ← invented for iOS, again, in a hurry
```

Nobody designed that. It accreted. Every one of those is now load-bearing for a
client you can't force to update, which is how `v2` becomes permanent.

<figure class="diagram">
<svg viewBox="0 0 400 108" role="img" aria-label="A two-panel meme layout. Top panel, rejected: a mobile-specific dashboard endpoint, version two. Bottom panel, approved: one schema the client queries.">
  <rect class="d-node-fill" x="0" y="4" width="46" height="42" rx="3"/>
  <text class="d-label-fail" x="23" y="31" text-anchor="middle" style="font-size:18px">✕</text>
  <rect class="d-node-fill" x="52" y="4" width="348" height="42" rx="3"/>
  <text class="d-label" x="66" y="30">GET /users/42/dashboard-mobile-v2</text>
  <rect class="d-node-fill" x="0" y="54" width="46" height="42" rx="3"/>
  <text class="d-label" x="23" y="81" text-anchor="middle" style="font-size:18px">✓</text>
  <rect class="d-node-fill" x="52" y="54" width="348" height="42" rx="3"/>
  <text class="d-label" x="66" y="80">one schema, the client asks for the shape it needs</text>
</svg>
<figcaption>The Drake meme, minus the copyrighted photograph of Drake.</figcaption>
</figure>

## GraphQL: the client says what it needs

GraphQL stops guessing what the client wants and lets it ask.

```graphql
query Dashboard($id: ID!) {
  user(id: $id) {
    name
    orders(last: 5) {
      total
      items { sku title }
    }
  }
}
```

One round trip, no over-fetching, and six months of "can you add `avatarUrl` to
the orders endpoint" stops happening. That last part is worth more than it
sounds.

The bill arrives in three parts.

### 1. N+1 queries

That innocent query resolves `items` once per order. Five orders, six database
round trips. Bump the page size to fifty and you have fifty-one. The resolver is
three lines long and looks fine.

```js
// one query per order, and it scales with the page size
const items = ({ id }) => db.items.where({ orderId: id });

// one query per tick, whatever shape the request came in
const itemLoader = new DataLoader(async (orderIds) => {
  const rows = await db.items.whereIn('order_id', orderIds);
  return orderIds.map((id) => rows.filter((r) => r.order_id === id));
});
```

DataLoader isn't optional garnish. It batches every resolver call in a tick into
one query, and without it your page size is a load test.

### 2. Nested queries are a denial of service you shipped yourself

`user → orders → items → user → orders → items`. A query within a query within
a query, and unlike Inception nobody wakes up at the end. Fifteen lines an
intern could type by accident will pin every core you own.

```js
const server = new ApolloServer({
  schema,
  validationRules: [depthLimit(8), costAnalysis({ maximumCost: 1000 })],
});
```

Depth limits and cost analysis are the floor. Above that: persisted queries. The
client sends a hash, the server keeps the allowlist, and anything not on the
list doesn't get in.

### 3. You just traded away your CDN

One `POST /graphql`, opaque body, different answer every time. Every cache
between your server and your user shrugs and forwards it. That free `304` from
earlier is gone, and you will rebuild it in application code with Redis, and
maintain the invalidation yourself.<span class="sn"></span><span
class="sidenote">Persisted queries claw some of this back — a hash in the URL is
cacheable again — which is a second reason to adopt them.</span>

## gRPC: fast, terse and internal

gRPC is for calls between services you own. Protobuf over HTTP/2, compact on the
wire, unreadable without the schema, and no browser in sight. Both ends already
share every assumption, so nothing has to be self-describing.

```proto
syntax = "proto3";

service Orders {
  rpc Get(GetOrderRequest) returns (Order);
}

message Order {
  string id       = 1;
  int64  cents    = 2;
  reserved 3;  // was discount_cents — number retired, never reissued
  string currency = 4;
}
```

The numbers are the contract, not the field names. Old servers skip what they
don't recognise and keep running, which is how you deploy a schema change on
Tuesday and let the clients catch up on Friday. Once a number has been used it
never gets reused, which is what `reserved` is for.

The other underrated gift is deadline propagation. A timeout set at the edge
travels the whole call graph, so a request the user abandoned stops burning CPU
seven services deep.

```go
ctx, cancel := context.WithTimeout(ctx, 300*time.Millisecond)
defer cancel()
order, err := client.Get(ctx, &pb.GetOrderRequest{Id: id})
```

### The bill: your load balancer stops balancing

This is the one that gets people at 2am. HTTP/2 multiplexes thousands of
requests down one long-lived TCP connection, which is the efficiency everyone
came for. Your L4 load balancer balances *connections*.

<figure class="diagram">
<svg viewBox="0 0 400 148" role="img" aria-label="Two clients each open one long-lived connection through an L4 load balancer. Both land on pod one, which takes all the requests, while pods two and three sit idle.">
  <rect class="d-node-fill" x="0" y="26" width="66" height="28" rx="3"/>
  <text class="d-label" x="33" y="44" text-anchor="middle">client A</text>
  <rect class="d-node-fill" x="0" y="86" width="66" height="28" rx="3"/>
  <text class="d-label" x="33" y="104" text-anchor="middle">client B</text>
  <path class="d-edge" d="M66 40 H126 V64"/>
  <path class="d-edge" d="M66 100 H126 V80"/>
  <rect class="d-node-fill" x="126" y="56" width="66" height="32" rx="3"/>
  <text class="d-label" x="159" y="76" text-anchor="middle">L4 LB</text>
  <path class="d-edge" d="M192 72 H240 V26 H286"/>
  <polygon class="d-arrow" points="290,26 282,22 282,30"/>
  <path class="d-edge-fail" d="M240 72 V80 H286"/>
  <path class="d-edge-fail" d="M240 80 V132 H286"/>
  <rect class="d-node-fill" x="290" y="12" width="66" height="28" rx="3"/>
  <text class="d-label" x="323" y="30" text-anchor="middle">pod 1</text>
  <text class="d-label-fail" x="362" y="30">100%</text>
  <rect class="d-node-fill" x="290" y="66" width="66" height="28" rx="3"/>
  <text class="d-label" x="323" y="84" text-anchor="middle">pod 2</text>
  <text class="d-label-sm" x="362" y="84">idle</text>
  <rect class="d-node-fill" x="290" y="118" width="66" height="28" rx="3"/>
  <text class="d-label" x="323" y="136" text-anchor="middle">pod 3</text>
  <text class="d-label-sm" x="362" y="136">idle</text>
</svg>
<figcaption>Two connections, three pods, one very warm pod. Autoscaling reads
low average CPU and helpfully removes capacity.</figcaption>
</figure>

It's a bouncer counting cars in the car park to work out how full the club is.
Ten people arrive in one car and the club is empty, officially.

You fix it at L7 — a proxy or mesh that balances per request — or with
client-side load balancing and a name resolver, so clients spread their own
connections across pods. Either way it's real infrastructure, and it's the part
nobody mentions in the benchmark post.

## You use all three

<figure class="diagram">
<svg viewBox="0 0 400 132" role="img" aria-label="Browsers and mobile clients hit a public edge speaking REST and GraphQL, which then talks gRPC to three internal services.">
  <rect class="d-node-fill" x="0" y="18" width="72" height="28" rx="3"/>
  <text class="d-label" x="36" y="36" text-anchor="middle">browser</text>
  <rect class="d-node-fill" x="0" y="72" width="72" height="28" rx="3"/>
  <text class="d-label" x="36" y="90" text-anchor="middle">mobile</text>
  <path class="d-edge" d="M72 32 H120 V52"/>
  <path class="d-edge" d="M72 86 H120 V72"/>
  <rect class="d-node-fill" x="128" y="44" width="90" height="36" rx="3"/>
  <text class="d-label" x="173" y="60" text-anchor="middle">edge</text>
  <text class="d-label-sm" x="173" y="73" text-anchor="middle">REST + GraphQL</text>
  <path class="d-edge" d="M218 62 H252"/>
  <polygon class="d-arrow" points="256,62 248,58 248,66"/>
  <text class="d-label-sm" x="224" y="38">gRPC</text>
  <rect class="d-node-fill" x="296" y="6" width="84" height="26" rx="3"/>
  <text class="d-label" x="338" y="23" text-anchor="middle">orders</text>
  <rect class="d-node-fill" x="296" y="50" width="84" height="26" rx="3"/>
  <text class="d-label" x="338" y="67" text-anchor="middle">inventory</text>
  <rect class="d-node-fill" x="296" y="94" width="84" height="26" rx="3"/>
  <text class="d-label" x="338" y="111" text-anchor="middle">pricing</text>
  <path class="d-edge" d="M256 62 H276 V19 H292"/>
  <path class="d-edge" d="M276 62 H292"/>
  <path class="d-edge" d="M276 62 V107 H292"/>
</svg>
<figcaption>The boundary does the translating. Nobody outside it has ever heard
of your protobufs.</figcaption>
</figure>

The pattern that keeps working: a public edge that speaks HTTP the way the
internet expects, and internal calls that speak gRPC because both ends are
yours and you control every deploy.

So the question is never which one is best. It is:

- Third parties, browsers, or anything you want cached and curl-able? REST.
- Several clients with different screens and a schema you own end to end?
  GraphQL, with DataLoader, depth limits and persisted queries on day one rather
  than in the incident review.
- Service to service, inside your own network, latency you can feel? gRPC, and
  budget for L7 balancing before it becomes a page.
- Two services and four engineers? JSON over HTTP. Ship the product and come
  back to this post later.
