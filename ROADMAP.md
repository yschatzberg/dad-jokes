# Roadmap

Ideas not being built yet. Captured 2026-07-18.

The dividing line that matters: **the app is currently a static site with no
backend.** Two of these fit that; three don't, and doing any of those three
means picking a backend first. That decision is worth making deliberately,
because it's what turns this from a file on a CDN into a service with uptime,
costs, and data to look after.

## Fits the current architecture

### 1. Like / favourite a joke — DONE (2026-07-18)

Shipped. Save a joke with the footer heart, a double-tap on the note, or the
`s` key; it's stored in `localStorage` keyed by joke id, and the **Saved**
button opens a filtered view. On-device only, as planned — see the "Saved
jokes" section of the README. (An in-note star was the first attempt, but the
note captures the pointer, so clicks never reached it; the heart lives in the
footer, outside the note, for that reason.)

### 4. Guess the punchline

A mode where the punchline is masked and you guess it — hangman-style letter
reveals, or multiple choice against punchlines pulled from other jokes.

Pure client-side; the joke data already has everything it needs. Multiple
choice is much easier to build and to score than free-text guessing, which
needs fuzzy matching to avoid punishing near-misses.

Worth deciding: does this share the peel interaction, or is it a separate mode
with its own screen?

## Needs a backend

These three can't be done on GitHub Pages alone.

### 2. Submit a joke

Options, cheapest first:

- **A form service** (Formspree, Netlify Forms) — submissions land in email or
  a dashboard, no server to run. Free tiers are small but probably ample.
- **A GitHub issue** created via the API from a form — free, keeps submissions
  next to the code, and gives a natural review queue.
- **A real backend** — only worth it if 3 and 5 are also happening.

Whatever the route, submissions must not go straight into the app. See below.

### 3. Submission moderation

The reason 2 can't ship alone. An open submission box on a public joke site
attracts spam and worse, and this app is aimed at family use.

Minimum viable: submissions queue somewhere private, a human approves, approved
jokes get added to `index.html` on the next deploy. That's slow but has no
moving parts and no way for unreviewed content to reach a reader.

Anything faster than human review needs a moderation pass (a service, or an
LLM check) and a way to pull a joke back down quickly once it's live.

### 5. Joke of the week / month, community voted

Needs persistent storage for votes and a way to stop one person voting a
thousand times — which in practice means either accounts or accepting that the
count is approximate.

Depends on 2 and 3 being in place first: there's nothing to vote on without
submissions, and no safe way to surface submissions without moderation.

## Suggested order

1 and 4 first: they're self-contained, need no infrastructure, and make the app
better on their own. Then 2 and 3 together as a single piece of work, since
submissions without moderation shouldn't ship. Then 5 once there's a corpus
worth voting on.
