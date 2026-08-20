---
title: The render pipeline we decided not to build
description: Remotion Lambda took us most of the way. The obvious next step was to build our own renderer, and with three engineers that was exactly the wrong thing to build.
date: 2026-08-24
featured: true
draft: true
---

Export was the last part of the product we did not own. Everything before it was
ours: capture, re-encode of camera and screen, quality enhancement, proxy
renditions, an editor with TTS voiceover synced through FFmpeg. Then the user
pressed export, and the actual work happened on Remotion Lambda.

## What sectioning bought us

Lambda stops at fifteen minutes. Remotion Lambda spreads a composition across
invocations, and we cut ours into sections of eight to ten minutes so that no
single invocation came near the
ceiling.<span class="sn"></span><span class="sidenote">Fifteen minutes is a
property of the execution model, not a quota. There is no support ticket that
raises it.</span>

The headroom mattered more than the throughput. A render that dies at minute
fourteen has spent fourteen minutes and produced nothing, and the user is
sitting in front of a progress bar the whole time.

TODO(interview): what specifically pushed you past what sectioning could
absorb — longer videos, higher resolution, cost, queue times?

## The obvious next step

Once you have outgrown someone else's renderer, the appealing move is to build
your own. We could see the shape of it clearly: own the encode, run it on
instances we picked, split the work however we wanted, stop paying a per-render
premium to a third party.

<figure class="diagram">
<svg viewBox="0 0 400 200" role="img" aria-label="Three options for rendering: Remotion Lambda with sectioning, building our own pipeline, or rendering on the client. Building our own was rejected on cost of engineering time.">
  <rect class="d-node-fill" x="0" y="78" width="104" height="34" rx="3"/>
  <text class="d-label" x="14" y="99">export request</text>

  <path class="d-edge" d="M104 95 C 150 95, 156 31, 200 31"/>
  <polygon class="d-arrow" points="204,31 196,27 196,35"/>
  <rect class="d-node-fill" x="204" y="14" width="192" height="34" rx="3"/>
  <text class="d-label" x="218" y="35">Remotion Lambda, sectioned</text>
  <text class="d-label-sm" x="218" y="62">fine until the videos got longer</text>

  <path class="d-edge-fail" d="M104 95 H 200"/>
  <polygon class="d-arrow-fail" points="204,95 196,91 196,99"/>
  <rect class="d-node-fill" x="204" y="78" width="192" height="34" rx="3"/>
  <text class="d-label" x="218" y="99">a renderer of our own</text>
  <text class="d-label-fail" x="218" y="126">costs three engineers, permanently</text>

  <path class="d-edge" d="M104 95 C 150 95, 156 159, 200 159"/>
  <polygon class="d-arrow" points="204,159 196,155 196,163"/>
  <rect class="d-node-fill" x="204" y="142" width="192" height="34" rx="3"/>
  <text class="d-label" x="218" y="163">render on the client</text>
  <text class="d-label-sm" x="218" y="190">the machine was already there</text>
</svg>
<figcaption>The middle option is the one an engineer wants to build.</figcaption>
</figure>

So we priced it, and the number that mattered was not the AWS bill. It was us.
A renderer is not a project you finish. It is queueing, retries, storage
lifecycle, cost monitoring, a fleet to keep warm, and someone awake when an
export fails at two in the morning. We were three engineers and two designers.
Taking that on meant one of the three permanently maintaining infrastructure
whose only job was to produce a file.

Measured that way, building it did not lose narrowly. It lost badly.

## Where the compute already was

The user's machine had already rendered the preview. It had the timeline, it had
the source media, and it was sitting idle while our Lambdas did the same
arithmetic a second time. Moving the render to the client did not just remove a
bill, it removed an entire system we would otherwise have had to own.

TODO(interview): what actually runs client-side now — ffmpeg.wasm, WebCodecs,
canvas capture? And how does the TTS voiceover stay in sync without FFmpeg on
the server?

TODO(interview): what broke when you moved it — memory ceilings, background tab
throttling, Safari, older machines? Is there still a server-side fallback?

TODO(interview): what changed for users, and how long did the Lambda version
run before you switched?

## What I would tell myself

Price your own time first, before the infrastructure. The version of this
decision I would have got wrong is the flattering one, where the interesting
system is also the correct one. It usually is not, and on a team of three the
gap is not close. The best thing we built that quarter was the thing we decided
not to build.
