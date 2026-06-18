#!/usr/bin/env python3
"""Build matches.json (per-match parts w/ thumbnails) + print like/view distribution."""
import json, re, statistics, datetime

MATCHES = {
    "Ninjaa v Auro": [2],
    "IceMatrix v Cliff": [3, 4],
    "Moroten v Droner": [5],
    "FonderCargo v Aran": [6, 7],
    "Klass v Kiriyama": [8],
    "Alcaras v Rincewind": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "Mojo v Fiddler": [20, 21, 22],
    "Nizar v Jams": [23, 27, 28, 29, 30, 31],
    "Yagman v Marauder": [24, 25],
    "ThePurpleBullMoose v MongrelEyes": [26],
    "IceMatrix v Kiriyama781": [32, 33, 34],
    "Klass v Cliff": [35],
    "Anarkos v Becked": [36, 37],
    "Sabertooth v Blaj": [38, 39],
    "Ninja v Fiddler": [40, 41],
    "ThePurpleBullMoose v Moroten": [42, 43],
    "MongrelEyes v Droner": [44],
    "Mojo v Auro": [45, 46, 47, 48, 49, 50],
    "Fluffybunny v Becked": [51, 52],
    "Amadeus v Rincewind": [53],
    "Marauder v Jams": [54, 55],
    "Alcaras v MichaelofMinsk": [56, 57],
    "Nizar v Yagman": [58, 59, 60, 61, 62, 63],
    "Seasand v Cycle4x": [64, 65, 66],
    "Aran v Sabertooth": [67, 68, 69],
    "FonderCargo v Blaj": [70, 71],
    "Cliff v Groudon": [72],
    "Sabertooth v MongrelEyes": [73, 74, 75],
    "Siontific v Seasand": [76],
    "Auro v FluffyBunny (Winner's Bracket QF)": [77],
    "Aran v Siontific": [78, 79, 80, 81],
    "ThePurpleBullMoose v Klass_Koala": [82],
    "Moroten v Blaj": [83, 84, 85, 86],
    "Hazard v Anarkos": [87, 88, 89, 90, 91],
    "Alcaras v Nizar": [92, 93, 94, 95, 96, 97],
    "Cliff v Blaj": [98, 99, 100],
}

# Featured matches: order + draft blurb (user edits). Key = match label.
FEATURED = {
    "Auro v FluffyBunny (Winner's Bracket QF)": "The headline match of the whole tournament — a Winner's Bracket Quarterfinal that pulled 8,000+ views, more than 5x any other game.",
    "Alcaras v Nizar": "A six-part marathon between two of the tournament's sharpest players, with both a full cast and a PoV series.",
    "Nizar v Yagman": "Six tense parts that kept viewers coming back — one of the most-watched series of the bracket.",
    "Aran v Siontific": "A three-part heavyweight clash plus a postmatch interview — high views across the board.",
    "ThePurpleBullMoose v MongrelEyes": "A single explosive game that punched well above its weight in likes and views.",
    "Mojo v Auro": "An eight-game epic (six parts on the channel) — the longest series of the tournament.",
    "Cliff v Blaj": "The late-tournament showdown, aired right up to mid-November.",
    "ThePurpleBullMoose v Moroten": "Two parts, sky-high engagement — viewers loved this one.",
    "Ninjaa v Auro": "The very first match aired — and still one of the most-watched single games.",
}

def label_for(title, idx):
    t = title.lower()
    pov = "pov" in t
    cast = "cast" in t
    interview = "interview" in t
    mturn = re.search(r"turn\s*(\d+)", t)
    mpart = re.search(r"part\s*(\d+)", t) or re.search(r"pt\.?\s*(\d+)", t)
    if interview:
        return "Interview"
    kind = "PoV" if pov else ("Cast" if cast else "")
    if mturn:
        base = f"Turn {mturn.group(1)}"
    elif mpart:
        base = f"Part {mpart.group(1)}"
    else:
        base = "Part 1"
    return f"{kind} · {base}" if kind else base

