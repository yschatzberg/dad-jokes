"""Merge the hand-picked jokes into index.html with fresh, permanent ids."""
import io
import json
import re

# Indices into curated.json, chosen by reading all 333 candidates.
# Dropped: weak/non-jokes, near-duplicates of the existing 50, internal
# duplicates, and anything with innuendo.
SELECTED = [
    2, 4, 5, 6, 8, 14, 15, 17, 19, 20, 22, 24, 25, 27, 29, 30, 31, 32, 33, 35,
    36, 37, 38, 41, 42, 43, 44, 45, 46, 47, 50, 51, 52, 53, 55, 56, 57, 59, 60,
    61, 62, 64, 66, 67, 68, 69, 70, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86,
    87, 90, 92, 93, 94, 95, 96, 97, 98, 100, 102, 103, 104, 105, 106, 107, 109,
    110, 111, 114, 115, 117, 119, 121, 122, 123, 125, 126, 127, 128, 129, 130,
    131, 132, 133, 135, 136, 137, 139, 140, 141, 143, 144, 145, 146, 147, 149,
    150, 151, 153, 154, 155, 156, 157, 158, 159, 161, 163, 165, 166, 167, 168,
    169, 170, 173, 175, 177, 178, 179, 181, 182, 183, 184, 185, 188, 189, 190,
    191, 192, 194, 196, 198, 200, 201, 203, 204, 207, 208, 209, 210, 211, 212,
    213, 214, 215, 217, 218, 219, 222, 223, 224, 225, 226, 227, 228, 229, 230,
    231, 232, 233, 235, 236, 237, 239, 241, 243, 245, 247, 248, 249, 250, 251,
    252, 253, 256, 257, 259, 260, 262, 263, 265, 266, 267, 268, 269, 270, 271,
    272, 273, 274, 275, 277, 278, 280, 282, 284, 285, 286, 287, 289, 290, 291,
    292, 293, 296, 298, 299, 300, 301, 303, 304, 305, 306, 310, 311, 313, 314,
    316, 318, 320, 321, 322, 324, 326, 327, 331, 332,
]

# Spelling and capitalisation the source got wrong.
FIXES = {
    "MOODOO": "Moo-doo",
    "mummys": "mummies",
    "Zen Buddist": "Zen Buddhist",
    "Cinderalla": "Cinderella",
    "peter pan": "Peter Pan",
    "Sign Language": "Sign language",
    "a labracadabrador": "A labracadabrador",
    "1023MB": "1023 MB",
}


def tidy(t):
    for bad, good in FIXES.items():
        t = t.replace(bad, good)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([,.!?])", r"\1", t)
    t = re.sub(r'"\s*(\w)', r'" \1', t)          # `"tuna"fish` -> `"tuna" fish`
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    if t and t[-1] not in ".!?":
        t += "."
    return t


def js_str(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


def main():
    curated = json.load(open("curated.json"))
    existing = json.load(open("existing.json"))
    next_id = max(j["id"] for j in existing) + 1

    added = []
    for i in SELECTED:
        j = curated[i]
        added.append({"id": next_id, "s": tidy(j["s"]), "p": tidy(j["p"])})
        next_id += 1

    # final safety net: no repeated setup or punchline anywhere in the app
    seen, clashes = {}, []
    for j in existing + added:
        for field in ("s", "p"):
            k = re.sub(r"[^a-z0-9]", "", j[field].lower())
            if k in seen:
                clashes.append((seen[k], j["id"], j[field][:45]))
            seen[k] = j["id"]
    if clashes:
        print("DUPLICATE TEXT:", clashes)

    lines = []
    for j in existing:
        lines.append(f'    {{ id: {j["id"]},  s: "{js_str(j["s"])}", p: "{js_str(j["p"])}" }},')
    for n, j in enumerate(added):
        comma = "," if n < len(added) - 1 else ""
        lines.append(f'    {{ id: {j["id"]}, s: "{js_str(j["s"])}", p: "{js_str(j["p"])}" }}{comma}')

    path = "/Users/yoavschatzberg/Claude Code/jokebox/index.html"
    src = io.open(path, encoding="utf-8").read()
    start = src.index("  const JOKES = [")
    end = src.index("  ];", start) + len("  ];")
    block = "  const JOKES = [\n" + "\n".join(lines) + "\n  ];"
    io.open(path, "w", encoding="utf-8").write(src[:start] + block + src[end:])

    print(f"existing {len(existing)} + added {len(added)} = {len(existing) + len(added)} jokes")
    print("id range added:", added[0]["id"], "-", added[-1]["id"])
    longest = max(existing + added, key=lambda j: len(j["s"]) + len(j["p"]))
    print("longest:", len(longest["s"]) + len(longest["p"]), "chars ->", longest["s"][:50])


if __name__ == "__main__":
    main()
