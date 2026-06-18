import json, glob, re
from collections import defaultdict

GAMES = '/Users/dominik/Library/CloudStorage/Dropbox/cc/owglick/data/raw/games/*.json'

def norm(s):
    s = s.split('_')[0]
    s = re.sub(r'^Lord', '', s)
    s = re.sub(r'(Mohawk|Gaming|PL|TheWizard|BringsAxe)$', '', s)
    s = re.sub(r'\d+$', '', s)
    return re.sub(r'[^a-z]', '', s.lower())
ROSTER = {'alcaras','amadeus','anarkos','aran','auro','becked','blajj','cliff','droner','fiddlers',
    'fluffybunny','fondercargo','groudon','hazard','icematrix','jams','kiriyama','klass','sabertooth',
    'marauder','michaelofminsk','mojo','mongreleyes','moroten','ninjaa','nizar','rincewind','seasand',
    'siontific','thepurplebullmoose'}
def canon(n):
    if n in ROSTER: return n
    for c in ROSTER:
        if len(n)>=4 and len(c)>=4 and (n.startswith(c) or c.startswith(n)): return c
    for c in ROSTER:
        if (len(n)>=5 and n in c) or (len(c)>=5 and c in n): return c
    return n

games = []
for f in glob.glob(GAMES):
    try: d = json.load(open(f))
    except: continue
    mm = d.get('match_metadata', {})
    date = mm.get('save_date', '')
    pr = d.get('player_roster', [])
    humans = [p for p in pr if p.get('is_human')]
    if len(humans) != 2: continue
    win = mm.get('winner') or {}
    widx = win.get('winner_player_xml_id')
    games.append(dict(date=date, players=[(p.get('player_name'), p.get('nation'), p.get('player_index')) for p in humans], widx=widx))

# tournament window
window = [g for g in games if g['date'] and '2025-09' <= g['date'][:7] <= '2025-12']
print(f"total blobs: {len(games)} | 2-human | in Sep-Dec 2025 window: {len(window)}")

bypair = defaultdict(list)
for g in window:
    cn = [canon(norm(n)) for n, nat, i in g['players']]
    key = frozenset(cn)
    bypair[key].append(g)

print(f"\ndistinct tournament-window matchups in blobs: {len(bypair)}")
inroster = sum(1 for k in bypair if all(x in ROSTER for x in k))
print(f"  matchups where BOTH players are roster names: {inroster}")
print("\n=== sample matchups with nations ===")
NAT = lambda s: (s or '').replace('NATION_', '').title()
for key, gs in sorted(bypair.items(), key=lambda kv: -len(kv[1]))[:25]:
    names = ' / '.join(sorted(key))
    pernation = []
    for g in gs:
        pr = ', '.join(f"{canon(norm(n))}={NAT(nat)}" for n, nat, i in g['players'])
        pernation.append(f"[{g['date']}: {pr}]")
    print(f"  {len(gs)}  {names:30} {' '.join(pernation[:4])}")
