"""Curate jokes from official_joke_api (MIT) for merging into dadjokes.wtf.

Filters for: dad-joke shape, family-friendly content, and short enough to fit
the square note without tripping the .xlong size step.
"""
import json
import re
import unicodedata

SRC = "oja.json"

# Length caps. The existing 50 all sit under these and are verified to fit.
MAX_TOTAL = 145
MAX_SETUP = 115
MAX_PUNCH = 85

# Content this app shouldn't serve at a family dinner table.
BLOCK = re.compile(r"""
    sex|sexy|sexual|condom|boob|breast|nipple|penis|vagina|butt\b|arse|
    bastard|bitch|crap|piss|damn|shit|fuck|
    drunk|beer|vodka|whiskey|tequila|booze|drug|weed|cocaine|
    prostitut|strip\s?club|naked|nude|porn|viagra|erect|orgasm|
    abortion|suicide|rape|murder|nazi|racist|slave|
    fat\s|ugly|stupid|idiot|divorce|affair|cheat|
    gun|shoot|bomb|terror
""", re.I | re.X)

# Jokes that need a back-and-forth don't work on a static note.
NEEDS_DIALOGUE = re.compile(r"knock,?\s*knock|who'?s there", re.I)


def norm_text(t):
    t = unicodedata.normalize("NFKC", t or "")
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("—", " - ").replace("–", "-")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def key(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def main():
    data = json.load(open(SRC))

    existing = json.load(open("existing.json"))
    seen = set()
    for j in existing:
        seen.add(key(j["s"]))
        seen.add(key(j["p"]))

    kept, rejected = [], {"type": 0, "length": 0, "content": 0, "dupe": 0, "dialogue": 0}

    for j in data:
        if j.get("type") not in ("general", "dad"):
            rejected["type"] += 1
            continue

        s = norm_text(j.get("setup"))
        p = norm_text(j.get("punchline"))
        if not s or not p:
            rejected["length"] += 1
            continue

        if NEEDS_DIALOGUE.search(s + " " + p):
            rejected["dialogue"] += 1
            continue

        if len(s) + len(p) > MAX_TOTAL or len(s) > MAX_SETUP or len(p) > MAX_PUNCH:
            rejected["length"] += 1
            continue

        if BLOCK.search(s + " " + p):
            rejected["content"] += 1
            continue

        ks, kp = key(s), key(p)
        if ks in seen or kp in seen:
            rejected["dupe"] += 1
            continue
        seen.add(ks)
        seen.add(kp)

        kept.append({"s": s, "p": p})

    kept.sort(key=lambda j: len(j["s"]) + len(j["p"]))
    json.dump(kept, open("curated.json", "w"), indent=1)

    print("kept:", len(kept), "| rejected:", rejected)
    print()
    for i, j in enumerate(kept):
        print(f"{i:3d}. {j['s']}  ||  {j['p']}")


if __name__ == "__main__":
    main()
