import json, re
from collections import defaultdict

PLAYLIST = '/Users/dominik/Library/CloudStorage/Dropbox/cc/owtournament2025videos/playlist_data.tsv'
br = json.load(open('/tmp/bracket_matches.json'))

pool = {}
for line in open(PLAYLIST):
    p = line.rstrip('\n').split('\\t')
    if len(p) >= 7:
        pool[p[1]] = p[6]
for line in open('/tmp/candidates_raw.txt'):
    if '|' in line:
        vid, title = line.rstrip('\n').split('|', 1)
        pool.setdefault(vid, title)
for line in open('/tmp/sweep_raw.txt'):
    parts = line.rstrip('\n').split('@@')
    if len(parts) == 3:
        pool.setdefault(parts[1], parts[2])

JUNK = re.compile(r'warhammer|blood bowl|offworld|aow3|age of wonders|fortnite|yu-?gi-?oh|tekken|mortal kombat|atlas|trailer', re.I)

def valid(t):
    tl = t.lower()
    if JUNK.search(t):
        return False
    # must mention old world AND tournament (drops cloud duels, playthroughs, guides, FFAs)
    return ('old world' in tl) and ('tournament' in tl)

BOILER = [
    r'old world\s*2025', r'old world', r'community', r'duelist',
    r'tournament', r'2025', r'\bnetwork\b', r'\bedition\b',
    r'semi-?finals?', r'\bfinals?\b', r'grand final',
    r'\bround\b\s*\d*', r'\d+\s*(st|nd|rd|th)\s*round', r'\bmy match\b',
    r'part\s*\d+(\s*of\s*\d+)?', r'pt\.?\s*\d+', r'\bgame\s*\d+', r'turn\s*\d+',
    r'\d+\s*of\s*\d+', r'post-?game.*', r'postmatch.*', r'post-?match.*',
    r'\bdiscussion\b', r'\binterview\b', r'\bcast\b', r'\bpov\b', r'\bfinale\b',
    r'coastal rain basin', r'\bduel\b', r'\bwide\b', r'\bcoastal\b',
]
BRE = re.compile('|'.join(BOILER), re.I)

def extract_pair(title):
    t = re.sub(r'\[[^\]]*\]', ' ', title)
    t = re.sub(r'\([^)]*\)', ' ', t)
    t = re.sub(r'[-–—:.,!?]+', ' ', t)
    t = BRE.sub(' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    m = re.search(r'(.+?)\s+(?:vs?|versus|and)\s+(.+)', t, flags=re.I)
    if not m:
        return None
    left = [w for w in m.group(1).split() if w]
    right = [w for w in m.group(2).split() if w]
    if not left or not right:
        return None
    a = re.sub(r'[^A-Za-z0-9_]', '', left[-1])
    b = re.sub(r'[^A-Za-z0-9_]', '', right[0])
    # Michael of Minsk
    if b.lower().startswith('michael') and len(right) >= 3 and right[1].lower() == 'of':
        b = 'MichaelofMinsk'
    if right[0].lower() == 'michael' and len(right) >= 3:
        b = 'MichaelofMinsk'
    return (a, b) if a and b else None

def norm(s):
    s = s.split('_')[0]                                  # Klass_Koalas -> Klass
    s = re.sub(r'^Lord', '', s)                          # LordSabertooth -> Sabertooth
    s = re.sub(r'(Mohawk|Gaming|PL|TheWizard|BringsAxe)$', '', s)  # trailing suffix only
    s = re.sub(r'\d+$', '', s)                           # trailing digits
    return re.sub(r'[^a-z]', '', s.lower())

# canonical bracket roster (normalized base -> display name)
ROSTER = {
    'alcaras':'Alcaras','amadeus':'Amadeus','anarkos':'Anarkos','aran':'Aran','auro':'Auro',
    'becked':'Becked','blajj':'Blaj','cliff':'Cliff','droner':'Droner','fiddlers':'Fiddler',
    'fluffybunny':'FluffyBunny','fondercargo':'FonderCargo','groudon':'Groudon','hazard':'Hazard',
    'icematrix':'IceMatrix','jams':'Jams','kiriyama':'Kiriyama','klass':'Klass','sabertooth':'Sabertooth',
    'marauder':'Marauder','michaelofminsk':'MichaelofMinsk','mojo':'Mojo','mongreleyes':'MongrelEyes',
    'moroten':'Moroten','ninjaa':'Ninjaa','nizar':'Nizar','rincewind':'Rincewind','seasand':'Seasand',
    'siontific':'Siontific','thepurplebullmoose':'ThePurpleBullMoose',
}
NONBRACKET = {'yagman':'Yagman','yagmam':'Yagman','cyclex':'Cycle4x','plantvogue':'PlantVogue',
              'antvogue':'PlantVogue'}

def canon(n):
    """Map a normalized name to a canonical bracket player (prefix/substring)."""
    if n in ROSTER:
        return n
    for c in ROSTER:
        if len(n) >= 4 and len(c) >= 4 and (n.startswith(c) or c.startswith(n)):
            return c
    for c in ROSTER:
        if (len(n) >= 5 and n in c) or (len(c) >= 5 and c in n):
            return c
    return n

def disp(n):
    return ROSTER.get(n) or NONBRACKET.get(n) or n.title()

groups = defaultdict(list)
unparsed = []
for vid, title in pool.items():
    if not valid(title):
        continue
    pr = extract_pair(title)
    if not pr:
        unparsed.append((vid, title)); continue
    a, b = canon(norm(pr[0])), canon(norm(pr[1]))
    if len(a) < 3 or len(b) < 3:
        unparsed.append((vid, title)); continue
    groups[frozenset([a, b])].append((vid, title))

RN = {1:'WB Round 1',2:'WB Round 2',3:'WB Quarterfinal',4:'WB Semifinal',5:'WB Final',6:'Grand Final',
      -1:'LB Round 1',-2:'LB Round 2',-3:'LB Round 3',-4:'LB Round 4',-5:'LB Round 5',-6:'LB Round 6',-7:'LB Round 7',-8:'LB Final'}
brpairs = defaultdict(list)
for m in br:
    brpairs[frozenset([canon(norm(m['p1'])), canon(norm(m['p2']))])].append(m)

print(f"valid tournament videos grouped: {sum(len(v) for v in groups.values())}")
print(f"matchups: {len(groups)}    unparsed: {len(unparsed)}\n")
print("=== GROUPS ===")
for key, vids in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    bm = brpairs.get(key, [])
    rounds = ', '.join(RN[m['round']] for m in sorted(bm, key=lambda x: x['identifier'])) if bm else '— no bracket match'
    names = ' / '.join(sorted(disp(x) for x in key))
    print(f"  {len(vids):2}  {names:32} [{rounds}]")
print("\n=== bracket matches with NO video group ===")
for key, ms in sorted(brpairs.items(), key=lambda kv: min(x['identifier'] for x in kv[1])):
    if key not in groups:
        for m in ms:
            print(f"   {RN[m['round']]:16} #{m['identifier']:2}: {m['p1']} vs {m['p2']}")
print("\n=== UNPARSED ===")
for vid, t in unparsed:
    print("   ", vid, t)
json.dump({'|'.join(sorted(k)): v for k, v in groups.items()}, open('/tmp/groups.json', 'w'), indent=1)
