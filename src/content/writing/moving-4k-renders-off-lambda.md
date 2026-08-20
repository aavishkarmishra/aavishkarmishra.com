---
title: Why 4K renders left Lambda for the browser
description: Distributed Lambda rendering is elegant right up until the fifteen-minute wall. What we measured, what self-hosting would have cost, and why the client won.
date: 2026-08-24
featured: true
draft: true
---

The export pipeline had one job: take a timeline the user assembled in the
editor and produce a single 4K/60fps file. Everything upstream of it worked.
Capture, re-encode, enhancement, proxy renditions, the TTS voiceover synced
through FFmpeg — all of that was solved. Export was the part that kept
failing, and it failed in a way that could not be tuned away.

## The shape of the problem

<figure class="diagram">
<svg viewBox="0 0 400 200" role="img" aria-label="Three options for the render step: distributed Lambda, self-hosted encode, and the browser. The first two were rejected.">
  <rect class="d-node-fill" x="0" y="78" width="112" height="34" rx="3"/>
  <text class="d-label" x="14" y="99">render request</text>

  <path class="d-edge-fail" d="M112 95 C 160 95, 164 31, 208 31"/>
  <polygon class="d-arrow-fail" points="212,31 204,27 204,35"/>
  <rect class="d-node-fill" x="212" y="14" width="184" height="34" rx="3"/>
  <text class="d-label" x="226" y="35">distributed Lambda</text>
  <text class="d-label-fail" x="226" y="62">hard 15-minute execution ceiling</text>

  <path class="d-edge-fail" d="M112 95 H 208"/>
  <polygon class="d-arrow-fail" points="212,95 204,91 204,99"/>
  <rect class="d-node-fill" x="212" y="78" width="184" height="34" rx="3"/>
  <text class="d-label" x="226" y="99">self-hosted encode</text>
  <text class="d-label-fail" x="226" y="126">several dollars per render, per user</text>

  <path class="d-edge" d="M112 95 C 160 95, 164 159, 208 159"/>
  <polygon class="d-arrow" points="212,159 204,155 204,163"/>
  <rect class="d-node-fill" x="212" y="142" width="184" height="34" rx="3"/>
  <text class="d-label" x="226" y="163">the client</text>
  <text class="d-label-sm" x="226" y="190">their hardware, their electricity</text>
</svg>
<figcaption>Three ways to render. Two of them we paid to find out about.</figcaption>
</figure>

Lambda was the obvious first answer, and for short clips it was the right one.
Fan out by segment, render in parallel, concatenate, done. The failure mode
only shows up on long-form video: a single segment of 4K/60fps footage does not
finish inside fifteen minutes, and fifteen minutes is not a quota you can
raise.<span class="sn"></span><span class="sidenote">It is a hard limit on the
execution model, not a soft default. There is no support ticket that fixes
this.</span> Splitting more finely helps until the segments get short enough
that concatenation artefacts and per-invocation overhead eat the gain.

TODO(interview): the actual segment length where this broke down, and what the
concatenation artefacts looked like.

## Pricing the obvious alternative

The next answer is to stop being clever and run the encode on a machine we
control. That works — encoding is exactly what a big instance is for — but
export is a *user-triggered* operation, so the cost scales with how often
people click the button rather than with anything we control.

TODO(interview): what you actually measured here — instance type, wall-clock
per render, and the per-render figure you derived. Public list prices only,
no internal numbers.

At that point the question stops being technical. A feature that costs
meaningful money every time a user touches it either raises the price of the
product or gets rationed, and rationing an export button is a bad product.

## Where the compute was already sitting

The user has a machine. It rendered the preview. It has the source media in
front of it, or can get it. Moving the render client-side turns the most
expensive operation in the product into the one operation that costs us
nothing.<span class="sn"></span><span class="sidenote">It also removes the
upload of the source media in the common case, which was its own latency
problem.</span>

TODO(interview): what broke when you moved it — browser variance, memory
limits, what you had to keep server-side as a fallback.

## What I would tell myself earlier

Find the hard limits in a prototype, not in production. The fifteen-minute
ceiling is documented; we could have read it against a realistic worst-case
input on day one instead of discovering it with real users on real footage.
The cost model deserves the same treatment. Both of those are half a day of
work, and either one would have pointed straight at the answer we eventually
shipped.
