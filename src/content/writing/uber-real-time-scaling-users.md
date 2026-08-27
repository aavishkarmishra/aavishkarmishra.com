---
title: Uber's hardest scaling problem was its users
description: The Uber real-time paper names three scaling problems. Data is the one everybody quotes, and it's the one they solved by downloading software.
date: 2026-08-26
featured: false
draft: false
---

Fu and Soman's [Real-time Data Infrastructure at
Uber](https://arxiv.org/abs/2104.00087) (SIGMOD 2021) gets cited for its
numbers. Trillions of messages and petabytes a day as of October 2020, which is
the sentence that ends up in slide decks.

The numbers are real. They're also the least interesting third of the paper.
Section 1 names three scaling problems, not one: scaling data, scaling use
cases, scaling users. And if you go through the paper counting what Uber
*adopted* against what Uber *wrote*, the split falls almost entirely along that
line. Scaling data was solved by picking good software. Scaling use cases and
users is where all the code went.

## The adopted list is short

Kafka for streaming storage, Flink for stream processing, Pinot for OLAP,
Presto for interactive queries, HDFS for archival. Five systems, all off the
shelf, all chosen on ordinary grounds. Flink beat Storm in 2016 because Storm
took hours to chew through a backlog of millions of messages where Flink took
twenty minutes, and it beat Spark because Spark wanted five to ten times the
memory for the same job. Pinot beat Elasticsearch in 2018 on all three axes
they measured: four times less memory, eight times less disk, and queries two
to four times faster.

Those are procurement decisions. Good ones, well documented, but the kind of
thing a competent team makes in a quarter.

Now the written list: cluster federation, a metadata server, dead letter
queues, a consumer proxy, uReplicator, Chaperone, an offset management service,
FlinkSQL, a resource estimator, a rule-based failure recovery engine, a unified
job management layer, Pinot upserts, peer-to-peer segment recovery, a Presto
connector, Kappa+, a centralised schema repository, and a drag-and-drop UI.

Read that list again and ask what each item is *for*. A few of them buy speed.
Most of them stand between a person and a system so the person doesn't have to
know the system is there.

## Seven layers, and who walks in at each

Section 3 draws the stack before it names a single product, and the shape of it
is the argument I'm making. Bottom up: storage, stream, compute, OLAP, SQL,
API. Metadata sits across all of them.

<figure class="diagram">
<svg viewBox="0 0 400 204" role="img" aria-label="Six stacked layers, from API at the top down through SQL, OLAP, compute, stream and storage. API is annotated advanced users, SQL is annotated analysts and ops staff, and a bracket spanning OLAP down to storage is annotated invisible from both doors. A separate box below is labelled metadata.">
  <rect class="d-node-fill" x="0" y="0" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="16">API</text>
  <text class="d-label-sm" x="206" y="16">advanced users</text>
  <rect class="d-node-fill" x="0" y="28" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="44">SQL</text>
  <text class="d-label-sm" x="206" y="44">analysts and ops staff</text>
  <rect class="d-node-fill" x="0" y="56" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="72">OLAP</text>
  <rect class="d-node-fill" x="0" y="84" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="100">compute</text>
  <rect class="d-node-fill" x="0" y="112" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="128">stream</text>
  <rect class="d-node-fill" x="0" y="140" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="156">storage</text>
  <path class="d-edge" d="M200 60 H206 V160 H200"/>
  <text class="d-label-sm" x="212" y="113">invisible from both doors</text>
  <rect class="d-node-fill" x="0" y="176" width="196" height="24" rx="3"/>
  <text class="d-label" x="12" y="192">metadata</text>
  <text class="d-label-sm" x="206" y="192">versions and compatibility</text>
</svg>
<figcaption>Six layers and a seventh that cuts across all of them. Only the top
two are meant to be entered by a person.</figcaption>
</figure>

Four of those are machinery. Two are doors. The SQL layer exists because most
real-time OLAP stores have thin join support, so something above them has to
fill the gap. The API layer exists, in the paper's own description, for advanced
users the SQL interface doesn't serve. That's a stack with a tier list of humans
built into it: analysts and ops staff come in at SQL, engineers come in at API,
and everything below is supposed to be invisible from either door.

Metadata is the layer I'd have underrated. It holds the schemas for everything
the other layers touch, and its stated requirements are version history and
backward-compatibility checks across versions. Nothing about throughput. Its
entire job is stopping one team's schema change from breaking another team's
pipeline.

The stack also contains the tradeoff I come back to below. The paper
notes that joins can happen up at the SQL layer, or be pre-materialised down at
the compute layer and served straight out of OLAP without further processing, at
a higher cost. Same answer, different bill.

## Federation is a curtain

Kafka's own scaling story is dull: Uber found empirically that a cluster runs
best under 150 nodes, so past that you add clusters rather than nodes. Fine.

The interesting part is what federation hides. Producers and consumers see one
logical cluster; a metadata server knows which physical cluster holds a topic
and routes the request there. It's the man behind the curtain, and the entire
value of the arrangement is that nobody looks.

Because the alternative wasn't slower — it was a meeting. Moving a topic with
live consumers between clusters used to mean coordinating with every team
consuming it, getting them to shift traffic, and restarting their jobs.
Federation turns a cross-team migration into a routing table update.<span
class="sn"></span><span class="sidenote">This is the tell for the whole paper.
The bottleneck being removed is human coordination, and the fix happens to be
software.</span>

The dead letter queue is the same shape. Kafka gives you two options for a
message the consumer can't process: drop it, or retry forever and block
everything behind it. Neither is acceptable for something like trip receipts,
so Uber built a third — park the message in a separate topic, keep the line
moving, let a human decide later whether to purge or retry it. That's not a
performance feature. It's an admission that some failures need a person, and
the person shouldn't have to stop production to be that person.

Replication between clusters is another pair of built things. uReplicator moves
messages across clusters, with a rebalancing algorithm tuned to disturb as few
partitions as possible and standby workers it can shift load onto when traffic
spikes. Chaperone sits alongside it and does nothing but count: unique messages
per tumbling window, at every stage of the replication pipeline, each stage
compared against the last, alerting on any mismatch.

Chaperone produces no data anyone queries. It exists so that when a number looks
wrong, somebody can find out which hop lost it. The lessons section extends the
same idea across the whole ecosystem: every business event carries a unique
identifier, an application timestamp, a service name and a tier, so loss and
duplication can be tracked from Kafka through Flink and Pinot into Hive, in
every data centre.

## The consumer proxy exists because upgrades took months

My favourite detail in the paper has nothing to do with data volume at all.

Kafka's consumer library is clever — batching, compression, all client-side.
Clever clients are wonderful until you have tens of thousands of applications
running them, at which point every improvement you make to the library takes
months to actually reach production, because it ships inside other people's
deployments. Multiply that by four languages and the platform team spends its
life debugging code it can't upgrade.

So Uber inverted it. A proxy layer consumes from Kafka and pushes messages to a
gRPC endpoint the application registers. The complexity lives in the proxy,
which the platform team deploys on its own schedule, and the application holds
a generated client thin enough to be uninteresting.

The side effect is the good kind. Open-source Kafka caps a consumer group at
one instance per partition, so your parallelism is bounded by a number you
chose when you created the topic. Push-based dispatch doesn't inherit that
cap, so slow consumers get real parallelism back. A change made for deployability
bought throughput on the way past.

## FlinkSQL moves the work, it doesn't remove it

FlinkSQL is the most ambitious layer in the paper. A user writes a Calcite SQL
query; the platform compiles it to a logical plan, optimises it, produces a
physical plan, and emits a real Flink job. Data scientists and ops staff ship
streaming pipelines to production in hours without knowing Flink exists.

The paper is honest about the price, which is why I trust the rest of it. Those
hidden internals add, in the authors' words, "significant operational overhead
for the platform team". Nobody stopped tuning the jobs. The tuning moved.

<figure class="diagram">
<svg viewBox="0 0 400 168" role="img" aria-label="One box at the top labelled a SQL query represents what the user writes. Below, a chain of four boxes — plan, optimise, Flink job, cluster — with a feedback loop labelled monitor, autoscale and restart, represents what the platform team runs.">
  <text class="d-label-sm" x="0" y="10">what the user writes</text>
  <rect class="d-node-fill" x="0" y="18" width="186" height="28" rx="3"/>
  <text class="d-label" x="12" y="36">SELECT … GROUP BY city</text>
  <path class="d-edge" d="M93 46 V64"/><polygon class="d-arrow" points="93,68 89,60 97,60"/>
  <text class="d-label-sm" x="0" y="86">what the platform team then owns</text>
  <rect class="d-node-fill" x="0" y="94" width="62" height="28" rx="3"/>
  <text class="d-label" x="31" y="112" text-anchor="middle">plan</text>
  <path class="d-edge" d="M62 108 H76"/><polygon class="d-arrow" points="80,108 72,104 72,112"/>
  <rect class="d-node-fill" x="80" y="94" width="72" height="28" rx="3"/>
  <text class="d-label" x="116" y="112" text-anchor="middle">optimise</text>
  <path class="d-edge" d="M152 108 H166"/><polygon class="d-arrow" points="170,108 162,104 162,112"/>
  <rect class="d-node-fill" x="170" y="94" width="72" height="28" rx="3"/>
  <text class="d-label" x="206" y="112" text-anchor="middle">Flink job</text>
  <path class="d-edge" d="M242 108 H256"/><polygon class="d-arrow" points="260,108 252,104 252,112"/>
  <rect class="d-node-fill" x="260" y="94" width="66" height="28" rx="3"/>
  <text class="d-label" x="293" y="112" text-anchor="middle">cluster</text>
  <path class="d-edge" d="M293 122 V146 H31 V126"/><polygon class="d-arrow" points="31,122 27,130 35,130"/>
  <text class="d-label-sm" x="162" y="160" text-anchor="middle">monitor · autoscale · restart the stuck job</text>
</svg>
<figcaption>One box of user-facing surface, four boxes and a pager rotation
underneath it.</figcaption>
</figure>

Which is why the paper spends real space on resource estimation. Somebody had
to work out that a stateless Flink job is CPU-bound while a stream-stream join
is almost always memory-bound, then watch load and garbage collection to
autoscale, then write a rule-based engine that restarts jobs it finds wedged.
It's the sorcerer's apprentice problem: hand out a tool powerful enough to
start something, and someone has to come back and stop it. Several thousand
jobs, growing 30% a year, none of them written by the people carrying them.

That's still the right trade. Concentrating the expertise in one team that can
automate it beats scattering it across every team that wants a pipeline. But it
is a transfer, and it belongs in the estimate before you build the abstraction,
rather than showing up in the on-call rota afterwards.

## One SQL for everyone

Pinot is fast and it can't do joins or subqueries. That's an ordinary
limitation for a real-time OLAP store, and the fix is the one the stack
predicted: put a full SQL layer above it. Uber wired Pinot into Presto, already
the default engine for interactive queries internally.

The connector is where the care went, because a naive version would have thrown
away the thing they picked Pinot for. Presto is an in-memory MPP engine; left to
its own devices it will pull rows out of Pinot and do the work itself, ignoring
every index Pinot has. The first version pushed predicates down and stopped
there, limited by what the Connector API allowed. So they extended the Connector
API and Presto's planner to push projection, aggregation and limit down as well.
That's what gets these queries under a second, which the same SQL against Hive
would not.

In user terms this buys one dialect. The lessons section says the consolidation
was deliberate: two low-level languages, Java and Go, and PrestoSQL as the
single high-level one, with connectors built out to everything else. The Eats
ops team in section 5 is the payoff. During Covid they needed to hold
restaurants in several European countries inside occupancy limits, so they
explored real-time data with Presto queries over Pinot, found the metric that
mattered, and dropped the same query into a rule-based automation framework.
Exploration and production spoke the same language, so shipping it was a paste
rather than a rewrite.

## The one tradeoff worth stealing

Section 5 sets its use cases against each other on purpose, and that is where
the paper earns its keep.

Surge pricing wants freshness and availability, so it runs on a Kafka cluster
tuned for throughput rather than losslessness, and simply drops late messages.
A late event can't affect a price that already went out. Financial data on the
same platform accepts none of that. UberEats Restaurant Manager wants a p99
under a second on a fixed set of query shapes.

That last one produces the cleanest tradeoff in the paper. Restaurant Manager
gets its latency because Flink filters, rolls up and partially aggregates
before the data ever lands, and Pinot stores the result pre-aggregated. The
query is fast because most of the work already happened.

<figure class="diagram">
<svg viewBox="0 0 400 150" role="img" aria-label="Two horizontal bars of equal total length. The first spends most of its length in Flink at transform time and a little in Pinot at query time. The second is the reverse, spending little in Flink and most in Pinot.">
  <text class="d-label-sm" x="0" y="30">pre-materialise</text>
  <rect class="d-node-fill" x="94" y="16" width="176" height="26" rx="2"/>
  <text class="d-label" x="182" y="33" text-anchor="middle">roll up · filter · aggregate</text>
  <rect class="d-node-fill" x="270" y="16" width="54" height="26" rx="2"/>
  <text class="d-label" x="297" y="33" text-anchor="middle">scan</text>
  <text class="d-label-sm" x="182" y="56" text-anchor="middle">Flink, at write time</text>
  <text class="d-label-sm" x="297" y="56" text-anchor="middle">Pinot</text>
  <text class="d-label-sm" x="0" y="88">keep it raw</text>
  <rect class="d-node-fill" x="94" y="74" width="54" height="26" rx="2"/>
  <text class="d-label" x="121" y="91" text-anchor="middle">copy</text>
  <rect class="d-node-fill" x="148" y="74" width="176" height="26" rx="2"/>
  <text class="d-label" x="236" y="91" text-anchor="middle">filter · group · aggregate</text>
  <text class="d-label-sm" x="121" y="114" text-anchor="middle">Flink</text>
  <text class="d-label-sm" x="236" y="114" text-anchor="middle">Pinot, at query time</text>
  <text class="d-label-sm" x="209" y="140" text-anchor="middle">both bars are the same length</text>
</svg>
<figcaption>Restaurant Manager takes the top row. The Eats ops team, running
ad-hoc queries through Presto, needs the bottom one.</figcaption>
</figure>

The bar doesn't get shorter. Work you do in Flink is paid once per event, on
write, by the platform's compute budget. Work you leave for Pinot is paid on
every query, by the person waiting. Pre-aggregating buys latency and spends
flexibility: the dashboard answers its fixed questions fast and can't answer
new ones without a schema change.

Pinot's own numbers say why they cared. In two years at Uber it went from
dozens of gigabytes to hundreds of terabytes, and from hundreds of queries per
second to tens of thousands. At that ratio, work moved to write time is work
done once instead of ten thousand times a second.<span class="sn"></span><span
class="sidenote">The same logic that makes a materialised view worth it, at a
point on the curve where the answer stops being obvious and starts being
arithmetic.</span>

## Failover has a user interface too

Section 6 contains the most expensive sentence in the paper. Surge pricing runs
redundant Flink pipelines in every region, and the authors say plainly that this
is compute intensive.

They had little choice. The Flink job's state is too large to replicate
synchronously between regions, so each region computes its own from scratch. It
works because every region reads the same aggregate Kafka stream, so the states
converge on their own. One region's update service is stamped primary by a
coordinating service and writes the result into an active-active database, and
when a region goes dark another gets stamped instead. Redundant compute is what
they pay for not having to replicate state.

Services that can't accept that run the other way round. Payments and auditing
go active-passive: one named consumer reads from one designated primary region
at a time, and fails over when it has to.

Which creates a problem I wouldn't have anticipated, and it's a human-facing
one. On failover, where does the consumer resume? Not the high watermark, since
that silently skips everything in between and these are precisely the services
that accept no loss. Not the low watermark, since that's an unbounded backlog to
chew through in the middle of an incident. And an offset from one region means
nothing in another.

So there's a service for it. uReplicator checkpoints the mapping from source
offset to destination offset into an active-active database as it replicates,
and a sync job keeps offsets aligned across regions for the active-passive
consumers. Failover resumes from the latest synchronised offset. An entire
service exists so that whoever is running the disaster recovery has a
defensible answer to "start from where?"

## An operational limit set the architecture

The backfill section is the one I keep coming back to.

Backfill is unavoidable — new pipelines need testing against real history,
models need months of training data, and bugs get found after they've processed
a week of events. Kappa architecture is the elegant answer: run the same
streaming code over old data by rewinding Kafka far enough.

Uber can't. Kafka retention is capped at a few days, because at their volume
the storage and node-replacement operations aren't worth it. So Kappa is off
the table, and they built Kappa+ instead. Same stream processing logic, pointed
at Hive rather than Kafka, with the awkward parts handled: finding the
boundaries of a bounded input, throttling historical data that arrives far
faster than live traffic, and sizing windows for records that show up badly out
of order.

Under Hive is HDFS, the least glamorous component in the paper and the one
everything else leans on. Raw Avro logs land there from Kafka and get compacted
into Parquet, and that becomes the source of truth for every analytical dataset
at Uber, the thing that backfills Kafka, Pinot, and even some transactional and
key-value sinks. Flink checkpoints its offsets and per-container state there.
Pinot archives its segments there.

And it has no high-availability guarantee. The paper's conclusion is blunt about
it: they covered for the archival layer's availability with Flink's
checkpointing and Pinot's peer-to-peer segment recovery. The fix for the bottom
of the stack went in one layer up, which is worth recognising the next time the
storage layer is the part you can't change.

The architecture wasn't chosen on elegance. One operational number ruled out
the clean answer and everything downstream adapted. I've had exactly this
happen at a much smaller scale: Lambda stops at fifteen minutes, that number
isn't negotiable, and it decided the shape of an entire [export
pipeline](/writing/rendering-was-never-the-problem/). Find the number that
isn't moving before you draw the diagram.

