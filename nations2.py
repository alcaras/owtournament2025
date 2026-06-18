import json, glob, re
from collections import defaultdict, Counter
from datetime import date, timedelta

PROJ = '/Users/dominik/Library/CloudStorage/Dropbox/cc/owtournament2025videos'
def norm(s):
    s=s.split('_')[0]; s=re.sub(r'^Lord','',s)
    s=re.sub(r'(Mohawk|Gaming|PL|TheWizard|BringsAxe)$','',s); s=re.sub(r'\d+$','',s)
    return re.sub(r'[^a-z]','',s.lower())
ROSTER={'alcaras','amadeus','anarkos','aran','auro','becked','blajj','cliff','droner','fiddlers','fluffybunny','fondercargo','groudon','hazard','icematrix','jams','kiriyama','klass','sabertooth','marauder','michaelofminsk','mojo','mongreleyes','moroten','ninjaa','nizar','rincewind','seasand','siontific','thepurplebullmoose'}
SUBS={'yagman','cyclex'}
def canon(n):
    if n in ROSTER or n in SUBS: return n
    for c in ROSTER:
        if len(n)>=4 and len(c)>=4 and (n.startswith(c) or c.startswith(n)): return c
    for c in ROSTER:
        if (len(n)>=5 and n in c) or (len(c)>=5 and c in n): return c
    return n
def slug(nat): return (nat or '').replace('NATION_','').lower()

def pdate(s):
    try: return date.fromisoformat(s[:10])
    except: return None

# load blobs
blobs=[]
for f in glob.glob('/Users/dominik/Library/CloudStorage/Dropbox/cc/owglick/data/raw/games/*.json'):
    try: d=json.load(open(f))
    except: continue
    mm=d.get('match_metadata',{}); dt=pdate(mm.get('save_date',''))
    hum=[p for p in d.get('player_roster',[]) if p.get('is_human')]
    if len(hum)!=2 or not dt: continue
    pl={canon(norm(p['player_name'])): slug(p.get('nation')) for p in hum if p.get('nation')}
    if len(pl)!=2: continue   # need two distinct players (mirror nations are fine)
    blobs.append(dict(date=dt, pair=frozenset(pl), nat=pl, gn=(mm.get('game_name') or '')))

data=json.load(open(PROJ+'/matches.json'))
covered=0
for m in data['matches']:
    keyset=frozenset(canon(x) for x in m['key'].split('|'))
    vdates=sorted(p for s in (m.get('segments',[])+m.get('clips',[])) for p in [s['primary'].get('date')] if p)
    if not vdates:
        m['nations']=None; continue
    lo=pdate(vdates[0])-timedelta(days=75); hi=pdate(vdates[-1])+timedelta(days=21)
    cands=[b for b in blobs if b['pair']==keyset and lo<=b['date']<=hi]
    if not cands:
        m['nations']=None; continue
    # per player: nations used, by frequency then recency
    pernat=defaultdict(Counter)
    for b in cands:
        for pl,nat in b['nat'].items():
            pernat[pl][nat]+=1
    # align to m['players'] order
    aligned=[]
    for disp in m['players']:
        cp=canon(norm(disp))
        aligned.append([n for n,_ in pernat.get(cp,Counter()).most_common()])
    if any(aligned):
        m['nations']=aligned
        m['nation_games']=len(cands)
        covered+=1
    else:
        m['nations']=None

json.dump(data, open(PROJ+'/matches.json','w'), indent=1)
print(f"matchups with nation data: {covered}/{len(data['matches'])}")
print("\n=== sample (player nations per matchup) ===")
for m in data['matches']:
    if m.get('nations'):
        s=' vs '.join(f"{p}={'/'.join(n) or '?'}" for p,n in zip(m['players'], m['nations']))
        print(f"  {m['round'][:14]:14} {m['label']:30} ({m.get('nation_games')}g) {s}")
