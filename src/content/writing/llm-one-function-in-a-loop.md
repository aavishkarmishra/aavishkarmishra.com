---
title: An LLM is one function in a loop
description: A language model returns one probability distribution over its vocabulary. Temperature, hallucination and chain of thought all fall out of that.
date: 2026-05-08
featured: false
draft: false
---

Almost everything that surprises people about language models comes from one
mechanism, and it's smaller than the surprise.

The model is a function. It takes the tokens you have so far and returns a score
for every token in its vocabulary — one score per candidate, for the very next
position, and then the call is over. It isn't holding a sentence, an answer, or
a plan for the paragraph it's about to write. You just call it again.

<figure class="diagram">
<svg viewBox="0 0 400 104" role="img" aria-label="Five token boxes feed into a box labelled model, which outputs one score for every token in the vocabulary, shown as a row of bars of different heights trailing off into an ellipsis.">
  <text class="d-label-sm" x="0" y="10">tokens so far</text>
  <rect class="d-node-fill" x="0" y="18" width="34" height="22" rx="2"/>
  <text class="d-label" x="17" y="33" text-anchor="middle">The</text>
  <rect class="d-node-fill" x="37" y="18" width="46" height="22" rx="2"/>
  <text class="d-label" x="60" y="33" text-anchor="middle">deploy</text>
  <rect class="d-node-fill" x="86" y="18" width="40" height="22" rx="2"/>
  <text class="d-label" x="106" y="33" text-anchor="middle">failed</text>
  <path class="d-edge" d="M126 29 H146"/><polygon class="d-arrow" points="150,29 142,25 142,33"/>
  <rect class="d-node-fill" x="150" y="14" width="60" height="30" rx="3"/>
  <text class="d-label" x="180" y="33" text-anchor="middle">model</text>
  <path class="d-edge" d="M210 29 H230"/><polygon class="d-arrow" points="234,29 226,25 226,33"/>
  <text class="d-label-sm" x="240" y="14">a score for every token</text>
  <rect class="d-node-fill" x="240" y="20" width="10" height="24"/>
  <rect class="d-node-fill" x="254" y="28" width="10" height="16"/>
  <rect class="d-node-fill" x="268" y="33" width="10" height="11"/>
  <rect class="d-node-fill" x="282" y="37" width="10" height="7"/>
  <rect class="d-node-fill" x="296" y="40" width="10" height="4"/>
  <rect class="d-node-fill" x="310" y="41" width="10" height="3"/>
  <text class="d-label" x="332" y="44">…</text>
  <text class="d-label-sm" x="348" y="44">50k more</text>
  <path class="d-edge" d="M280 48 V84 H20 V50"/><polygon class="d-arrow" points="20,46 16,54 24,54"/>
  <text class="d-label-sm" x="150" y="79" text-anchor="middle">append one token, call it again</text>
</svg>
<figcaption>The whole interface. Everything else is a loop around this.</figcaption>
</figure>

## What the model returns

Those raw scores are logits. They're unbounded, they don't sum to anything in
particular, and on their own they aren't probabilities. Softmax turns them into
one:

```python
def softmax(logits, temperature=1.0):
    z = logits / temperature
    z = z - z.max()          # exp() overflows without this
    e = np.exp(z)
    return e / e.sum()
```

Say the prompt ends with `The deploy failed because the`, and five candidate
tokens come back with logits of 5.2, 4.6, 3.9, 3.1 and 2.4.<span class="sn"></span><span class="sidenote">Subtracting the maximum
before `exp` changes nothing mathematically, because the constant cancels in the
ratio. Leave it out and a logit of 800 gives you `inf/inf`, which is `nan`, and
your generation loop starts emitting whatever token sits at index zero.</span>
Through softmax at temperature 1.0 that becomes:

```text
database  49.9%
config    27.4%
build     13.6%
token      6.1%
disk       3.0%
```

The model didn't pick `database`. It said `database` is about as likely as
everything else combined, and something downstream still has to draw one token
from that.

## Temperature reshapes the distribution

