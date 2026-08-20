---
title: Rendering was never the problem
description: We spent a year and eight months making video renders faster and cheaper. Then we asked customers what they were waiting on, and it was not the render.
date: 2026-08-24
featured: true
draft: true
---

For most of two years, export was the part of the product I thought about most.
Everything before it was ours: capture, re-encode of camera and screen, quality
enhancement, proxy renditions, an editor with TTS voiceover synced through
FFmpeg. Then the user pressed export, and the real work happened on Remotion
Lambda.

Lambda stops at fifteen minutes. Remotion Lambda spreads a composition across
invocations, and we cut ours into sections of eight to ten minutes so no single
invocation came near the
ceiling.<span class="sn"></span><span class="sidenote">Fifteen minutes is a
property of the execution model, not a quota. There is no support ticket that
raises it.</span> The headroom mattered more than the throughput. A render that dies at minute
fourteen has spent fourteen minutes and produced nothing, and the user has
watched the whole thing happen.

<figure class="diagram">
<svg viewBox="0 0 400 64" role="img" aria-label="A progress bar filling towards a dashed line marked 15:00, stopping just short of it and resetting to zero, over and over.">
  <text class="d-label-sm" x="0" y="10">rendering</text>
  <text class="d-label-fail" x="292" y="10">15:00</text>

  <rect class="d-track" x="0" y="18" width="286" height="11" rx="2"/>
  <rect class="d-fill" x="0" y="18" height="11" rx="2"/>
  <path class="d-ceiling" d="M290 14 V33"/>

  <text class="d-boom" x="298" y="27" style="font: 400 11px var(--sans)">nothing</text>
  <text class="d-label-sm" x="0" y="52">and again, and again, and again</text>
</svg>
<figcaption>Fourteen minutes of compute, one file of size zero, and a customer
who watched every second of it.</figcaption>
</figure>

That worked. We ran it for a year and eight months and tracked what every
single render cost us, which turned out to be the most useful thing we did,
though not for the reason we expected.

## The renderer we decided not to build

Once you have outgrown someone else's renderer, the appealing move is to build
your own. We could see the shape of it: own the encode, run it on instances we
picked, split the work however we wanted, stop paying a per-render premium.

So we priced it, and the number that mattered was not the AWS bill. It was us. A
renderer is not a project you finish. It is queueing, retries, storage
lifecycle, cost monitoring, capacity to keep warm, and somebody awake when an
export fails at two in the morning. We were three engineers and two designers.
Building it meant one of the three permanently maintaining infrastructure whose
entire job was to produce a file.

Measured that way it did not lose narrowly. It lost badly, and that part of the
decision was easy.

## The question we should have asked first

The harder part is that we had been asking the wrong question for a year. Every
version of it — sectioning, cost per render, build or buy — assumed that render
speed was what stood between a customer and the thing they wanted.

Then we talked to customers, and they were not waiting on renders. They were
waiting to *share*. Getting an article or a video in front of someone else was
the slow step in their day, and rendering was somewhere behind it.

<figure class="diagram">
<svg viewBox="0 0 400 120" role="img" aria-label="A four-step flow: edit, render, share, viewer. A bracket above the render step is labelled 'a year of our attention'. A bracket below the share step is labelled 'what customers were waiting on'.">
  <path class="d-edge" d="M88 26 V19 H164 V26"/>
  <text class="d-label-sm" x="126" y="12" text-anchor="middle">a year of our attention</text>

  <rect class="d-node-fill" x="0" y="40" width="76" height="32" rx="3"/>
  <text class="d-label" x="38" y="60" text-anchor="middle">edit</text>
  <path class="d-edge" d="M76 56 H84"/><polygon class="d-arrow" points="88,56 80,52 80,60"/>

  <rect class="d-node-fill" x="88" y="40" width="76" height="32" rx="3"/>
  <text class="d-label" x="126" y="60" text-anchor="middle">render</text>
  <path class="d-edge" d="M164 56 H172"/><polygon class="d-arrow" points="176,56 168,52 168,60"/>

  <rect class="d-node-fill" x="176" y="40" width="76" height="32" rx="3"/>
  <text class="d-label" x="214" y="60" text-anchor="middle">share</text>
  <path class="d-edge" d="M252 56 H260"/><polygon class="d-arrow" points="264,56 256,52 256,60"/>

  <rect class="d-node-fill" x="264" y="40" width="76" height="32" rx="3"/>
  <text class="d-label" x="302" y="60" text-anchor="middle">viewer</text>

  <path class="d-edge-fail" d="M176 86 V93 H252 V86"/>
  <text class="d-label-fail" x="214" y="107" text-anchor="middle">what customers were waiting on</text>
</svg>
<figcaption>We had spent a year on the second box.</figcaption>
</figure>

That reframes the render problem entirely. If nobody is waiting on the render,
you do not need it to be fast. You need it to stop costing you money and
attention.

## Moving it onto the machine that was already there

So we stopped rendering in the cloud. The product became a desktop app, and
rendering moved onto the user's own machine: FFmpeg and Remotion running
locally, on hardware that had already rendered the preview and was sitting idle
while our Lambdas did the same arithmetic a second time.

It is slower on some machines, and that turned out not to matter. Most
computers will get through a fifteen or twenty minute video, and taking a while
longer costs the customer nothing they had ever mentioned wanting. What it
bought us was the whole cloud render bill, and the attention of three
engineers, which went into editing and sharing instead. The renderer stopped
being a system we operated and became a thing that happens on someone else's
laptop while they make tea.

We had suspected about a year in that a web app was the wrong shape for this
product. Knowing it did not help much. The customers we had were on the web,
and a desktop app they could move to takes as long as it takes to build. We
knew exactly where the couch had to go and still spent eight months getting it
up the stairs, running the Lambda version the whole way.

## What I would take from it

Two things, and the second one cost more than the first.

Price your own time before the infrastructure. The flattering version of a
decision is the one where the interesting system is also the correct one. On a
team of three it almost never is.

Then: measure the thing customers are waiting on, not the thing you happen to
be working on. We had a year of per-render cost data and no idea where the wait
actually was. Both of those took roughly a day to find out. We did one of them
immediately and the other far too late.
