---
title: Rendering was never the problem
description: We spent a year and eight months making video renders faster and cheaper. Then we asked customers what they were waiting on, and it was not the render.
date: 2026-08-24
featured: true
draft: true
---

Export was the one part of the product we did not own.

Everything before it we built: capture, re-encode of camera and screen, quality
enhancement, proxy renditions, an editor with TTS voiceover synced through
FFmpeg. Then the user pressed export, and the work happened on Remotion Lambda.

## Sectioning, and why we wanted the margin

Lambda stops at fifteen minutes. Remotion Lambda spreads a composition across
invocations, so we cut ours into sections of eight to ten minutes. Nothing came
near the ceiling.<span class="sn"></span><span class="sidenote">Fifteen minutes
is a property of the execution model, not a quota. There is no support ticket
that raises it.</span>

We wanted the margin more than the speed. A render that dies at minute fourteen
has burned fourteen minutes and produced nothing, and the user watched it
happen.

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

That setup ran for a year and eight months. We tracked what every render cost us
for the whole of it.

## The renderer we did not build

Once you outgrow someone else's renderer, the obvious move is to build your own.
We could see the shape of it. Own the encode, run it on instances we picked,
split the work how we wanted, stop paying per render.

So we priced it. The number that decided it was not the AWS bill. It was us.

A renderer is queueing, retries, storage lifecycle, cost monitoring, capacity to
keep warm, and someone awake when an export fails at two in the morning. We were
three engineers and two designers. Building it meant one of the three
maintaining infrastructure whose only job was to produce a file.

> All we have to decide is what to do with the time that is given us.
>
> — Gandalf, *The Fellowship of the Ring*

A five-person company has one real budget and it is not the one in dollars.

## The question we should have asked first

We had been asking the wrong question for a year. Sectioning, cost per render,
build or buy: all of it assumed render speed was what stood between a customer
and the thing they wanted.

Then we talked to customers. They were not waiting on renders. They were waiting
to share. Getting an article or a video in front of someone else was the slow
step in their day. Rendering was somewhere behind it.

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

If nobody is waiting on the render, it does not need to be fast. It needs to
stop costing us money and attention.

## Moving it to the machine that was already there

We stopped rendering in the cloud. The product became a desktop app, and
rendering moved onto the user's machine: FFmpeg and Remotion running locally, on
hardware that had already rendered the preview.

It is slower on some machines. That turned out not to matter. Most computers get
through a fifteen or twenty minute video, and taking longer costs the customer
nothing they had ever asked us for. We got back the cloud render bill and the
attention of three engineers, which went into editing and sharing instead.

We had suspected a year in that a web app was the wrong shape for this product.
Knowing it did not help much. Our customers were on the web, and a desktop app
takes as long as it takes to build. We knew where the couch had to go. It still
took eight months to get it up the stairs, and we ran the Lambda version the
whole way.

## What I would do differently

Price my own time before the infrastructure. The flattering version of a
decision is the one where the interesting system is also the right one. On a
team of three it usually is not.

And measure what customers are waiting on, not what I happen to be working on.
We had a year of per-render cost data and no idea where the wait was. Both took
about a day to find out. We did one immediately and the other far too late.