Temperature is the division in the first line of that function, applied to the
logits before they're normalised. Calling it a creativity slider hides where it
acts. Dividing by a number below 1 spreads the logits further apart, so softmax
concentrates the mass. Dividing by a number above 1 pulls them together and
flattens it.

Same five logits, three temperatures:

<figure class="diagram">
<svg viewBox="0 0 400 148" role="img" aria-label="Three bar charts of the same five candidate tokens at temperature 0.2, 1.0 and 1.8. At 0.2 the first bar takes almost all the mass. At 1.0 it takes about half. At 1.8 the five bars are close to even.">
  <path class="d-edge" d="M0 110 H110"/>
  <rect class="d-node-fill" x="0" y="43" width="18" height="67"/>
  <rect class="d-node-fill" x="23" y="107" width="18" height="3"/>
  <rect class="d-node-fill" x="46" y="109" width="18" height="1"/>
  <rect class="d-node-fill" x="69" y="109" width="18" height="1"/>
  <rect class="d-node-fill" x="92" y="109" width="18" height="1"/>
  <text class="d-label" x="55" y="126" text-anchor="middle">T = 0.2</text>
  <text class="d-label-sm" x="55" y="140" text-anchor="middle">95.1% on one token</text>
  <path class="d-edge" d="M145 110 H255"/>
  <rect class="d-node-fill" x="145" y="75" width="18" height="35"/>
  <rect class="d-node-fill" x="168" y="91" width="18" height="19"/>
  <rect class="d-node-fill" x="191" y="100" width="18" height="10"/>
  <rect class="d-node-fill" x="214" y="106" width="18" height="4"/>
  <rect class="d-node-fill" x="237" y="108" width="18" height="2"/>
  <text class="d-label" x="200" y="126" text-anchor="middle">T = 1.0</text>
  <text class="d-label-sm" x="200" y="140" text-anchor="middle">49.9%</text>
  <path class="d-edge" d="M290 110 H400"/>
  <rect class="d-node-fill" x="290" y="84" width="18" height="26"/>
  <rect class="d-node-fill" x="313" y="92" width="18" height="18"/>
  <rect class="d-node-fill" x="336" y="98" width="18" height="12"/>
  <rect class="d-node-fill" x="359" y="102" width="18" height="8"/>
  <rect class="d-node-fill" x="382" y="105" width="18" height="5"/>
  <text class="d-label" x="345" y="126" text-anchor="middle">T = 1.8</text>
  <text class="d-label-sm" x="345" y="140" text-anchor="middle">36.7%</text>
</svg>
<figcaption>Bars are database, config, build, token and disk, left to right. The
model's opinion never changed. Only the shape you sample from did.</figcaption>
</figure>

At 0.2, `database` holds 95.1% and `config` gets 4.7%; the other three are
rounding error. At 1.8, `database` is down to 36.7% and `disk`, which the model
ranked last, comes up 7.7% of the time. That's roughly one run in thirteen
blaming the disk.

So temperature is a decision about how often you want the model's fifth choice.
For extraction, classification and anything you're going to parse, that answer
is never. For a first draft it's sometimes. There's no setting at which the
model tries harder.

## The loop only ever appends

Sampling one token is the whole forward step. To get a sentence, you append and
call again:

```python
tokens = tokenize(prompt)
for _ in range(max_new_tokens):
    probs = softmax(model(tokens), temperature)
    nxt = sample(probs)
    if nxt == EOS:
        break
    tokens.append(nxt)   # the only state that survives the call
```

That list is the entire memory of the process. There's no draft buffer, no
outline it's working from, and no step where it reads back what it wrote and
fixes the opening. Improv has the same constraint: once a line is out, the only
legal move is to build on it. A model that has committed to "There are three
reasons" will invent a third reason, because the alternative would be revising
a token it already emitted, and nothing in the loop can do that.

