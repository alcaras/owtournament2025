"""Fetch the full tournament match list (players + nations + date + winner) from
Prospector (prospector.fly.dev), a Dash app that parses the actual save files.
The Dash callback `match-selector.options` returns every match as a labelled
option like:
  "Aran (Egypt) vs Ninjaa (Assyria) (2026-03-07) - 70 turns - Winner: Ninjaa (Assyria)"
Writes prosp_matches.json. Re-run to refresh."""
import json, re, urllib.request

URL = 'https://prospector.fly.dev/_dash-update-component'
PAYLOAD = {
    "output": "match-selector.options",
    "outputs": {"id": "match-selector", "property": "options"},
    "inputs": [{"id": "_pages_location", "property": "pathname", "value": "/matches"}],
    "changedPropIds": [], "state": [],
}
req = urllib.request.Request(URL, data=json.dumps(PAYLOAD).encode(),
                            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
opts = json.load(urllib.request.urlopen(req))['response']['match-selector']['options']

pat = re.compile(r'^(.*?) \((\w[\w ]*?)\) vs (.*?) \((\w[\w ]*?)\) \((\d{4}-\d{2}-\d{2})\) - (\d+) turns - Winner: (.*?) \((\w[\w ]*?)\)')
rows = []
for o in opts:
    m = pat.match(o['label'])
    if not m:
        print('UNPARSED:', o['label']); continue
    p1, n1, p2, n2, date, turns, w, wn = m.groups()
    rows.append(dict(id=o['value'], p1=p1, n1=n1, p2=p2, n2=n2, date=date,
                     turns=int(turns), winner=w, wnat=wn))
json.dump(rows, open('prosp_matches.json', 'w'), indent=1)
print(f'wrote prosp_matches.json: {len(rows)} matches')
