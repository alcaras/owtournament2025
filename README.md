# Old World 2025 Tournament — Best Games

A static guide to the best games of the Old World 2025 Community / Duelist Tournament,
with direct links to every part of every match.

**Live:** https://alcaras.github.io/owtournament2025/

## Editing the recommended matches & blurbs

Open `index.html` and edit the `BLURBS` object near the bottom (clearly marked
`✏️ EDIT YOUR BLURBS HERE`). The keys are match labels; the order is the display
order. Add a match to feature it, delete one to un-feature it. Commit & push —
GitHub Pages redeploys automatically.

## Regenerating the data

```
yt-dlp --print "%(playlist_index)s\t%(id)s\t%(view_count)s\t%(like_count)s\t%(upload_date)s\t%(duration)s\t%(title)s" \
  "https://www.youtube.com/playlist?list=PLsRPrwJXwEjaUyfAN956kM8WBGWPsHBEp" > playlist_data.tsv
python3 generate_data.py            # -> matches.json (+ distribution stats)
python3 -c "open('index.html','w').write(open('index_template.html').read().replace('__DATA__', open('matches.json').read()))"
```

- `generate_data.py` — groups the 100 videos into 36 matches (mapping is hand-curated in the `MATCHES` dict) and writes `matches.json`.
- `index_template.html` — the page (`__DATA__` placeholder gets the JSON inlined).
- `best_games.md` — plain-text ranked tables.
