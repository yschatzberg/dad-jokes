"""Curate + merge a hand-written batch of classic dad jokes into index.html.

Dedupes against the existing set on BOTH setup and punchline (so we never
repeat a gag or a punchline the app already uses), plus within the batch.
"""
import io
import json
import re

APP = "/Users/yoavschatzberg/Claude Code/jokebox/index.html"

MAX_TOTAL, MAX_SETUP, MAX_PUNCH = 145, 115, 85

BLOCK = re.compile(r"""
    sex|sexy|condom|boob|breast|nipple|penis|vagina|arse|bastard|bitch|
    piss|shit|fuck|drunk|vodka|whiskey|cocaine|prostitut|naked|nude|porn|
    viagra|abortion|suicide|rape|murder|nazi|racist|slave|terror|bomb
""", re.I | re.X)


# setups whose gag already exists in the app under different wording -
# exact-key dedupe can't catch these, so drop them explicitly
REMOVE_SETUPS = [
    "Why did the bicycle collapse?", "How does the ocean say hello?",
    "How do you fix a cracked pumpkin?", "What did the traffic light tell the car?",
    "Why did the tomato turn red?", "Why can't your nose be twelve inches long?",
    "What do you call a pony with a cough?", "How do trees get online?",
    "Why did the cookie go to the nurse?", "What did the plate whisper to the other plate?",
    "Why did the stadium get hot after the game?", "Why was six afraid of seven?",
    "Why don't eggs like telling secrets?", "What did one hat say to the other?",
    "Why did the frog take the bus?", "What did the ocean say to the shore?",
    "Why did the calendar feel nervous?", "Why can't a bike stand on its own?",
    "Why did the smartphone need glasses?", "What did the big flower say to the little one?",
    "Why don't skeletons ever go trick-or-treating?", "Why did the cyclist bring a ladder?",
    "Why did the mushroom get invited everywhere?", "What did papa tomato say to the slow baby tomato?",
    "Why did the painter go to jail?", "What's a vampire's favorite fruit?",
    "Why did the bee go to the salon?", "What do you call a pile of kittens?",
    "What did the mountain climber say to his son?", "What did the ocean do when it got tired?",
    "Why did the tofu blush?", "Why did the cabbage always win at poker?",
    "What did one wall say when it met the other?", "What do you call a dinosaur with a great vocabulary?",
    "Why did the farmer win an award?", "Why did the belt get arrested?",
]


def tidy(t):
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([,.!?])", r"\1", t)
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    if t and t[-1] not in ".!?":
        t += "."
    return t


def key(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def js(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


def main():
    existing = json.load(open("existing.json"))
    batch = json.load(open("batch.json"))

    seen = set()
    for j in existing:
        seen.add(key(j["s"]))
        seen.add(key(j["p"]))

    remove = {key(s) for s in REMOVE_SETUPS}

    next_id = max(j["id"] for j in existing) + 1
    kept, drop = [], {"dupe_setup": 0, "dupe_punch": 0, "length": 0,
                      "content": 0, "concept": 0}

    for pair in batch:
        s, p = tidy(pair[0]), tidy(pair[1])
        ks, kp = key(s), key(p)

        if ks in remove:
            drop["concept"] += 1; continue
        if ks in seen:
            drop["dupe_setup"] += 1; continue
        if kp in seen:
            drop["dupe_punch"] += 1; continue
        if len(s) + len(p) > MAX_TOTAL or len(s) > MAX_SETUP or len(p) > MAX_PUNCH:
            drop["length"] += 1; continue
        if BLOCK.search(s + " " + p):
            drop["content"] += 1; continue

        seen.add(ks); seen.add(kp)
        kept.append({"id": next_id, "s": s, "p": p})
        next_id += 1

    json.dump(kept, open("kept_batch.json", "w"), indent=1)
    print(f"batch {len(batch)} -> kept {len(kept)} | dropped {drop}")
    print(f"new total: {len(existing) + len(kept)}  (ids {kept[0]['id']}-{kept[-1]['id']})")
    print()
    for j in kept:
        print(f"{j['id']:3d}. {j['s']}  ||  {j['p']}")


if __name__ == "__main__":
    main()