<figure class="diagram">
<svg viewBox="0 0 400 92" role="img" aria-label="A cycle: tokens so far feeds the model, which produces a distribution, which is sampled, and the sampled token is appended back to tokens so far.">
  <rect class="d-node-fill" x="0" y="16" width="88" height="30" rx="3"/>
  <text class="d-label" x="44" y="35" text-anchor="middle">tokens so far</text>
  <path class="d-edge" d="M88 31 H104"/><polygon class="d-arrow" points="108,31 100,27 100,35"/>
  <rect class="d-node-fill" x="108" y="16" width="62" height="30" rx="3"/>
  <text class="d-label" x="139" y="35" text-anchor="middle">model</text>
  <path class="d-edge" d="M170 31 H186"/><polygon class="d-arrow" points="190,31 182,27 182,35"/>
  <rect class="d-node-fill" x="190" y="16" width="90" height="30" rx="3"/>
  <text class="d-label" x="235" y="35" text-anchor="middle">distribution</text>
  <path class="d-edge" d="M280 31 H296"/><polygon class="d-arrow" points="300,31 292,27 292,35"/>
  <rect class="d-node-fill" x="300" y="16" width="62" height="30" rx="3"/>
  <text class="d-label" x="331" y="35" text-anchor="middle">sample</text>
  <path class="d-edge" d="M331 46 V68 H44 V50"/><polygon class="d-arrow" points="44,46 40,54 48,54"/>
  <text class="d-label-sm" x="188" y="80" text-anchor="middle">append one token</text>
</svg>
<figcaption>One direction only. The loop has no edge that removes a token.</figcaption>
</figure>

This is also why asking for the reasoning first does something real. The
intermediate tokens go into `tokens`, so every later call is conditioned on
them. The mechanism is conditioning rather than encouragement, and a different
input produces a different distribution.

## It has no index of what it knows

There's no lookup table in there and no confidence field to consult. When a
model states a function signature that doesn't exist, nothing failed. It
returned the highest-probability continuation given everything before it, and a
plausible-looking signature is exactly that.

A forecast that says 70% chance of rain isn't lying on the day it stays dry. The
model is that forecast, for tokens, and it has no way to mark which of its
outputs happened to land on something true. Facts and fluent nonsense come out
of the same distribution, at the same temperature, with the same confident tone.

Which is why grounding works and asking for honesty doesn't. Retrieval changes
the input, so it changes the distribution. "Only answer if you're sure" is a
string of tokens that tilts the distribution slightly toward hedging language,
without connecting the model to a truth oracle it never had.

## Tokens are not words

The vocabulary is subword fragments, and this leaks in ways that look like
stupidity. Counting the letters in a word means reasoning about characters the
model saw as two or three opaque chunks. Reversing a string, spotting a
palindrome, doing arithmetic on long numbers: all of it asks about the inside of
tokens.

If you need those, do them in code and let the model call the code. No prompt
recovers it, because the information was gone before the first layer.

## Temperature zero is not determinism

Temperature 0 makes sampling deterministic given identical logits. It doesn't
guarantee identical logits.

Floating-point addition isn't associative, and the order of reductions on a GPU
depends on batch shape, kernel choice and hardware. Two identical requests that
land in differently-sized batches can produce logits that differ in the last
bits, and if the top two candidates are close, that's enough to flip the token.
Everything after that token is conditioned on the flip.

So treat temperature 0 as "as repeatable as I can get", not as a guarantee. If
you need exact reproducibility, cache the output. Don't rely on regenerating it.

## Constrain the output space, don't ask nicely

The useful consequence of all this is that the distribution is something you can
edit before you sample from it.

Constrained decoding works directly on the logits. At each step you compute
which tokens could legally come next under your grammar or JSON schema, and set
everything else to negative infinity before softmax:

```python
mask = grammar.allowed_tokens(state)   # bool array over the vocabulary
logits[~mask] = -np.inf                # softmax sends these to exactly zero
```

`exp(-inf)` is 0, so those tokens can't be sampled at any temperature. Nothing
is asking the model to remember the format, because a token that would break it
can no longer be chosen.

Most good decisions here have that shape. Put the output in a schema rather than
a plea, use retrieval when you need facts, keep temperature low for anything you
parse, and hand arithmetic to a tool. All of it follows from the same fact: one
function returning one distribution, called in a loop that only moves forward.
