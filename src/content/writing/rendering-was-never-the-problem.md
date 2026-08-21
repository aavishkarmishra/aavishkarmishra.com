---
title: Rendering was never the problem
description: We spent a year and eight months making video renders faster and cheaper. Then we asked customers what they were waiting on, and it was not the render.
date: 2025-03-24
featured: true
draft: false
---

We built the entire game and then handed somebody else the controller for the
final boss.

Everything before export was ours: capture, re-encode of camera and screen,
quality enhancement, proxy renditions, an editor with TTS voiceover synced
through FFmpeg. Then the user pressed export, and the work happened on Remotion
Lambda.

## Lambda turns back into a pumpkin at fifteen minutes

Cinderella had until midnight. Lambda gives you fifteen minutes, and it is just
as non-negotiable. Remotion Lambda spreads a composition across invocations, so
we cut ours into sections of eight to ten minutes. Nothing came near the
ceiling.<span class="sn"></span><span class="sidenote">Fifteen minutes is a
property of the execution model, not a quota. There is no support ticket that
raises it.</span>

We wanted the margin more than the speed. A render that dies at minute fourteen
has burned fourteen minutes and produced nothing, and the user watched it
happen. Then they hit export again. It's Groundhog Day without the character
development.

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

## The renderer we didn't build

Once you outgrow someone else's renderer, the obvious move is to build your own.
We could see the shape of it. Own the encode, run it on instances we picked,
split the work how we wanted, stop paying per render.

The entire plot of Jurassic Park is a team so busy proving they could that
nobody stopped to ask whether they should. Build-versus-buy has exactly that
failure mode. We could, comfortably. Whether we should was a different question,
and it turned out to be a question about us rather than about rendering.

So we priced it. The number that decided it wasn't the AWS bill. It was us.

<figure class="diagram">
<svg viewBox="0 0 400 146" role="img" aria-label="An iceberg comparison. Above the waterline, one box: encode a file. Below it, six boxes: queueing, retries, storage lifecycle, cost monitoring, warm capacity, and someone awake at 2am.">
  <text class="d-label-sm" x="0" y="12">what we were pricing</text>
  <rect class="d-node-fill" x="137" y="18" width="126" height="24" rx="3"/>
  <text class="d-label" x="200" y="34" text-anchor="middle">encode a file</text>
  <path class="d-edge" d="M0 54 H400"/>
  <text class="d-label-fail" x="0" y="70">what a renderer actually is</text>
  <rect class="d-node-fill" x="0" y="78" width="126" height="24" rx="3"/>
  <text class="d-label" x="63" y="94" text-anchor="middle">queueing</text>
  <rect class="d-node-fill" x="137" y="78" width="126" height="24" rx="3"/>
  <text class="d-label" x="200" y="94" text-anchor="middle">retries</text>
  <rect class="d-node-fill" x="274" y="78" width="126" height="24" rx="3"/>
  <text class="d-label" x="337" y="94" text-anchor="middle">storage lifecycle</text>
  <rect class="d-node-fill" x="0" y="110" width="126" height="24" rx="3"/>
  <text class="d-label" x="63" y="126" text-anchor="middle">cost monitoring</text>
  <rect class="d-node-fill" x="137" y="110" width="126" height="24" rx="3"/>
  <text class="d-label" x="200" y="126" text-anchor="middle">capacity kept warm</text>
  <rect class="d-node-fill" x="274" y="110" width="126" height="24" rx="3"/>
  <text class="d-label" x="337" y="126" text-anchor="middle">someone awake at 2am</text>
</svg>
<figcaption>We priced the top box. The bill was the other six.</figcaption>
</figure>

We were three engineers and two designers. Building it meant one of the three
maintaining infrastructure whose only job was to produce a file.

> All we have to decide is what to do with the time that is given us.
>
> — Gandalf, *The Fellowship of the Ring*

A five-person company has one real budget and it isn't the one in dollars.

## We were counting the wrong stat

Moneyball is a story about a roomful of scouts who measured the wrong things
brilliantly for decades. We had a year of per-render cost data, tracked
carefully and reviewed often, and not one number in it told us where our
customers were waiting.

Sectioning, cost per render, build or buy: all of it assumed render speed was
what stood between a customer and the thing they wanted.

Then we talked to customers. They weren't waiting on renders. They were waiting
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

If nobody is waiting on the render, it doesn't need to be fast. It needs to stop
costing us money and attention.

## The render machine was in the room the whole time

Every horror film has the moment where the call turns out to be coming from
inside the house. Ours was less dramatic: the machine that could render the
video was already sitting in front of the user, and it had just finished
rendering the preview.

So we stopped rendering in the cloud. The product became a desktop app, and
rendering moved onto the user's machine: FFmpeg and Remotion running locally, on
hardware that had already done the hard part once.

It's slower on some machines. That turned out not to matter. Most computers get
through a fifteen or twenty minute video, and taking longer costs the customer
nothing they had ever asked us for. We got back the cloud render bill and the
attention of three engineers, which went into editing and sharing instead.

We had suspected a year in that a web app was the wrong shape for this product.
Knowing it didn't help much. Our customers were on the web, and a desktop app
takes as long as it takes to build. Ross's problem was never working out where
the couch had to go. It was the stairs. We knew the answer for eight months
while we built it, and we ran the Lambda version the whole way up.

## What I would do differently

Price my own time before the infrastructure. The flattering version of a
decision is the one where the interesting system is also the right one, and it
sings the whole time you're deciding. On a team of three it usually isn't the
right one. Tie yourself to the mast and run the numbers on your own headcount
first.

And measure what customers are waiting on, not what I happen to be working on.
We had a year of per-render cost data and no idea where the wait was. Both took
about a day to find out. We did one immediately and the other far too late.