## What transfers down, and what doesn't

The failure mode of reading a paper like this is copying the shape without the
scale. So, plainly: most of what Uber built here, you should not build.

Cluster federation needs multiple clusters to federate. Below that it's a
metadata server guarding nothing. The idea underneath it is cheap and does
transfer: clients address a logical name, and something else owns the mapping to
physical topology. Anyone who has moved a database behind a connection string
already believes this.

The consumer proxy is the one I'd expect to arrive earliest, because its trigger
isn't volume. It's the number of deploys you don't control. Uber's number was
tens of thousands of applications and a client library that took months to roll
forward, but the same argument bites at eight services owned by three teams.
Logic that lives in a client you don't deploy upgrades on someone else's
schedule.

Auditing is the cheapest thing on the list and the first thing everyone skips.
Chaperone stripped down is a count of what went in against what came out, per
stage. That fits in a cron job, and you'll want it the first time two dashboards
disagree.

FlinkSQL is the one to be careful with, because my own argument is the warning.
It works at Uber because there's a platform team to absorb the transferred work.
Build that abstraction without one and you haven't distributed the tuning,
you've volunteered for it: all of it, for every pipeline anyone writes, from now
on, and the people writing them don't know the tuning exists. Don't ship a
self-serve pipeline builder unless you want to be its operations department.

