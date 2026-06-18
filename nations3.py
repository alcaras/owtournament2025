"""Attach nations from Prospector (prosp_matches.json) to matches.json.
Authoritative source: prospector.fly.dev parses the actual tournament save files.
Run AFTER build_data2.py, BEFORE inlining into the template."""
import json, re
from collections import defaultdict

PROJ = '/Users/dominik/Library/CloudStorage/Dropbox/cc/owtournament2025videos'
prosp = json.load(open(f'{PROJ}/prosp_matches.json'))

ROSTER = {'alcaras','amadeus','anarkos','aran','auro','becked','blajj','cliff','droner','fiddlers',
    'fluffybunny','fondercargo','groudon','hazard','icematrix','jams','kiriyama','klass','sabertooth',
    'marauder','michaelofminsk','mojo','mongreleyes','moroten','ninjaa','nizar','rincewind','seasand',
    'siontific','thepurplebullmoose'}
SUBS = {'yagman','cyclex'}
ALIAS = {'pbm':'thepurplebullmoose','yagiz':'yagman','koala':'klass','koalas':'klass'}
def norm(s):
    s = s.split('_')[0]
    s = re.sub(r'^Lord', '', s)
    s = re.sub(r'(Mohawk|Gaming|PL|TheWizard|BringsAxe)$', '', s)
    s = re.sub(r'\d+$', '', s)
    return re.sub(r'[^a-z]', '', s.lower())
def canon(n):
    n = norm(n)
    if n in ALIAS: return ALIAS[n]
    if n in ROSTER or n in SUBS: return n
    for c in ROSTER:
        if len(n)>=4 and len(c)>=4 and (n.startswith(c) or c.startswith(n)): return c
    for c in ROSTER:
        if (len(n)>=5 and n in c) or (len(c)>=5 and c in n): return c
    return n

# group prospector games by canonical player-pair
bypair = defaultdict(list)
for g in prosp:
    a, b = canon(g['p1']), canon(g['p2'])
    bypair[frozenset([a, b])].append({a: g['n1'].lower().replace(' ', ''), b: g['n2'].lower().replace(' ', ''),
                                      'date': g['date'], 'winner': canon(g['winner'])})

data = json.load(open(f'{PROJ}/matches.json'))
covered = 0
for m in data['matches']:
    pair = frozenset(canon(x) for x in m['key'].split('|'))
    games = bypair.get(pair, [])
    if not games:
        m['nations'] = None
        continue
    # per player (aligned to m['players']) collect nations across the matched games, ordered by date
    perplayer = []
    for disp in m['players']:
        cp = canon(disp)
        seen, nats = set(), []
        for g in sorted(games, key=lambda x: x['date']):
            nat = g.get(cp)
            if nat and nat not in seen:
                seen.add(nat); nats.append(nat)
        perplayer.append(nats)
    if any(perplayer):
        m['nations'] = perplayer
        m['nation_games'] = len(games)
        covered += 1
    else:
        m['nations'] = None

json.dump(data, open(f'{PROJ}/matches.json', 'w'), indent=1)
print(f"matchups with nations (from Prospector): {covered}/{len(data['matches'])}")
for m in data['matches']:
    if m.get('nations'):
        s = ' vs '.join(f"{p}={'/'.join(n) or '?'}" for p, n in zip(m['players'], m['nations']))
        print(f"  {m['round'][:14]:14} {m['label']:30} {s}")
