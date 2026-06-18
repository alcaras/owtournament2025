import json, re
from collections import defaultdict

PROJ = '/Users/dominik/Library/CloudStorage/Dropbox/cc/owtournament2025videos'
groups = json.load(open('/tmp/groups.json'))          # "a|b" -> [[id,title],...]
br = json.load(open('/tmp/bracket_matches.json'))

# ---------- name helpers (same as parse_group) ----------
def norm(s):
    s = s.split('_')[0]
    s = re.sub(r'^Lord', '', s)
    s = re.sub(r'(Mohawk|Gaming|PL|TheWizard|BringsAxe)$', '', s)
    s = re.sub(r'\d+$', '', s)
    return re.sub(r'[^a-z]', '', s.lower())
ROSTER = {'alcaras':'Alcaras','amadeus':'Amadeus','anarkos':'Anarkos','aran':'Aran','auro':'Auro',
    'becked':'Becked','blajj':'Blaj','cliff':'Cliff','droner':'Droner','fiddlers':'Fiddler',
    'fluffybunny':'FluffyBunny','fondercargo':'FonderCargo','groudon':'Groudon','hazard':'Hazard',
    'icematrix':'IceMatrix','jams':'Jams','kiriyama':'Kiriyama','klass':'Klass','sabertooth':'Sabertooth',
    'marauder':'Marauder','michaelofminsk':'MichaelofMinsk','mojo':'Mojo','mongreleyes':'MongrelEyes',
    'moroten':'Moroten','ninjaa':'Ninjaa','nizar':'Nizar','rincewind':'Rincewind','seasand':'Seasand',
    'siontific':'Siontific','thepurplebullmoose':'ThePurpleBullMoose'}
NONB = {'yagman':'Yagman','yagmam':'Yagman','cyclex':'Cycle4x','plantvogue':'PlantVogue','antvogue':'PlantVogue'}
def canon(n):
    if n in ROSTER: return n
    for c in ROSTER:
        if len(n)>=4 and len(c)>=4 and (n.startswith(c) or c.startswith(n)): return c
    for c in ROSTER:
        if (len(n)>=5 and n in c) or (len(c)>=5 and c in n): return c
    return n
def disp(n): return ROSTER.get(n) or NONB.get(n) or n.title()

RN = {1:'WB Round 1',2:'WB Round 2',3:'WB Quarterfinal',4:'WB Semifinal',5:'WB Final',6:'Grand Final',
      -1:'LB Round 1',-2:'LB Round 2',-3:'LB Round 3',-4:'LB Round 4',-5:'LB Round 5',-6:'LB Round 6',-7:'LB Round 7',-8:'LB Final'}
ORDER = ['Grand Final','WB Final','LB Final','WB Semifinal','LB Round 7','LB Round 6','WB Quarterfinal',
         'LB Round 5','LB Round 4','WB Round 2','LB Round 3','LB Round 2','WB Round 1','LB Round 1','Non-bracket']
def depth(rn): return len(ORDER) - ORDER.index(rn)

brpairs = defaultdict(list)
for m in br:
    brpairs[frozenset([canon(norm(m['p1'])), canon(norm(m['p2']))])].append(m)

# ---------- stats ----------
stats = {}
for line in open(f'{PROJ}/playlist_data.tsv'):
    p = line.rstrip('\n').split('\\t')
    if len(p) >= 7:
        stats[p[1]] = dict(views=int(p[2]) if p[2] not in('NA','') else None,
                           likes=int(p[3]) if p[3] not in('NA','') else None,
                           date=p[4], dur=int(p[5]) if p[5] not in('NA','') else 0, title=p[6], channel=None)
for line in open('/tmp/channels.tsv'):
    p = line.rstrip('\n').split('\\t')
    if len(p) >= 5 and p[0] in stats: stats[p[0]]['channel'] = p[1]
for line in open('/tmp/new_stats.tsv'):
    p = line.rstrip('\n').split('\\t')
    if len(p) >= 7:
        stats[p[0]] = dict(views=int(p[1]) if p[1] not in('NA','') else None,
                          likes=int(p[2]) if p[2] not in('NA','') else None,
                          date=p[3], dur=int(p[4]) if p[4] not in('NA','') else 0, channel=p[5], title=p[6])

def plabel(title):
    t = title.lower()
    if 'interview' in t or 'discussion' in t or 'post-game' in t or 'postmatch' in t or 'post game' in t:
        return 'Interview'
    kind = 'PoV' if 'pov' in t else ('Cast' if 'cast' in t else '')
    mt = re.search(r'turn\s*(\d+)', t)
    mp = re.search(r'part\s*(\d+)', t) or re.search(r'\bpt\.?\s*(\d+)', t) or re.search(r'\bg(\d+)\b', t)
    if mt: base = f'Turn {mt.group(1)}'
    elif mp: base = f'Part {mp.group(1)}'
    else: base = 'Full game'
    return f'{kind} · {base}' if kind else base