rows = {}
with open("playlist_data.tsv") as f:
    for line in f:
        p = line.rstrip("\n").split("\\t")
        if len(p) < 7:
            continue
        idx = int(p[0])
        rows[idx] = {
            "id": p[1],
            "views": int(p[2]) if p[2] not in ("NA", "") else None,
            "likes": int(p[3]) if p[3] not in ("NA", "") else None,
            "date": p[4],
            "dur": int(p[5]) if p[5] not in ("NA", "") else 0,
            "title": p[6],
        }

matches = []
all_video_views, all_video_likes = [], []
for label, idxs in MATCHES.items():
    parts = []
    for i in idxs:
        r = rows[i]
        if r["views"] is not None:
            all_video_views.append(r["views"])
        if r["likes"] is not None:
            all_video_likes.append(r["likes"])
        parts.append({
            "id": r["id"],
            "label": label_for(r["title"], i),
            "title": r["title"],
            "views": r["views"],
            "likes": r["likes"],
            "dur": r["dur"],
            "date": datetime.datetime.strptime(r["date"], "%Y%m%d").strftime("%Y-%m-%d"),
            "url": f"https://www.youtube.com/watch?v={r['id']}",
            "thumb": f"https://i.ytimg.com/vi/{r['id']}/mqdefault.jpg",
        })
    # game parts exclude interviews for the per-video averages
    game_parts = [p for p in parts if p["label"] != "Interview"]
    views = [p["views"] for p in game_parts if p["views"] is not None]
    likes = [p["likes"] for p in game_parts if p["likes"] is not None]
    n = len(game_parts)
    total_views = sum(views)
    total_likes = sum(likes)
    matches.append({
        "label": label,
        "players": re.sub(r"\s*\(.*\)", "", label),
        "n_parts": len(parts),
        "n_games": n,
        "total_views": total_views,
        "total_likes": total_likes,
        "avg_views": round(total_views / n, 1) if n else 0,
        "avg_likes": round(total_likes / len(likes), 1) if likes else 0,
        "lv_ratio": round(total_likes / total_views * 1000, 1) if total_views else 0,
        "first": min(p["date"] for p in parts),
        "hours": round(sum(p["dur"] for p in parts) / 3600, 1),
        "featured": label in FEATURED,
        "featured_rank": list(FEATURED).index(label) if label in FEATURED else 999,
        "blurb": FEATURED.get(label, ""),
        "parts": parts,
    })

matches.sort(key=lambda m: (m["featured_rank"], -m["total_views"]))
with open("matches.json", "w") as f:
    json.dump({"generated": "2026-06-18", "matches": matches}, f, indent=2)

# ---- distribution report ----
def pct(data, q):
    return statistics.quantiles(data, n=100)[q - 1]

def describe(name, data):
    data = sorted(data)
    print(f"\n{name} (n={len(data)})")
    print(f"  min {min(data):>6}  p25 {pct(data,25):>7.0f}  median {statistics.median(data):>7.0f} "
          f" mean {statistics.mean(data):>7.0f}  p75 {pct(data,75):>7.0f}  p90 {pct(data,90):>7.0f}  max {max(data):>6}")

print("=== PER-VIDEO distribution ===")
describe("views/video", all_video_views)
describe("likes/video", all_video_likes)
print("\n=== PER-MATCH distribution ===")
describe("total views/match", [m["total_views"] for m in matches])
describe("total likes/match", [m["total_likes"] for m in matches])
describe("avg views per video/match", [m["avg_views"] for m in matches])

# histogram of total views per match
buckets = [(0,200),(200,400),(400,700),(700,1200),(1200,2000),(2000,9000)]
print("\nTotal-views-per-match histogram:")
for lo, hi in buckets:
    c = sum(1 for m in matches if lo <= m["total_views"] < hi)
    print(f"  {lo:>5}-{hi:<5} | {'#'*c} {c}")
print(f"\n{len(matches)} matches written to matches.json")
