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
         'LB Round 5','LB Round 4','WB Round 2','LB Round 3','LB Round 2','WB Round 1','LB Round 1','Substitute']
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

POV_CHAN = {'alcaras':'alcaras','fluffybunny':'FluffyBunny','fluffbunny':'FluffyBunny',
            'nizar':'Nizar','aran':'Aran','jams':'Jams','siontific':'Siontific','syno':'Syno'}
def angle_of(title, channel):
    t = title.lower()
    if any(w in t for w in ('interview','discussion','post-game','postmatch','post game','postgame','wrap-up','wrap up')):
        return ('Interview', 9)
    if 'pov' in t:
        ch = (channel or '').lower()
        who = next((v for k, v in POV_CHAN.items() if k in ch), '')
        return (f'PoV — {who}' if who else 'PoV', 2)
    if 'cast' in t:
        return ('Cast', 1)
    return ('Broadcast', 0)

def partkey(title):
    t = title.lower()
    m = re.search(r'turn\s*(\d+)', t)
    if m: return ('t', int(m.group(1)))
    m = re.search(r'part\s*(\d+)', t) or re.search(r'\bpt\.?\s*(\d+)', t) or re.search(r'\bg(\d+)\b', t)
    if m: return ('p', int(m.group(1)))
    return ('p', 1)

def fdate(d):
    return f'{d[:4]}-{d[4:6]}-{d[6:8]}' if d and len(d) == 8 else d

# substitute players who really played but aren't in the Challonge roster
SUBS = {'yagman', 'cyclex', 'plantvogue', 'antvogue'}

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
        round_name = 'Substitute'; winner = None; rounds = []; bids = []
    is_sub = (a in SUBS) or (b in SUBS)

    vrec = []
    for vid, title in vids:
        s = stats.get(vid, {})
        date = fdate(s.get('date', ''))
        if date and date < '2025-08-01':       # drop pre-tournament (e.g. 2022 PlantVogue)
            continue
        ang, rank = angle_of(title, s.get('channel'))
        vrec.append(dict(id=vid, title=title, angle=ang, rank=rank, pkey=partkey(title),
                         views=s.get('views'), likes=s.get('likes'), dur=s.get('dur', 0),
                         date=date, channel=s.get('channel'),
                         url=f'https://www.youtube.com/watch?v={vid}',
                         thumb=f'https://i.ytimg.com/vi/{vid}/mqdefault.jpg'))
    if not vrec:
        continue

    # group videos into segments by part-key; Cast+PoV of same part = one segment (angles)
    segmap = {}
    for v in vrec:
        segmap.setdefault(v['pkey'], []).append(v)
    segments, clips = [], []
    for (kind, num), vs in sorted(segmap.items(), key=lambda kv: (kv[0][0] != 'p', kv[0][1])):
        vs.sort(key=lambda v: (v['rank'], v['date'] or ''))
        primary = vs[0]
        seg = dict(label=('Turn ' + str(num)) if kind == 't' else ('Part ' + str(num) if len(segmap) > 1 or kind == 't' else 'Full match'),
                   kind=kind, primary=primary,
                   angles=[dict(angle=v['angle'], url=v['url'], channel=v['channel'],
                                views=v['views'], dur=v['dur'], thumb=v['thumb'], id=v['id'], title=v['title']) for v in vs])
        (clips if kind == 't' else segments).append(seg)

    games_segs = [s for s in segments if s['primary']['angle'] != 'Interview']
    vv = [v['views'] for v in vrec if v['views'] is not None]
    ll = [v['likes'] for v in vrec if v['likes'] is not None]
    n_parts = len(games_segs) or 1
    tv, tl = sum(vv), sum(ll)
    matches.append(dict(
        players=[disp(a), disp(b)], label=f'{disp(a)} v {disp(b)}', key=key,
        round=round_name, round_depth=depth(round_name) if bms else 0, rounds=rounds, bracket_ids=bids,
        winner=winner, bracket=bool(bms), sub=is_sub,
        n_parts=len(games_segs), n_videos=len(vrec),
        total_views=tv, total_likes=tl, avg_views=round(tv/n_parts), avg_likes=round(tl/len(ll),1) if ll else 0,
        lv_ratio=round(tl/tv*1000, 1) if tv else 0,
        first=min((v['date'] for v in vrec if v['date']), default=''),
        hours=round(sum(v['dur'] for v in vrec)/3600, 1),
        segments=segments, clips=clips))

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
for m in matches:
    if m.get('sub'): print(f"  SUB {m['label']:26} {m['n_parts']}p/{m['n_videos']}v")