def fdate(d):
    return f'{d[:4]}-{d[4:6]}-{d[6:8]}' if d and len(d) == 8 else d

matches = []
for key, vids in groups.items():
    a, b = key.split('|')
    bms = brpairs.get(frozenset([a, b]), [])
    bms = sorted(bms, key=lambda m: depth(RN[m['round']]), reverse=True)
    if bms:
        primary = bms[0]
        round_name = RN[primary['round']]
        winner = disp(canon(norm(primary['winner']))) if primary['winner'] else None
        rounds = [RN[m['round']] for m in bms]
        bids = [m['identifier'] for m in bms]
    else:
        round_name = 'Non-bracket'; winner = None; rounds = []; bids = []
    parts = []
    for vid, title in vids:
        s = stats.get(vid, {})
        parts.append(dict(id=vid, label=plabel(title), title=title,
                          views=s.get('views'), likes=s.get('likes'), dur=s.get('dur', 0),
                          date=fdate(s.get('date', '')), channel=s.get('channel'),
                          url=f'https://www.youtube.com/watch?v={vid}',
                          thumb=f'https://i.ytimg.com/vi/{vid}/mqdefault.jpg'))
    games = [p for p in parts if p['label'] != 'Interview']
    vv = [p['views'] for p in games if p['views'] is not None]
    ll = [p['likes'] for p in games if p['likes'] is not None]
    parts.sort(key=lambda p: (p['date'] or '', p['label']))
    n = len(games) or 1
    tv, tl = sum(vv), sum(ll)
    matches.append(dict(
        players=[disp(a), disp(b)], label=f'{disp(a)} v {disp(b)}', key=key,
        round=round_name, round_depth=depth(round_name), rounds=rounds, bracket_ids=bids,
        winner=winner, bracket=bool(bms), n_videos=len(parts), n_games=len(games),
        total_views=tv, total_likes=tl, avg_views=round(tv/n), avg_likes=round(tl/len(ll),1) if ll else 0,
        lv_ratio=round(tl/tv*1000, 1) if tv else 0,
        first=min((p['date'] for p in parts if p['date']), default=''),
        hours=round(sum(p['dur'] for p in parts)/3600, 1), parts=parts))

# unfilmed bracket matches
unfilmed = []
for key, ms in brpairs.items():
    if key not in {frozenset(k.split('|')) for k in groups}:
        m = sorted(ms, key=lambda x: depth(RN[x['round']]), reverse=True)[0]
        unfilmed.append(dict(label=f"{disp(canon(norm(m['p1'])))} v {disp(canon(norm(m['p2'])))}",
                             round=RN[m['round']], round_depth=depth(RN[m['round']]),
                             winner=disp(canon(norm(m['winner']))) if m['winner'] else None))

champ = [m for m in br if m['round'] == 6][0]
champion = disp(canon(norm(champ['winner'])))
runner = disp(canon(norm(champ['p1'] if champ['winner'] != champ['p1'] else champ['p2'])))
# wait: winner_id resolves to winner name already; runner = the other
runner = disp(canon(norm(champ['p2'] if champ['winner'] == champ['p1'] else champ['p1'])))

matches.sort(key=lambda m: (-m['round_depth'], -m['total_views']))
out = dict(generated='2026-06-18', champion=champion, runner_up=runner,
           n_bracket_matches=len(br), n_matchups=len(matches),
           n_videos=sum(m['n_videos'] for m in matches),
           total_views=sum(m['total_views'] for m in matches),
           total_likes=sum(m['total_likes'] for m in matches),
           total_hours=round(sum(m['hours'] for m in matches), 1),
           order=ORDER, matches=matches, unfilmed=sorted(unfilmed, key=lambda x: -x['round_depth']))
json.dump(out, open(f'{PROJ}/matches.json', 'w'), indent=1)
print(f"champion: {champion}  runner-up: {runner}")
print(f"matchups: {len(matches)} | videos: {out['n_videos']} | views: {out['total_views']:,} | likes: {out['total_likes']:,} | hours: {out['total_hours']}")
print(f"unfilmed bracket matches: {len(unfilmed)}")
print("\ntop by round_depth:")
for m in matches[:14]:
    w = f" — {m['winner']} won" if m['winner'] else ""
    print(f"  {m['round']:16} {m['label']:34} {m['n_videos']}v {m['total_views']:>5}views{w}")
