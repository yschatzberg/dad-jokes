"""Generate one tiny share page per joke, at j/<id>/index.html.

A static host can't vary a response by query string, and link crawlers don't
run JavaScript - so a shared /?j=27 link can only ever show the same generic
preview card. One real file per joke fixes that: each carries its own Open
Graph tags, so iMessage shows that joke's setup.

The punchline never appears in these files. The whole point is that the
recipient peels it themselves.

Re-run after changing the joke list:

    python3 tools/build_share_pages.py
"""
import html
import io
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "j")

SITE = "https://dadjokes.wtf"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<link rel="canonical" href="{site}/j/{id}/">

<!-- The setup, and only the setup. A crawler reading a punchline here would
     spoil the joke before the link is ever opened. -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="dadjokes.wtf">
<meta property="og:url" content="{site}/j/{id}/">
<meta property="og:title" content="{setup}">
<meta property="og:description" content="Tap the note to peel the punchline.">
<meta property="og:image" content="{site}/icons/icon-512.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{setup}">
<meta name="twitter:description" content="Tap the note to peel the punchline.">
<meta name="twitter:image" content="{site}/icons/icon-512.png">
<meta name="theme-color" content="#17140F">

<style>
  html, body {{
    margin: 0;
    height: 100%;
    background: #17140F;
    color: #948871;
    font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
    display: grid;
    place-items: center;
    text-align: center;
    padding: 24px;
    box-sizing: border-box;
  }}
  a {{ color: #E9E0CB; }}
  p {{ margin: 0; font-size: 13px; letter-spacing: 0.08em; }}
</style>
</head>
<body>
<!-- Humans get bounced to the app immediately; crawlers stop at the tags
     above, because they don't run scripts. -->
<script>window.location.replace("../../?j={id}");</script>
<noscript><p><a href="../../?j={id}">Open the joke</a></p></noscript>
<p>Opening the joke&hellip;</p>
</body>
</html>
"""


def load_jokes():
    src = io.open(APP, encoding="utf-8").read()
    start = src.index("const JOKES = [")
    block = src[start:src.index("];", start)]
    rows = re.findall(
        r'\{\s*id:\s*(\d+),\s*s:\s*"((?:[^"\\]|\\.)*)",\s*p:\s*"((?:[^"\\]|\\.)*)"\s*\}',
        block)
    return [
        {"id": int(i), "s": s.replace('\\"', '"'), "p": p.replace('\\"', '"')}
        for i, s, p in rows
    ]


def main():
    jokes = load_jokes()
    if not jokes:
        raise SystemExit("no jokes parsed - did the JOKES format change?")

    # rebuild from scratch so deleted jokes don't leave orphan pages behind
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    for j in jokes:
        setup = html.escape(j["s"], quote=True)
        page = TEMPLATE.format(id=j["id"], setup=setup, title=setup, site=SITE)

        # belt and braces: never ship a punchline in a preview page
        if j["p"] and j["p"] in page:
            raise SystemExit(f"punchline leaked into page for id {j['id']}")

        d = os.path.join(OUT, str(j["id"]))
        os.makedirs(d)
        io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)

    print(f"wrote {len(jokes)} share pages to j/")
    print(f"ids {jokes[0]['id']}-{jokes[-1]['id']}")


if __name__ == "__main__":
    main()
