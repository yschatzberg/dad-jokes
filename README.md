# dadjokes.wtf

A stack of dad jokes on sticky notes, installable to a phone home screen.

**https://dadjokes.wtf** — see [Installing on a phone](#installing-on-a-phone).

Swipe right for the next joke, left to go back. On desktop the arrows either
side of the note do the same, as do the arrow keys. Right is always forward.

The punchline hides under a flap. Tap anywhere on the note to peel it open —
or drag upward if you want to lift it by hand. Space bar works too.

Everything ships in `index.html` — markup, styles, script, and the jokes
themselves. No build step, no dependencies, no network calls.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app |
| `manifest.webmanifest` | Makes it installable to a home screen |
| `sw.js` | Precaches the app so it works offline |
| `icons/` | Home-screen icons (generated, see below) |
| `THIRD-PARTY-LICENSES.md` | MIT notice for the bundled jokes |
| `tools/` | Icon generator and joke curation scripts |

## Running it locally

Needs to be served over HTTP rather than opened as a `file://` — service
workers won't register otherwise.

```sh
python3 -m http.server 8777
# then open http://localhost:8777
```

## Installing on a phone

**Live at: https://dadjokes.wtf**

### iPhone / iPad

1. Open that URL in **Safari**. Add to Home Screen doesn't exist in Chrome on
   iOS, so this step is Safari-only — the app itself runs fine in any browser.
2. Share (the square with the arrow) → scroll down → **Add to Home Screen**.
3. Launch from the icon.

### Android

1. Open the URL in **Chrome**.
2. Tap the **⋮** menu (top right).
3. Tap **Install app** — older versions say **Add to Home screen**, and some
   show an **Install** button in a banner at the bottom of the page instead.
4. Confirm **Install**.

Android goes a step further than iOS here: because the app has a valid manifest,
a service worker, and 192/512 icons, Chrome installs it as a WebAPK — a real
app entry. It shows up in the app drawer, gets its own window in Recents, and
appears under Settings → Apps like anything from the Play Store.

The 512 icon is also declared `maskable`, so Android crops it to whatever icon
shape your launcher uses (circle, squircle, rounded square) without slicing off
the note. The artwork is centred with room to spare for exactly this reason.

**Other Android browsers:** Samsung Internet works — menu → **Add page to** →
**Home screen**. Firefox for Android can add a shortcut but its standalone
support is weaker, so use Chrome or Samsung Internet if you want it to feel
like a real app.

### What you get

Full screen, no browser chrome, its own icon, and it keeps working with no
signal — the service worker precaches everything the first time you open it
online.

To confirm offline actually works: open it once with a connection, then turn on
Airplane Mode and relaunch from the icon. If it loads, you're set.

### If the icon looks wrong or the app won't update

First, check you bumped `CACHE` in `sw.js` — that's the usual cause, and no
amount of reinstalling fixes it.

**iOS:** caches aggressively. Delete the home-screen icon, open the URL in
Safari again, and re-add it.

**Android:** long-press the icon → **Uninstall** (it's a real app, so it
uninstalls like one), then reinstall from Chrome. Android refreshes the WebAPK
on its own schedule, so an icon change can take a day or two to appear
otherwise.

## Deploying

Already set up: GitHub Pages serves `main` from the repo root, so **pushing to
`main` deploys**. It takes a minute or two to go live.

**Bump `CACHE` in `sw.js` before every push** (`dadjokes-v6`, and so on).
The service worker serves cache-first, so without a bump your phone keeps
serving the old files and it looks like the deploy silently failed.

```sh
# edit sw.js: const CACHE = 'dadjokes-v6';
git commit -am "Whatever changed"
git push
```

## Adding jokes

They're an array of `{ id, s, p }` objects near the top of the script in
`index.html` — `s` is the setup, `p` is the punchline.

**`id` is permanent.** Share links point at it, so never renumber, and never
reuse the id of a joke you delete. New jokes take the next number up. Order in
the array doesn't matter; the deck is shuffled anyway.

Notes size their own text with container query units, and long jokes step down
a size via the `.long` / `.xlong` classes, which key off character count. That
threshold is a proxy for how the text actually wraps — if you add a much longer
joke than the current set, check it still fits inside the square, and that the
flap still covers the whole punchline.

### Where these came from

**ids 1–50** are classic dad jokes in wide circulation, written out for this
project rather than copied from any single source.

**ids 51–285** are curated from
[official_joke_api](https://github.com/15Dkatz/official_joke_api), which is MIT
licensed — see [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md), which
reproduces the copyright notice the licence requires.

Most joke APIs publish no content licence at all. `icanhazdadjoke` has more
jokes but states no terms of use and no content licence, which is fine for
personal use and murky for anything you ship.

Of 451 source jokes, 285 - 50 = 235 made it in. The rest were dropped as
programming/knock-knock jokes, too long for the note, near-duplicates, or not
family-friendly. `tools/curate_jokes.py` does the filtering and prints
candidates; `tools/merge_jokes.py` takes a hand-picked list of indices and
rewrites the `JOKES` block. Filtering alone isn't enough — the final pick was
made by reading all 333 survivors.

They're bundled into `index.html` rather than fetched at runtime, because a
network call would break offline support, which is most of the point of
installing this.

## Sharing

The **Share** button uses the Web Share API where it exists (iOS, Android), so
you get the native share sheet. Elsewhere it copies the joke and link to the
clipboard and shows a toast.

Shared links look like `https://dadjokes.wtf/?j=18`. Opening one puts that joke
first in the stack, still covered — the recipient gets to peel it themselves.
**Shuffle** clears the `?j=` from the URL so a refresh doesn't snap back to it.

## Icons

Generated by `tools/mkicons.py` (pure stdlib, no Pillow needed):

```sh
ICON_OUT=icons python3 tools/mkicons.py
```
