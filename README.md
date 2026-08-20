# aavishkarmishra.com

Astro, markdown, no client JS. Deployed on Cloudflare Pages.

```
npm run dev      # localhost:4321
npm run build    # -> dist/
```

## Writing a post

Create `src/content/writing/<slug>.md`:

```md
---
title: Why 4K renders left Lambda for the browser
description: One sentence. Shows on the index and in the RSS feed.
date: 2026-08-24
featured: false   # true pins it to the homepage under "Selected work"
draft: true       # visible in dev, excluded from the build
---
```

`git push` deploys.

### Sidenotes

Markdown allows raw HTML. Numbering is automatic:

```html
...is not a quota you can raise.<span class="sn"></span><span
class="sidenote">A hard limit on the execution model, not a soft default.</span>
```

Wide screens put the note in the right margin; narrow screens inline it.

### Diagrams

Inline SVG in the post. Use the `d-*` classes so it recolors with the theme —
never hardcode a hex value, and never use a raster image for a diagram.

```html
<figure class="diagram">
<svg viewBox="0 0 400 200" role="img" aria-label="Describe the diagram here.">
  <rect class="d-node-fill" x="0" y="78" width="112" height="34" rx="3"/>
  <text class="d-label" x="14" y="99">render request</text>
  <path class="d-edge" d="M112 95 H 208"/>
  <polygon class="d-arrow" points="212,95 204,91 204,99"/>
</svg>
<figcaption>Caption.</figcaption>
</figure>
```

`d-edge-fail` / `d-arrow-fail` / `d-label-fail` mark rejected or failing paths.

## Adding a book

Append to the top of `books` in `src/data/reading.ts`. Title, author, and one
honest line. If there is nothing specific to say about it, leave it out.

## Editorial rules

- Never claim "senior". Specifics earn it; adjectives do not.
- No employer revenue or internal cost figures. Public list prices are fine.
- Every post comes from something actually built. Nothing reworded from
  someone else's blog.
- No Leetcode counts, no skill bars, no logo walls.