The all-active setup and the offset management service are pure scale artifacts.
Redundant Flink jobs in every region and a cross-region offset mapper are a
rounding error on Uber's budget and most of the year on a small one.

The write-time-versus-query-time choice transfers at every size, because it was
never really about Flink and Pinot. It's whether you materialise now or compute
later, which Postgres makes you decide on a table of ten thousand rows.

The pattern holds on the way down. What transfers is the work about people:
naming, auditing, who owns the upgrade. What doesn't is the work about volume.
Same split the paper opens with, arriving a second time from the other end.

## What I took from it

Three things, none of them about petabytes.

Every abstraction is a transfer, so name the recipient. FlinkSQL didn't delete
the tuning work; it moved the work off its users and onto one team, which was
the right call because that team could automate it. Say that part out loud when
you propose the layer.

A thin client is an architectural decision. Uber consolidated to two low-level
languages and one SQL dialect, and pushed cleverness out of clients into
proxies, because code that ships inside someone else's deployment upgrades on
someone else's schedule.

And find the immovable number first. Cluster size under 150 nodes, Kafka
retention of a few days, fifteen minutes on a Lambda. Those don't bend, and
everything you design around them will.

Fu and Soman make the general point more plainly than I have. Their own
conclusion credits the win to a layer of indirection between users and
technologies, and to what that layer did to the cost of supporting them. The
petabytes are in the abstract because petabytes are what gets read.
