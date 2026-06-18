#!/usr/bin/env python3
"""Group Old World 2025 tournament playlist videos into matches and rank them."""
import csv, datetime

# index -> (canonical match label). Built by reading all 100 titles.
# Excluded from matches: 1 = trailer, 81 = postmatch interview (not a game).
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
    "Aran v Siontific": [78, 79, 80],
    "ThePurpleBullMoose v Klass_Koala": [82],
    "Moroten v Blaj": [83, 84, 85, 86],
    "Hazard v Anarkos": [87, 88, 89, 90, 91],
    "Alcaras v Nizar": [92, 93, 94, 95, 96, 97],
    "Cliff v Blaj": [98, 99, 100],
}

# Load data
rows = {}
with open("playlist_data.tsv") as f:
    for line in f:
        parts = line.rstrip("\n").split("\\t")
        if len(parts) < 7:
            continue
        idx = int(parts[0])
        views = int(parts[2]) if parts[2] not in ("NA", "") else None
        likes = int(parts[3]) if parts[3] not in ("NA", "") else None
        date = parts[4]
        dur = int(parts[5]) if parts[5] not in ("NA", "") else 0
        title = parts[6]
        rows[idx] = {"views": views, "likes": likes, "date": date, "dur": dur, "title": title}

results = []
for label, idxs in MATCHES.items():
    vids = [rows[i] for i in idxs]
    n = len(vids)
    views = [v["views"] for v in vids if v["views"] is not None]
    likes = [v["likes"] for v in vids if v["likes"] is not None]
    n_hidden = sum(1 for v in vids if v["likes"] is None)
    total_views = sum(views)
    total_likes = sum(likes)
    avg_views = total_views / n  # all videos have views
    avg_likes = total_likes / len(likes) if likes else 0  # over videos with visible likes
    # earliest upload of the match
    dates = sorted(v["date"] for v in vids)
    first = datetime.datetime.strptime(dates[0], "%Y%m%d").strftime("%Y-%m-%d")
    total_dur_h = sum(v["dur"] for v in vids) / 3600
    results.append({
        "label": label, "n": n, "total_views": total_views, "avg_views": avg_views,
        "total_likes": total_likes, "avg_likes": avg_likes, "n_hidden": n_hidden,
        "first": first, "hours": total_dur_h,
        "lv_ratio": (total_likes / total_views * 1000) if total_views else 0,
    })

def fmt(n): return f"{n:,}"

def table(sorted_res, metric_name):
    lines = [f"| # | Match | Vids | Avg likes/vid | Avg views/vid | Total likes | Total views | Likes/1k views | First aired |",
             "|---|-------|------|---------------|---------------|-------------|-------------|----------------|-------------|"]
    for r, item in enumerate(sorted_res, 1):
        flag = f" ⚠️{item['n_hidden']}h" if item["n_hidden"] else ""
        lines.append(f"| {r} | {item['label']}{flag} | {item['n']} | {item['avg_likes']:.1f} | "
                     f"{item['avg_views']:.0f} | {fmt(item['total_likes'])} | {fmt(item['total_views'])} | "
                     f"{item['lv_ratio']:.1f} | {item['first']} |")
    return "\n".join(lines)

by_likes = sorted(results, key=lambda r: r["avg_likes"], reverse=True)
by_views = sorted(results, key=lambda r: r["avg_views"], reverse=True)

out = []
out.append("# Old World 2025 Community / Duelist Tournament — Best Games Reference\n")
out.append(f"_Generated {datetime.date(2026,6,18)} from the YouTube playlist (100 videos → "
           f"{len(results)} matches). Trailer and one postmatch interview excluded._\n")
out.append("**How to read this:** A \"match\" bundles every video covering the same matchup "
           "(main cast + PoV + multi-part splits). **Avg likes/vid** averages over videos with "
           "visible like counts; **avg views/vid** averages over all the match's videos — both "
           "normalize for matches that were split into many parts. ⚠️Nh = N videos had likes hidden.\n")
out.append("## 🏆 Ranked by AVERAGE LIKES per video\n")
out.append(table(by_likes, "avg_likes"))
out.append("\n## 👁 Ranked by AVERAGE VIEWS per video\n")
out.append(table(by_views, "avg_views"))
out.append("\n## Notes & caveats\n")
out.append("- **Standout single video:** *Auro vs FluffyBunny — Winner's Bracket Quarterfinal* "
           "(8,085 views, 193 likes in one upload) is by far the most-watched of the whole tournament.\n")
out.append("- **Nizar v Jams** bundles 6 videos with inconsistent round labels (some say Round 1, "
           "one says Round 2). Treated as one matchup; if they actually met twice the split is unclear from titles.\n")
out.append("- **Siontific v Seasand** (#76, titled \"@Siontific and Seasand\") may be a co-stream/"
           "discussion rather than a head-to-head game — verify before citing.\n")
out.append("- Like counts hidden on 5 videos (parts of Alcaras v Rincewind, Mojo v Fiddler, Nizar v Jams); "
           "their views still count.\n")
out.append("- All videos uploaded Sep–Nov 2025, so as of mid-2025 they've had comparable time to "
           "accumulate views/likes — rankings aren't badly skewed by upload recency.\n")

report = "\n".join(out)
with open("best_games.md", "w") as f:
    f.write(report)
print(report)
print(f"\n\n--- {len(results)} matches, {sum(r['n'] for r in results)} match-videos (+2 excluded) ---")
